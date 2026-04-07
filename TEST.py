import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds_dict = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
}

creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

client = gspread.authorize(creds)

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

spreadsheet = client.open_by_key(SPREADSHEET_ID)

worksheets = spreadsheet.worksheets()

for ws in worksheets:
    print(ws.title)