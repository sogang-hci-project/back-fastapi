import os
import openai

from dotenv import load_dotenv

load_dotenv()


def register_openai_variable():
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_ORGANIZATION_KEY = os.environ.get("OPENAI_ORGANIZATION_KEY")

    openai.organization = OPENAI_ORGANIZATION_KEY
    openai.api_key = OPENAI_API_KEY
