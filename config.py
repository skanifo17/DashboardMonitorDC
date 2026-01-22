import streamlit as st

GSHEET_KEY = st.secrets["general"]["GSHEET_KEY"]

LEAD_TIME = 5
DOC_ALERT = 3
UTIL_ALERT = 90

WA_GROUP_ID = st.secrets["general"]["WA_GROUP_ID"]
WA_API_KEY = st.secrets["general"]["WA_API_KEY"]
WA_API_URL = "https://api.callmebot.com/whatsapp.php"
