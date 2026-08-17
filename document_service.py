from pathlib import Path

import fitz


def extract_text_from_pdf(path):

    path = Path(path)

    if not path.exists():

        return ""

    try:

        document = fitz.open(
            path
        )

        text = "\n".join(
            page.get_text()
            for page in document
        )

        document.close()

        return text.strip()

    except Exception:

        return ""