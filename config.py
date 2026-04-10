import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
PHONE = os.getenv("TG_PHONE")
DEST_CHANNEL = os.getenv("DEST_CHANNEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")