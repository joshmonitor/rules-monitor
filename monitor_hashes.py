import requests
from lxml import html
import os

URL = "https://rules.utah.gov/publications/index-of-changes/"
DB_FILE = "last_hash.txt"
TARGET_YEAR = "2027"  # Update this as the years progress

def get_current_hash():
    response = requests.get(URL)
    tree = html.fromstring(response.content)
    
    # XPath to find the <li> containing our target year and extract the text
    # The structure is typically: <li>2027 Index of Changes... (MD5 Hash: [hash]);</li>
    xpath_query = f"//li[contains(text(), '{TARGET_YEAR} Index of Changes')]/text()"
    content_list = tree.xpath(xpath_query)
    
    if not content_list:
        return None
        
    full_text = "".join(content_list)
    if "MD5 Hash:" in full_text:
        # Extract the 32-character hex string
        return full_text.split("MD5 Hash:")[1].strip().split()[0].rstrip(');.')
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