import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SHOP_URL = "https://www.etsy.com/shop/PeacemakerRanchCo"
SHEET_NAME = "Etsy Competitor Tracker"

def get_credentials():
    creds_json = os.environ["GOOGLE_CREDENTIALS"]
    creds_dict = json.loads(creds_json)

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return creds


def get_listings():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(SHOP_URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    listings = []
    seen = set()

    for a in soup.select("a[href*='/listing/']"):
        url = "https://www.etsy.com" + a["href"]

        if url in seen:
            continue

        seen.add(url)

        title = a.get_text(strip=True)

        listings.append({
            "title": title,
            "url": url
        })

    return listings


def connect_sheet(creds):
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet


def save_snapshot(sheet, listings):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item in listings:
        sheet.append_row([
            now,
            item["title"],
            item["url"]
        ])


def main():
    creds = get_credentials()
    sheet = connect_sheet(creds)
    listings = get_listings()
    save_snapshot(sheet, listings)


if __name__ == "__main__":
    main()
