import re
import sys
import requests
from lxml import html
from urllib.parse import urljoin
from common import get_session, write_outputs

URL = "https://flrules.org/BigDoc"
DB_FILE = "last_florida_issue.txt"

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}


def get_latest_issue_id(session):
    try:
        response = session.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        tree = html.fromstring(response.content)
        links = tree.xpath("//a[contains(@href, 'IID=')]/@href")

        if not links:
            print("DEBUG: Could not find any Issue IDs on the BigDoc page.")
            return None, None

        highest_id = 0
        best_link = ""

        for link in links:
            match = re.search(r'IID=(\d+)', link)
            if match:
                current_num = int(match.group(1))
                if current_num > highest_id:
                    highest_id = current_num
                    best_link = link

        if highest_id == 0:
            print("DEBUG: Found links, but couldn't extract any valid numbers.")
            return None, None

        full_url = urljoin("https://flrules.org/", best_link)
        return str(highest_id), full_url

    except Exception as e:
        print(f"ERROR: {e}")
        return None, None


def read_last_id():
    try:
        with open(DB_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def main():
    session = get_session()
    current_id, file_url = get_latest_issue_id(session)

    if not current_id:
        print("ERROR: Could not find Florida Issue ID.")
        sys.exit(1)

    old_id = read_last_id()

    if current_id != old_id:
        print(f"FLORIDA_CHANGE_DETECTED: New Issue ID {current_id} (was {old_id})")
        with open(DB_FILE, "w") as f:
            f.write(current_id)
        write_outputs({"fl_changed": "true", "fl_url": file_url})
    else:
        print(f"No new Florida issue posted yet. Current ID: {current_id}")
        write_outputs({"fl_changed": "false"})

if __name__ == "__main__":
    main()
