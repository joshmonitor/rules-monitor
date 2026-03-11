import requests
from lxml import html
import os
import re

URL = "https://rules.utah.gov/publications/index-of-changes/"
DB_FILE = "last_hash.txt"
TARGET_YEAR = "2027"  # Update this as the years progress

def get_current_hash():
    response = requests.get(URL)
    tree = html.fromstring(response.content)
    
    # 1. Find the parent <li> that contains the link to the Excel file
    # This is more stable than looking for text strings.
    xpath_query = f"//li[contains(., '{TARGET_YEAR}') and contains(., '.xlsx')]"
    nodes = tree.xpath(xpath_query)
    
    if not nodes:
        print(f"DEBUG: Could not find a list item for {TARGET_YEAR}")
        return None
        
    # 2. Get all text inside that line
    full_text = nodes[0].text_content()
    print(f"DEBUG: Found line text: {full_text}")
    
    # 3. Use Regex to find exactly 32 hex characters (the MD5)
    # This ignores spaces, semicolons, and parentheses automatically.
    match = re.search(r'([a-fA-F0-9]{32})', full_text)
    
    if match:
        found_hash = match.group(1)
        print(f"DEBUG: Successfully extracted hash: {found_hash}")
        return found_hash
        
    print("DEBUG: Found the line, but no 32-character MD5 hash was inside it.")
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

