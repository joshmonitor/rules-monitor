import re
import sys
import os
import requests
from lxml import html
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://flrules.org/BigDoc"
DB_FILE = "last_florida_issue.txt"
BASE_URL = "https://flrules.org"

def get_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session

def get_latest_issue_id():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(URL, headers=headers, timeout=30)
        response.raise_for_status()
        tree = html.fromstring(response.content)
        links = tree.xpath("//a[contains(@href, 'IID=')]/@href")

        if not links:
            print("DEBUG: Could not find any Issue IDs on the BigDoc page.")
            return None, None

        highest_id = 0
        best_link = ""

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

        full_url = urljoin(BASE_URL + "/", best_link)
        return str(highest_id), full_url

    except Exception as e:
        print(f"ERROR: {e}")
        return None, None

def scrape_section_iii(issue_id):
    """Fetch Section III entries for the given issue ID and return an HTML table string."""
    url = f"{BASE_URL}/BigDoc/View_Section.asp?Issue={issue_id}&Section=3"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        tree = html.fromstring(response.content)

        count_text = ""
        count_nodes = tree.xpath("//td[contains(text(), 'Total number of notices')]")
        if count_nodes:
            count_text = count_nodes[0].text_content().strip()

        rows = tree.xpath("//tr[.//a[contains(@href, 'notice_Files.asp')]]")

        if not rows:
            return f"<p>Section III (<a href=\"{url}\">view on flrules.org</a>): No entries found.</p>"

        table_rows_html = ""
        for row in rows:
            cells = row.xpath(".//td")
            if len(cells) < 4:
                continue

            view_link_node = cells[1].xpath(".//a[@href]")
            view_href = (BASE_URL + view_link_node[0].get("href")) if view_link_node else "#"

            type_text = cells[2].text_content().strip()
            rule_link_node = cells[2].xpath(".//a[@href]")
            if rule_link_node:
                rule_href = rule_link_node[0].get("href")
                rule_num = rule_link_node[0].text_content().strip()
                if not rule_href.startswith("http"):
                    rule_href = BASE_URL + rule_href
                notice_type = type_text.replace(rule_num, "").strip()
                rule_num_cell = f'<a href="{rule_href}">{rule_num}</a>'
            else:
                notice_type = type_text
                rule_num_cell = ""

            rule_title = cells[3].text_content().strip()

            table_rows_html += (
                f'<tr>'
                f'<td style="padding:6px 10px;"><a href="{view_href}">View Text</a></td>'
                f'<td style="padding:6px 10px;">{notice_type}</td>'
                f'<td style="padding:6px 10px;">{rule_num_cell}</td>'
                f'<td style="padding:6px 10px;">{rule_title}</td>'
                f'</tr>'
            )

        section_html = (
            f'<h3 style="font-family:sans-serif;">Section III &#8212; Notices of Changes, Corrections and Withdrawals</h3>'
            f'<p style="font-family:sans-serif;font-size:13px;">{count_text}</p>'
            f'<table border="1" cellspacing="0" cellpadding="0" style="border-collapse:collapse;font-family:sans-serif;font-size:13px;">'
            f'<thead style="background:#f0f0f0;">'
            f'<tr>'
            f'<th style="padding:6px 10px;">Notice</th>'
            f'<th style="padding:6px 10px;">Type</th>'
            f'<th style="padding:6px 10px;">Rule Number</th>'
            f'<th style="padding:6px 10px;">Rule Title</th>'
            f'</tr>'
            f'</thead>'
            f'<tbody>{table_rows_html}</tbody>'
            f'</table>'
            f'<p style="font-family:sans-serif;font-size:12px;"><a href="{url}">View Section III on flrules.org</a></p>'
        )
        return section_html

    except Exception as e:
        print(f"ERROR scraping Section III: {e}")
        return f"<p>Could not retrieve Section III. Error: {e}</p>"

def read_last_id():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return f.read().strip()
    return ""

def write_outputs(outputs: dict):
    env_file = os.getenv('GITHUB_OUTPUT')
    if env_file:
        with open(env_file, "a") as f:
            for key, value in outputs.items():
                if "\n" in value:
                    # Multiline values require the heredoc delimiter syntax
                    f.write(f"{key}<<GHADELIMITER\n{value}\nGHADELIMITER\n")
                else:
                    f.write(f"{key}={value}\n")

def main():
    current_id, file_url = get_latest_issue_id()

    if not current_id:
        print("ERROR: Could not find Florida Issue ID.")
        sys.exit(1)

    old_id = read_last_id()

    if current_id != old_id:
        print(f"FLORIDA_CHANGE_DETECTED: New Issue ID {current_id} (was {old_id})")
        with open(DB_FILE, "w") as f:
            f.write(current_id)

        section_iii_html = scrape_section_iii(current_id)
        write_outputs({
            "fl_changed": "true",
            "fl_url": file_url,
            "fl_section_iii": section_iii_html,
        })
    else:
        print(f"No new Florida issue posted yet. Current ID: {current_id}")
        write_outputs({"fl_changed": "false"})

if __name__ == "__main__":
    main()
