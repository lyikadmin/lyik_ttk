import fitz  # PyMuPDF
from Switzerland6 import Switzerland6


def fill_pdf_form(
    pdf_template_path: str, output_pdf_path: str, model_data: Switzerland6
):
    """
    Fills a PDF form using data from a Pydantic model and saves the result.

    Args:
        pdf_template_path (str): Path to the input (template) PDF.
        output_pdf_path (str): Path to the output (filled) PDF.
        model_data (Switzerland5): An instance of the Pydantic model with sample data.
    """
    try:
        doc = fitz.open(pdf_template_path)
        data_dict = model_data.dict()

        for page in doc:
            widgets = page.widgets()
            if not widgets:
                continue

            for widget in widgets:
                field_name = widget.field_name
                if field_name and field_name in data_dict:
                    value = data_dict[field_name]
                    if widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                        widget.field_value = "Yes" if value else "Off"
                    else:
                        widget.field_value = str(value)
                    widget.update()

        doc.save(output_pdf_path)
        print(f"Filled PDF saved as: {output_pdf_path}")
    except Exception as e:
        print(f"Error while filling PDF: {e}")


if __name__ == "__main__":
    # Sample data to fill the form
    sample_data = Switzerland6()

    template_pdf = "Switzerland6_original.pdf"
    filled_pdf = f"{template_pdf}_filled.pdf"

    fill_pdf_form(template_pdf, filled_pdf, sample_data)
