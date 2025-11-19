from typing import List, Type, Dict, Any, get_origin, get_args, Optional, Union, Tuple
from pydantic import BaseModel, create_model, Field
import os
import json
from pathlib import Path
from enum import Enum

from importlib.resources import files, as_file
import lyik.ttk.models.pydantic_v2 as py_template_pkg
from datamodel_code_generator import generate
from datamodel_code_generator import InputFileType, DataModelType

from lyik.ttk.models.forms.singaporevisaapplicationform import (
    Singaporevisaapplicationform,
)
from lyik.ttk.models.forms.schengentouristvisa import Schengentouristvisa


class PydanticIntersectionBuilder:
    """
    Builds a universal Pydantic model which contains only fields
    that are structurally common across all given Pydantic model classes.

    Key behaviors implemented:
    - Strict intersection: keep only fields present in ALL models.
    - Preserve field metadata (title, description, examples, json_schema_extra, constraints when available)
      from the first model's field definition.
    - Make every field Optional[...] with default=None (applies recursively).
    - Generate separate Root* classes when encountered (keeps the name if possible).
    """

    @classmethod
    def build_intersection_model(
        cls,
        models: List[Type[BaseModel]],
        model_name: str = "UniversalModel",
    ) -> Type[BaseModel]:
        if not models:
            raise ValueError("Model list is empty.")

        fields = cls._intersect_fields(models)
        return create_model(
            model_name,
            **fields,
        )

    # ------------------------- MAIN INTERSECTION -------------------------
    @classmethod
    def _intersect_fields(cls, models: List[Type[BaseModel]]) -> Dict[str, Any]:
        """
        Inspect top-level fields of the first model and keep only those fields
        that appear in ALL models and have structurally compatible types.
        Each returned field is Optional[...] with default Field(None, **metadata).
        """
        common_fields: Dict[str, Any] = {}
        first_model = models[0]

        for field_name, first_field_info in first_model.model_fields.items():
            # Must exist in all models
            if not all(field_name in m.model_fields for m in models[1:]):
                continue

            # Collect annotations for this field across all models
            annotations = [m.model_fields[field_name].annotation for m in models]

            merged_type = cls._merge_types(annotations, name_hint=field_name)
            if merged_type is None:
                continue

            # --- CHANGED: Preserve metadata from the first model's field and make Optional + default None ---
            metadata_kwargs: Dict[str, Any] = {}

            # Try to extract common metadata attributes from the Field info object
            # Field info shape may differ across pydantic versions; guard with getattr
            fi = first_field_info
            # Common attributes typically present: title, description, json_schema_extra, example
            for attr in ("title", "description", "example", "deprecated", "const"):
                val = getattr(fi, attr, None)
                if val is not None:
                    metadata_kwargs[attr] = val

            # json schema extras
            json_extra = getattr(fi, "json_schema_extra", None)
            if json_extra:
                metadata_kwargs["json_schema_extra"] = json_extra

            # constraints: try to copy common constraint names if present (min_length etc.)
            # Depending on generator/FieldInfo attribute names, some may be nested; do a best-effort.
            for constraint in (
                "min_length",
                "max_length",
                "regex",
                "gt",
                "ge",
                "lt",
                "le",
                "multiple_of",
            ):
                val = getattr(fi, constraint, None)
                if val is not None:
                    metadata_kwargs[constraint] = val

            # Ensure nested fields also become optional via merged_type being already constructed as concrete type
            optional_type = Optional[merged_type]

            # Use Field(None, **metadata_kwargs) as the default to preserve metadata
            common_fields[field_name] = (optional_type, Field(None, **metadata_kwargs))
            # --- END CHANGED ---

        return common_fields

    # ------------------------- TYPE MERGE / COMPATIBILITY -------------------------
    @classmethod
    def _merge_types(cls, types: List[Any], name_hint: str = "FieldType"):
        """
        Attempt to produce a merged/compatible type from a list of types.
        Returns:
            - a Python typing annotation (e.g., str, int, Enum subclass, BaseModel subclass, typing constructs)
            - or None if incompatible
        """
        # Normalize Optionals / Unions: try to reduce to a common core type
        normalized = [cls._strip_optional(t) for t in types]

        # If all enums -> merge enums (intersection of member NAMES)
        if cls._all_enum_types(normalized):
            return cls._merge_enums(normalized, name_hint=name_hint)

        # If all are pydantic models -> recursively intersect fields and create nested model.
        if cls._all_pydantic_models(normalized):
            nested_models = normalized  # they are classes
            nested_fields = cls._intersect_fields(nested_models)
            if not nested_fields:
                return None

            # If the nested class name contains "Root" use that name (from first nested model)
            nested_name_candidate = getattr(nested_models[0], "__name__", None)
            if nested_name_candidate and "Root" in nested_name_candidate:
                model_name = nested_name_candidate
            else:
                model_name = cls._unique_nested_model_name(name_hint)

            # create nested model; nested_fields are already Optional with Field(None,...)
            return create_model(
                model_name,
                **nested_fields,
            )

        # If all identical simple types (including same generics) -> return that
        if cls._all_same_primitives(normalized):
            return normalized[0]

        # Handle generics like List[T], Dict[K,V], Tuple[...] by merging args
        origins = [get_origin(t) for t in normalized]
        if len(set(origins)) == 1 and origins[0] is not None:
            origin = origins[0]
            args_lists = [get_args(t) for t in normalized]

            # Lists / sequences
            if origin in (list, List):
                # merge inner element types
                inner_types = [args[0] for args in args_lists]
                merged_inner = cls._merge_types(inner_types, name_hint=name_hint)
                if merged_inner is None:
                    return None
                return List[merged_inner]

            # Tuple
            if origin in (tuple, Tuple):
                inner_groups = list(zip(*args_lists))
                merged_args = []
                for group in inner_groups:
                    merged = cls._merge_types(list(group), name_hint=name_hint)
                    if merged is None:
                        return None
                    merged_args.append(merged)
                if len(merged_args) == 1:
                    return Tuple[merged_args[0], ...]
                return Tuple[tuple(merged_args)]

            # Dict[K, V]
            if origin in (dict, Dict):
                key_types = [args[0] for args in args_lists]
                val_types = [args[1] for args in args_lists]
                merged_key = cls._merge_types(key_types, name_hint=name_hint + "_key")
                merged_val = cls._merge_types(val_types, name_hint=name_hint + "_val")
                if merged_key is None or merged_val is None:
                    return None
                return Dict[merged_key, merged_val]

        # Not compatible
        return None

    # ------------------------- HELPERS -------------------------
    @staticmethod
    def _strip_optional(t: Any) -> Any:
        """If t is Optional[X] or Union[..., None], return X; otherwise return t."""
        origin = get_origin(t)
        if origin is Union:
            args = [a for a in get_args(t) if a is not type(None)]
            if len(args) == 1:
                return args[0]
        return t

    @staticmethod
    def _all_enum_types(types: List[Any]) -> bool:
        """True if every type is an Enum class (subclass of Enum)."""

        def is_enum(t):
            try:
                return isinstance(t, type) and issubclass(t, Enum)
            except Exception:
                return False

        return all(is_enum(t) for t in types)

    @staticmethod
    def _all_pydantic_models(types: List[Any]) -> bool:
        """True if every type is a Pydantic BaseModel subclass."""

        def is_model(t):
            try:
                return isinstance(t, type) and issubclass(t, BaseModel)
            except Exception:
                return False

        return all(is_model(t) for t in types)

    @staticmethod
    def _all_same_primitives(types: List[Any]) -> bool:
        """Return True if all types are strictly equal and not Enum/BaseModel/generic origins mismatch."""
        first = types[0]
        return all(t == first for t in types)

    _nested_model_counter = 0

    @classmethod
    def _unique_nested_model_name(cls, hint: str) -> str:
        cls._nested_model_counter += 1
        safe = "".join(c for c in hint.title() if c.isalnum())
        return f"{safe or 'Nested'}Model{cls._nested_model_counter}"

    # ------------------------- ENUM MERGING -------------------------
    @classmethod
    def _merge_enums(
        cls, enums: List[Type[Enum]], name_hint: str = "Enum"
    ) -> Optional[Type[Enum]]:
        """
        Create a merged Enum class whose members are the UNION of input enums'
        member NAMES, but KEEP THE ORIGINAL ENUM CLASS NAME
        (taken from the first model's enum type).
        """
        # Instead of INTERSECTION, take UNION and also preserve original name.
        member_name_union = set()
        for e in enums:
            try:
                member_name_union |= set(e.__members__.keys())
            except Exception:
                return None

        if not member_name_union:
            return None

        # Keep the original enum class name from the first model
        original_name = enums[0].__name__

        # Use deterministic ordering
        members = {name: name for name in sorted(member_name_union)}

        # Build new Enum class with original name
        MergedEnum = Enum(original_name, members)
        return MergedEnum

    # ------------------------- GENERATE FILE -------------------------
    @classmethod
    def save_model_to_file_using_codegen(
        cls,
        model_cls: Type[BaseModel],
        output_path: str,
        base_class: str = "pydantic.BaseModel",
    ):
        """
        Saves the dynamically generated model class to a .py file using datamodel-code-generator.
        Steps:
        1. Dump the model's JSON schema to a temporary .json file.
        2. Run datamodel-code-generator on that schema to produce the .py file.

        Notes:
        - datamodel-code-generator expects a Path for `output` when a file path is provided.
        - We pass the Path object directly (not a string) to avoid internal type errors.
        """
        output_path_obj = Path(output_path)
        output_dir = output_path_obj.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Dump JSON schema to temporary file
        temp_schema_path = output_dir / f"{output_path_obj.stem}_temp.json"
        with open(temp_schema_path, "w", encoding="utf-8") as f:
            json.dump(model_cls.model_json_schema(), f, indent=2)

        with as_file(files(py_template_pkg)) as path:
            templates_path = Path(os.fspath(path))

        generate(
            input_=temp_schema_path,
            input_file_type=InputFileType.JsonSchema,
            output=output_path_obj,
            base_class=base_class,
            output_model_type=DataModelType.PydanticV2BaseModel,
            allow_extra_fields=True,
            custom_template_dir=templates_path,
        )

        # Cleanup temp file
        try:
            os.remove(temp_schema_path)
        except OSError:
            pass

        print(f"Generated model file at: {output_path}")

    # ------------------------- small util for debug / quick preview -------------------------
    @classmethod
    def build_and_return_schema(
        cls, models: List[Type[BaseModel]], name: str = "UniversalModel"
    ) -> Dict[str, Any]:
        """
        Convenience method: build the universal model and return its json-schema (dict)
        without writing to disk. Useful for quick verification in tests.
        """
        Model = cls.build_intersection_model(models, model_name=name)
        return Model.model_json_schema()


def run():
    # Step 1: Build the intersection model
    UniversalModel = PydanticIntersectionBuilder.build_intersection_model(
        [Schengentouristvisa, Singaporevisaapplicationform]
    )

    # Step 2: Save the generated model to a Python file using datamodel-code-generator
    PydanticIntersectionBuilder.save_model_to_file_using_codegen(
        UniversalModel,
        output_path="ttk_plugin/src/lyik/ttk/models/generated/universal_model.py",
    )


if __name__ == "__main__":
    run()
