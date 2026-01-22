import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def load_sheet(sheet_name):
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["google_service_account"],
            scope
        )

        client = gspread.authorize(creds)

        sheet_id = st.secrets["general"]["GSHEET_KEY"]

        sh = client.open_by_key(sheet_id)

        ws = sh.worksheet(sheet_name)

        return pd.DataFrame(ws.get_all_records())

    except Exception as e:
        st.error(f"❌ Gagal load sheet '{sheet_name}'")
        st.error(str(e))
        st.stop()
