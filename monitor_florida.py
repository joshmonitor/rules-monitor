import re
import requests
from lxml import html
import os

URL = "https://flrules.org/"
DB_FILE = "last_florida_issue.txt"

def get_latest_issue_id():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        tree = html.fromstring(response.content)
        
        # Look for any link containing 'IID=' (Issue ID) in the BigDoc directory
        links = tree.xpath("//a[contains(@href, 'IID=')]/@href")
        
        if not links:
            print("DEBUG: Could not find any Issue IDs on the BigDoc page.")
            return None, None
            
        latest_link = links[0]
        
        # Extract the ID number
        match = re.search(r'IID=(\d+)', latest_link)
        if match:
            issue_id = match.group(1)
            clean_link = latest_link.lstrip('/')
            full_url = f"https://flrules.org/BigDoc/{clean_link}"
            return issue_id, full_url
            
        return None, None

    except Exception as e:
        print(f"ERROR: {e}")
        return None, None

def main():
    current_id, file_url = get_latest_issue_id()
    if not current_id:
        print("Could not find Florida Issue ID.")
        return

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            old_id = f.read().strip()
    else:
        old_id = ""

    env_file = os.getenv('GITHUB_OUTPUT')

    if current_id != old_id:
        print(f"FLORIDA_CHANGE_DETECTED=true")
        print(f"New Issue ID: {current_id}")
        
        with open(DB_FILE, "w") as f:
            f.write(current_id)
            
        if env_file:
            with open(env_file, "a") as f:
                f.write("fl_changed=true\n")
                f.write(f"fl_url={file_url}\n")
    else:
        print("No new Florida issue posted yet.")
        if env_file:
            with open(env_file, "a") as f:
                f.write("fl_changed=false\n")

if __name__ == "__main__":
    main()
