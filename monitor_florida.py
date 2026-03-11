import re
import requests
from lxml import html
import os

URL = "https://flrules.org/BigDoc"
DB_FILE = "last_florida_issue.txt"

def get_latest_issue_id():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        tree = html.fromstring(response.content)
        
        # Grab every single IID link on the page
        links = tree.xpath("//a[contains(@href, 'IID=')]/@href")
        
        if not links:
            print("DEBUG: Could not find any Issue IDs on the BigDoc page.")
            return None, None
            
        highest_id = 0
        best_link = ""
        
        # Loop through all links to find the absolute highest ID number
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
            
        # We found the highest number! Format the URL and return it.
        clean_link = best_link.lstrip('/')
        full_url = f"https://flrules.org/BigDoc/{clean_link}"
        
        # Convert highest_id back to a string so it matches the text file
        return str(highest_id), full_url

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
