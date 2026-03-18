import re
import sys
from lxml import html
from common import get_session, write_outputs

URL = "https://rules.utah.gov/publications/index-of-changes/"
DB_FILE = "last_hash.txt"
TARGET_YEAR = "2027"

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}


def get_current_data(session):
    try:
        response = session.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        tree = html.fromstring(response.content)

        xpath_query = f"//p[a[contains(@href, '{TARGET_YEAR}')]]"
        nodes = tree.xpath(xpath_query)

        if not nodes:
            print(f"DEBUG: Could not find the <p> block for '{TARGET_YEAR}'")
            return None, None

        links = nodes[0].xpath(".//a[contains(@href, '.xlsx')]/@href")
        file_url = links[0] if links else "https://rules.utah.gov/publications/index-of-changes/"

        full_text = nodes[0].text_content()
        match = re.search(r'([a-fA-F0-9]{32})', full_text)
        found_hash = match.group(1) if match else None

        if not found_hash:
            print("DEBUG: Could not extract MD5 hash from page.")
            return None, None

        return found_hash, file_url

    except Exception as e:
        print(f"ERROR: {e}")
        return None, None


def read_last_hash():
    try:
        with open(DB_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def main():
    session = get_session()
    current_hash, file_url = get_current_data(session)

    if not current_hash:
        print("ERROR: Could not find hash on the page.")
        sys.exit(1)

    old_hash = read_last_hash()

    if current_hash != old_hash:
        print(f"CHANGE_DETECTED: New hash {current_hash} (was {old_hash})")
        with open(DB_FILE, "w") as f:
            f.write(current_hash)
        write_outputs({"changed": "true", "file_url": file_url})
    else:
        print(f"No changes. Current hash: {current_hash}")
        write_outputs({"changed": "false"})

if __name__ == "__main__":
    main()
