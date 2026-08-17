import os

from dotenv import load_dotenv


# Load .env file
load_dotenv()


APP_NAME = "LifePilot"


GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
)