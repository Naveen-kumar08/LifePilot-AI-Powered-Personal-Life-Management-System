import json

from groq import Groq

from config import GROQ_API_KEY


MODEL_NAME = "llama-3.1-8b-instant"


def extract_document_information(text):

    # -----------------------------------------------------
    # Check API Key
    # -----------------------------------------------------

    if not GROQ_API_KEY:

        return {
            "error": (
                "GROQ_API_KEY is not configured. "
                "Add it to your .env file."
            )
        }

    # -----------------------------------------------------
    # Check Text
    # -----------------------------------------------------

    if not text or not text.strip():

        return {
            "error": "No document text was found."
        }

    # -----------------------------------------------------
    # Prompt
    # -----------------------------------------------------

    prompt = f"""
Analyze the following document.

Return ONLY valid JSON.

Use exactly these fields:

{{
    "document_type": "",
    "person_name": "",
    "document_number": "",
    "issue_date": "",
    "expiry_date": "",
    "important_information": ""
}}

Rules:

1. Do not invent information.
2. If a field is unavailable, use an empty string.
3. Convert dates to YYYY-MM-DD whenever possible.
4. If there is no expiry date, return an empty string.
5. Return JSON only.
6. Do not use markdown.

DOCUMENT:

{text[:12000]}
"""

    # -----------------------------------------------------
    # AI Request
    # -----------------------------------------------------

    try:

        client = Groq(
            api_key=GROQ_API_KEY
        )

        response = (
            client.chat.completions.create(
                model=MODEL_NAME,

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a document information "
                            "extraction assistant. "
                            "Never invent facts."
                        )
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        # Remove markdown fences if AI adds them
        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(
            content
        )

    except json.JSONDecodeError:

        return {
            "error": (
                "AI returned invalid JSON. "
                "Please try again."
            )
        }

    except Exception as e:

        return {
            "error": f"AI error: {e}"
        }