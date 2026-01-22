import requests
from config import WA_API_URL, WA_GROUP_ID, WA_API_KEY

def send_alert(message):
    params = {
        "phone": WA_GROUP_ID,
        "text": message,
        "apikey": WA_API_KEY
    }
    requests.get(WA_API_URL, params=params)
