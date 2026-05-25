import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

SHOP_URL = "https://www.etsy.com/shop/PeacemakerRanchCo"
SHEET_NAME = "Etsy Competitor Tracker"

def get_listings():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(SHOP_URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    listings = []

    for link in soup.select("a[href*='/listing/']"):
        title = link.get_text(strip=True)
        url = "https://www.etsy.com" + link["href"]

        if title and url not in [l["url"] for l in listings]:
            listings.append({
                "title": title,
                "url": url,
                "price": "unknown"
            })

    return listings


def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet


def save_snapshot(sheet, listings):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item in listings:
        sheet.append_row([
            now,
            item["title"],
            item["price"],
            item["url"]
        ])


def main():
    listings = get_listings()
    sheet = connect_sheet()
    save_snapshot(sheet, listings)


if __name__ == "__main__":
    main()
