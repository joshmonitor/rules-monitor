import requests
from lxml import html
import os

URL = "https://rules.utah.gov/publications/index-of-changes/"
DB_FILE = "last_hash.txt"
TARGET_YEAR = "2027"  # Update this as the years progress

def get_current_hash():
    response = requests.get(URL)
    tree = html.fromstring(response.content)
    
    # NEW STRATEGY: Find the link to the Excel file for the year first.
    # Then, look at the parent element (the <li>) for the MD5 string.
    xpath_query = f"//a[contains(@href, '{TARGET_YEAR}') and contains(@href, '.xlsx')]/.."
    nodes = tree.xpath(xpath_query)
    
    if not nodes:
        print(f"DEBUG: Could not find a link containing '{TARGET_YEAR}' and '.xlsx'")
        return None
        
    # Get all text inside that <li>, even if it's broken up by tags
    full_text = nodes[0].text_content()
    print(f"DEBUG: Found text: {full_text}") # This helps you see what it found in the logs
    
    if "MD5 Hash:" in full_text:
        # Split by "MD5 Hash:", take the right side, and clean up extra characters
        parts = full_text.split("MD5 Hash:")
        hash_part = parts[1].strip()
        # Extract just the first 32 characters (the length of an MD5 hash)
        return hash_part[:32]
        
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
