import fitz  # PyMuPDF
import json
import os
from PIL import Image, ImageDraw  # Import Pillow for dummy image generation


def load_data_from_json(json_path):
    """
    Loads data from a JSON file.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ Data successfully loaded from '{json_path}'")
        return data
    except FileNotFoundError:
        print(f"❌ Error: JSON file '{json_path}' not found.")
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON file '{json_path}': {e}")
    except Exception as e:
        print(f"❌ Unexpected error while loading JSON: {e}")
    return []


def get_field_value(data_dict: dict, field_key: str):
    """
    Retrieves a field's value from a flat dictionary where keys are field names.
    Returns None if the key is not found.
    """
    return data_dict.get(field_key, None)


def populate_and_flatten_pdf(
    pdf_path, data_from_json, output_pdf_path, global_signature_image_path=None
):
    """
    Populates PDF form fields using JSON data, inserts signature images,
    and flattens the form.
    """
    try:
        doc = fitz.open(pdf_path)

        for page_num in range(doc.page_count):
            page = doc[page_num]
            # It's crucial to get a fresh list of widgets for each page
            # if we are modifying (deleting) widgets within the loop.
            # However, for deletion, it's safer to mark for deletion and do it afterwards or
            # iterate in reverse order. For simplicity and PyMuPDF's behavior,
            # we will delete immediately here as it affects only the current widget.
            widgets = page.widgets()

            print(f"\n📄 Processing page {page_num + 1}...")

            # Iterate over a copy of widgets if you delete, to avoid modifying list during iteration
            # But in this case, we are deleting the current widget, so it's fine.
            for widget in widgets:
                field_name = widget.field_name
                field_type = widget.field_type

                # Handle Text and Checkbox fields
                if field_type in (
                    fitz.PDF_WIDGET_TYPE_TEXT,
                    fitz.PDF_WIDGET_TYPE_CHECKBOX,
                    fitz.PDF_WIDGET_TYPE_RADIOBUTTON,
                    fitz.PDF_WIDGET_TYPE_LISTBOX,
                    fitz.PDF_WIDGET_TYPE_COMBOBOX,
                ):
                    field_data = get_field_value(data_from_json, field_name)

                    if field_data:
                        widget.field_value = field_data
                        widget.update()
                        print(f"📝 Set '{field_name}' to '{widget.field_value}'")

                # Handle Signature fields
                elif field_type == 1:
                    print(
                        f"🔑 Found signature field: '{field_name}' on page {page_num + 1} at: {widget.rect}"
                    )

                    image_to_insert = None
                    field_data = field_data = get_field_value(
                        data_from_json, field_name
                    )
                    if field_data and "signature_image_path" in field_data:
                        image_to_insert = field_data["signature_image_path"]
                    elif global_signature_image_path:
                        image_to_insert = global_signature_image_path

                    if image_to_insert and os.path.exists(image_to_insert):
                        try:
                            # Insert the image directly onto the page at the widget's rectangle
                            page.insert_image(widget.rect, filename=image_to_insert)
                            print(
                                f"🖊️ Inserted signature image '{image_to_insert}' into '{field_name}' rect."
                            )

                            # CRITICAL FIX: Delete the widget IMMEDIATELY after inserting the image
                            # This removes the interactive field that might be covering the image.
                            page.delete_widget(widget)
                            print(
                                f"🗑️ Removed signature widget '{field_name}' after image insertion."
                            )

                        except Exception as e:
                            print(
                                f"❌ Failed to insert signature image or remove widget for '{field_name}': {e}"
                            )
                    else:
                        print(
                            f"⚠️ No valid signature image found or path incorrect for '{field_name}'. Skipping."
                        )

        # doc.bake() flattens ALL remaining interactive fields.
        # If you only wanted to flatten signature fields, you'd skip doc.bake()
        # and rely solely on the delete_widget.
        # Since the function implies flattening, we keep it for other fields.
        doc.bake()

        doc.save(output_pdf_path, deflate=True, garbage=4)
        print(f"\n✅ PDF populated and saved as '{output_pdf_path}'")
    except Exception as e:
        print(f"❌ Error populating PDF: {e}")
    finally:
        if "doc" in locals():
            doc.close()


# === Main Execution ===
if __name__ == "__main__":
    input_pdf = "Switzerland5.pdf"
    json_data_path = "form_data.json"  # Ensure this JSON exists and has data
    signature_image_path_for_all_signatures = (
        "signature.png"  # Path to your signature image
    )
    # Ensure signature image exists for testing
    if not os.path.exists(signature_image_path_for_all_signatures):
        print(
            f"❗ Warning: Signature image '{signature_image_path_for_all_signatures}' not found."
        )
        print("Attempting to create a dummy 'signature.png'.")
        try:
            img = Image.new("RGB", (200, 100), color="white")  # Larger dummy image
            d = ImageDraw.Draw(img)
            d.text(
                (50, 30), "Signed Here", fill=(0, 0, 0)
            )  # Better text for visibility
            img.save(signature_image_path_for_all_signatures)
            print(
                f"Generated a dummy '{signature_image_path_for_all_signatures}' for testing."
            )
        except ImportError:
            print(
                "Pillow not installed. Cannot generate dummy signature. Please install it (pip install Pillow) or provide a real signature.png."
            )
            exit()

    filled_pdf_output = f"filled_flattened_from_{os.path.basename(json_data_path)}.pdf"

    if not os.path.exists(input_pdf):
        print(f"❌ Input PDF not found: {input_pdf}")
    elif not os.path.exists(json_data_path):
        print(f"❌ JSON data file not found: {json_data_path}")
    else:
        # Example form_data structure if you were providing specific image paths in JSON:
        # form_data = [
        #     {"field_name": "NameField", "field_value": "John Doe", "field_type": "Text"},
        #     {"field_name": "NewSignatureField", "field_type": "Signature", "signature_image_path": "path/to/john_doe_signature.png"}
        # ]
        # For now, we'll rely on the global_signature_image_path for all signatures.

        form_data = load_data_from_json(json_data_path)
        if form_data:
            populate_and_flatten_pdf(
                input_pdf,
                form_data,
                filled_pdf_output,
                global_signature_image_path=signature_image_path_for_all_signatures,
            )
