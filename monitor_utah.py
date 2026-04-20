import re
import sys
import os
import requests
from lxml import html
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://rules.utah.gov/publications/index-of-changes/"
DB_FILE = "last_hash.txt"
TARGET_YEAR = "2027"

def get_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session

def get_current_data():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    session = get_session()
    try:
        response = session.get(URL, headers=headers, timeout=30)
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
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return f.read().strip()
    return ""

def write_outputs(outputs: dict):
    env_file = os.getenv('GITHUB_OUTPUT')
    if env_file:
        with open(env_file, "a") as f:
            for key, value in outputs.items():
                f.write(f"{key}={value}\n")

def main():
    current_hash, file_url = get_current_data()

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
