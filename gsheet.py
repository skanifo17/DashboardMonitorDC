import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from config import GSHEET_KEY

def load_sheet(sheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "service_account.json", scope
    )
    client = gspread.authorize(creds)
    ws = client.open_by_key(GSHEET_KEY).worksheet(sheet_name)
    return pd.DataFrame(ws.get_all_records())
