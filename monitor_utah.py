import re
import requests
from lxml import html
import os

URL = "https://rules.utah.gov/publications/index-of-changes/"
DB_FILE = "last_hash.txt"
TARGET_YEAR = "2027"

def get_current_data():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        tree = html.fromstring(response.content)
        
        # 1. Target the paragraph containing our year
        xpath_query = f"//p[a[contains(@href, '{TARGET_YEAR}')]]"
        nodes = tree.xpath(xpath_query)
        
        if not nodes:
            print(f"DEBUG: Could not find the <p> block for '{TARGET_YEAR}'")
            return None, None
            
        # 2. Extract the actual URL using XPath
        # We look for the anchor tag inside the paragraph and grab its href attribute
        links = nodes[0].xpath(".//a[contains(@href, '.xlsx')]/@href")
        file_url = links[0] if links else "https://rules.utah.gov/publications/index-of-changes/"
        
        # 3. Extract the 32-character MD5 hash
        full_text = nodes[0].text_content()
        match = re.search(r'([a-fA-F0-9]{32})', full_text)
        found_hash = match.group(1) if match else None
        
        return found_hash, file_url

    except Exception as e:
        print(f"ERROR: {e}")
        return None, None

def main():
    current_hash, file_url = get_current_data()
    if not current_hash:
        print("Could not find hash on the page.")
        return

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            old_hash = f.read().strip()
    else:
        old_hash = ""

    # Connect directly to GitHub Actions output system
    env_file = os.getenv('GITHUB_OUTPUT')

    if current_hash != old_hash:
        print(f"CHANGE_DETECTED=true")
        print(f"Extracted URL: {file_url}")
        
        with open(DB_FILE, "w") as f:
            f.write(current_hash)
            
        # Push variables directly to the workflow steps
        if env_file:
            with open(env_file, "a") as f:
                f.write("changed=true\n")
                f.write(f"file_url={file_url}\n")
    else:
        print("No changes.")
        if env_file:
            with open(env_file, "a") as f:
                f.write("changed=false\n")

if __name__ == "__main__":
    main()
