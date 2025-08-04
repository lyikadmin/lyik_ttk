def get_docket_operation_html_message(
    title_text: str,
    instruction_points: list[str] | None = None,
    url: str | None = None,
    action_text: str | None = None,
) -> str:
    action_text = "Download Docket" if url and not action_text else action_text

    full_css = """
    <style>
        .operation-container {
            text-align: center;
            font-family: Arial, sans-serif;
            padding: 24px;
        }

        .submit-button {
            background-color: #3BB9EB;
            color: white;
            border: none;
            padding: 8px 50px;
            font-size: 17px;
            border-radius: 9999px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
            width: fit-content;
            margin-top: 16px;
            display: inline-block;
            text-decoration: none;
            font-weight: 600;
        }

        .submit-button:hover {
            background-color: #1280aa;
            transform: scale(1.02);
        }

        .operation-title {
            font-size: 22px;
            color: #333333;
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 24px;
        }

        .instruction-list {
            list-style-type: disc;
            padding-left: 20px;
            display: inline-block;
            text-align: left;
            font-size: 16px;
            color: #222222;
            font-weight: 500;
            line-height: 1.8;
            margin: 0 auto;
        }

        .instruction-list li {
            margin-bottom: 12px;
        }
    </style>
    """

    url_button = (
        f"""<a href="{url}" class="submit-button">{action_text}</a>""" if url else ""
    )

    instruction_html = ""
    if instruction_points:
        instruction_items = "".join(f"<li>{point}</li>" for point in instruction_points)
        instruction_html = f"<ul class='instruction-list'>{instruction_items}</ul>"

    html = f"""
    {full_css}
    <div class="operation-container">
        {url_button}
        <p class="operation-title">{title_text}</p>
        {instruction_html}
    </div>
    """

    return html
