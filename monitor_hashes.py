import requests
from lxml import html
import os
import re

URL = "https://rules.utah.gov/publications/index-of-changes/"
DB_FILE = "last_hash.txt"
TARGET_YEAR = "2027"  # Update this as the years progress

def get_current_hash():
    # Use a real browser User-Agent to avoid being blocked
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(URL, headers=headers)
    tree = html.fromstring(response.content)
    
    # 1. Look for the list item (li) that contains both your year and 'XLSX'
    # This covers the exact line you pasted.
    xpath_query = f"//li[contains(., '{TARGET_YEAR}') and contains(., 'XLSX')]"
    nodes = tree.xpath(xpath_query)
    
    if not nodes:
        print(f"DEBUG: Could not find the line for {TARGET_YEAR}")
        return None
        
    # 2. Extract the text content of the entire line
    full_text = nodes[0].text_content()
    print(f"DEBUG: Scanned text: {full_text}")
    
    # 3. Use Regex to find exactly 32 hex characters
    # This looks for any sequence of 32 characters (0-9 or a-f)
    match = re.search(r'([a-fA-F0-9]{32})', full_text)
    
    if match:
        extracted_hash = match.group(1)
        print(f"DEBUG: Extracted MD5: {extracted_hash}")
        return extracted_hash
        
    print("DEBUG: Found the correct line, but no MD5 hash was detected inside it.")
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


