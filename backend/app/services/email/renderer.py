import html


def _render_paragraphs(content: str) -> str:
    paragraphs = [
        paragraph.strip()
        for paragraph in content.split("\n\n")
        if paragraph.strip()
    ]

    return "\n".join(
        f"<p>{html.escape(paragraph)}</p>"
        for paragraph in paragraphs
    )


def render_newsletter_email(
    *,
    preview_text: str | None,
    content: str,
    cta_text: str | None = None,
    cta_url: str | None = None,
) -> str:
    safe_preview = html.escape(
        preview_text or ""
    )

    body_html = _render_paragraphs(content)

    cta_html = ""

    if cta_text and cta_url:
        safe_cta_text = html.escape(cta_text)
        safe_cta_url = html.escape(
            cta_url,
            quote=True,
        )

        cta_html = f"""
        <div style="margin-top: 30px;">
            <a
                href="{safe_cta_url}"
                style="
                    display: inline-block;
                    padding: 12px 22px;
                    background-color: #111827;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                "
            >
                {safe_cta_text}
            </a>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <title>SmartMail AI Newsletter</title>
</head>

<body
    style="
        margin: 0;
        padding: 0;
        background-color: #f3f4f6;
        font-family: Arial, Helvetica, sans-serif;
    "
>
    <div
        style="
            max-width: 680px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
        "
    >
        <div
            style="
                padding: 40px;
                color: #1f2937;
                line-height: 1.7;
            "
        >
            <div
                style="
                    color: #6b7280;
                    font-size: 14px;
                    margin-bottom: 24px;
                "
            >
                {safe_preview}
            </div>

            {body_html}

            {cta_html}
        </div>

        <div
            style="
                padding: 24px 40px;
                background-color: #f9fafb;
                color: #6b7280;
                font-size: 12px;
            "
        >
            You're receiving this email from SmartMail AI.
        </div>
    </div>
</body>
</html>
""".strip()