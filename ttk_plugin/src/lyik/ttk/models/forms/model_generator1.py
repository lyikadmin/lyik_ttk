import fitz  # PyMuPDF
import json
import os
from pydantic import BaseModel
import keyword
import re


def make_valid_identifier(name):
    """Converts field name to a valid Python identifier"""
    name = re.sub(r"\W|^(?=\d)", "_", name.strip())
    if keyword.iskeyword(name):
        name += "_field"
    return name or "field"


def python_type_from_pdf_field(field_type):
    """Maps PDF widget type to Python type"""
    if field_type == fitz.PDF_WIDGET_TYPE_TEXT:
        return "str"
    elif field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
        return "bool"
    elif field_type == fitz.PDF_WIDGET_TYPE_RADIOBUTTON:
        return "str"
    else:
        return "str"


def get_python_value(field_type, field_value):
    """Converts field value to Python literal based on type"""
    if field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
        return "True" if field_value in ["Yes", "On", "1", True] else "False"
    elif field_value is None:
        return "None"
    else:
        return f'"{str(field_value)}"'


def generate_pydantic_model(fields, model_filename):
    class_name = os.path.splitext(os.path.basename(model_filename))[0].capitalize()

    lines = [
        "from pydantic import BaseModel",
        "import os\n",
        f"class {class_name}(BaseModel):",
    ]

    for field in fields:
        field_name_raw = field["field_name"]
        field_name = make_valid_identifier(field_name_raw)
        field_type = python_type_from_pdf_field(field["field_type"])
        default_value = get_python_value(field["field_type"], field["field_value"])
        lines.append(
            f"    {field_name}: {field_type} = {default_value}  # PDF field: {field_name_raw}"
        )

    # Add save_to_json method
    lines += [
        "\n    def save_to_json(self, filename: str):",
        '        """',
        "        Writes all key-value pairs (attributes) of this EditableForm instance",
        "        into a JSON file. This can be updated for returning a JSON string",
        "        representation of the form data.",
        "",
        "        Args:",
        "            filename (str): The name of the JSON file to create or overwrite.",
        "                            This can be a full path or a relative path.",
        '        """',
        "        try:",
        "            json_data = self.model_dump_json(indent=4)  # Pydantic v2",
        "            output_dir = os.path.dirname(filename)",
        "            if output_dir and not os.path.exists(output_dir):",
        "                os.makedirs(output_dir)",
        "            with open(filename, 'w', encoding='utf-8') as f:",
        "                f.write(json_data)",
        "            print(f\"Successfully saved form data to '{filename}'\")",
        "        except ImportError:",
        "            print('Pydantic is likely an older version. Trying .json() method...')",
        "            try:",
        "                json_data = self.json(indent=4)",
        "                output_dir = os.path.dirname(filename)",
        "                if output_dir and not os.path.exists(output_dir):",
        "                    os.makedirs(output_dir)",
        "                with open(filename, 'w', encoding='utf-8') as f:",
        "                    f.write(json_data)",
        "                print(f\"Successfully saved form data to '{filename}' using .json()\")",
        "            except Exception as e:",
        "                print(f\"Error saving form data to '{filename}': {e}\")",
        "        except Exception as e:",
        "            print(f\"An unexpected error occurred while saving to '{filename}': {e}\")",
    ]

    model_code = "\n".join(lines)
    with open(model_filename, "w", encoding="utf-8") as f:
        f.write(model_code)
    print(f"\n✅ Pydantic model written to: {model_filename}")


def extract_pdf_fields_to_json_v2(pdf_path, json_output_path):
    try:
        print(f"\n📄 Extracting fields from PDF: {pdf_path} → JSON: {json_output_path}")
        if not os.path.exists(pdf_path):
            print(f"❌ Error: PDF file not found at '{pdf_path}'")
            return

        doc = fitz.open(pdf_path)
        extracted_data = {}

        for page_num in range(doc.page_count):
            page = doc[page_num]
            widgets = page.widgets()
            if not widgets:
                print(f"ℹ️ No fields found on Page {page_num + 1}.")
                continue

            for widget in widgets:
                field_name = widget.field_name
                field_value = widget.field_value
                field_type = widget.field_type

                if field_name is None:
                    field_name = "__UNNAMED_FIELD__"

                if field_type in {
                    fitz.PDF_WIDGET_TYPE_TEXT,
                    fitz.PDF_WIDGET_TYPE_CHECKBOX,
                    fitz.PDF_WIDGET_TYPE_RADIOBUTTON,
                    1,
                }:
                    extracted_data[field_name] = {
                        "field_name": field_name,
                        "field_value": field_value,
                        "field_type": field_type,
                    }

        doc.close()

        data_list = list(extracted_data.values())
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=4, ensure_ascii=False)

        print(f"✅ Data successfully extracted to '{json_output_path}'")

        # Generate Pydantic model file with default values
        model_file = os.path.splitext(pdf_path)[0] + ".py"
        generate_pydantic_model(data_list, model_file)

    except Exception as e:
        print(f"❌ An error occurred during extraction: {e}")


# --- Example Usage ---
if __name__ == "__main__":
    input_pdf = "Switzerland6.pdf"
    output_json = f"extracted_pdf_data_empty_{input_pdf}.json"
    extract_pdf_fields_to_json_v2(input_pdf, output_json)
