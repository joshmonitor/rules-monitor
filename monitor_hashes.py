import requests
from lxml import html
import os
import re

URL = "https://rules.utah.gov/publications/index-of-changes/"
DB_FILE = "last_hash.txt"
TARGET_YEAR = "2027"  # Update this as the years progress

def get_current_hash():
    # Headers to look like a real browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        tree = html.fromstring(response.content)
        
        # 1. Target the paragraph <p> that contains the link for the target year
        # We look for an <a> tag with the year in the href, then go to the parent <p>
        xpath_query = f"//p[a[contains(@href, '{TARGET_YEAR}')]]"
        nodes = tree.xpath(xpath_query)
        
        if not nodes:
            print(f"DEBUG: Could not find the <p> block containing '{TARGET_YEAR}'")
            return None
            
        # 2. Flatten all the <span> tags into one string
        # This turns the messy HTML into: "2027 Index of Changes (XLSX) -- ... (MD5 Hash: 4a152...);"
        full_text = nodes[0].text_content()
        print(f"DEBUG: Scanned text: {full_text}")
        
        # 3. Extract the 32-character MD5 hash
        match = re.search(r'([a-fA-F0-9]{32})', full_text)
        
        if match:
            found_hash = match.group(1)
            print(f"DEBUG: Successfully extracted MD5: {found_hash}")
            return found_hash
            
        print("DEBUG: Found the paragraph, but the MD5 hash was missing or formatted incorrectly.")
        return None

    except Exception as e:
        print(f"ERROR during request: {e}")
        return None

def main():
    current_hash = get_current_hash()
    if not current_hash:
        print("Could not find the hash on the page.")
        return

    # Read the old hash to compare
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            old_hash = f.read().strip()
    else:
        old_hash = ""

    if current_hash != old_hash:
        print(f"CHANGE_DETECTED=true")
        print(f"NEW_HASH={current_hash}")
        # Update the local file so we don't alert twice
        with open(DB_FILE, "w") as f:
            f.write(current_hash)
    else:
        print("CHANGE_DETECTED=false")

if __name__ == "__main__":

    main()



