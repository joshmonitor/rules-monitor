# State Rules Monitor
 
An automated GitHub Actions workflow that monitors state administrative rule publications and sends email alerts when new content is posted.
 
## What It Does
 
This repo watches three state regulatory sources daily and notifies you the moment something changes:
 
| Source | What's Monitored | Detection Method |
|--------|-----------------|-----------------|
| **Utah** | [Index of Changes](https://rules.utah.gov/publications/index-of-changes/) — the annual Excel file listing all rule changes | MD5 hash comparison |
| **Florida** | [Florida Administrative Register (BigDoc)](https://flrules.org/BigDoc) — daily issues of the FAR | Issue ID tracking |
| **New York** | [NY State Register](https://dos.ny.gov/state-register) — weekly issues of the NY State Register | Issue number tracking |
 
When a change is detected, the workflow commits the updated tracker file(s) to the repo and sends an email alert with a direct link to the new content.

## How It Works
 
The workflow runs automatically at **9:00 AM EST, Monday–Friday**, and can also be triggered manually via `workflow_dispatch`.
 
```
┌─────────────────────────────────────────────────────────┐
│  GitHub Actions (cron: weekdays 9 AM EST)               │
│                                                         │
│  1. Run monitor_utah.py   ──► compare MD5 hash          │
│  2. Run monitor_florida.py ──► compare issue ID         │
│  3. Run monitor_ny.py      ──► compare issue number     │
│                                                         │
│  If changed:                                            │
│    - Download latest file (Utah only)                   │
│    - Commit updated tracker to repo                     │
│    - Send email alert with direct link                  │
└─────────────────────────────────────────────────────────┘
```
 
### Utah Monitor (`monitor_utah.py`)
 
Fetches the Utah Index of Changes page, scrapes the MD5 hash published alongside the 2027 Excel file, and compares it to the hash stored in `last_hash.txt`. If they differ, a change is flagged, the new hash is saved, and the latest `.xlsx` file is downloaded.
 
### Florida Monitor (`monitor_florida.py`)
 
Fetches the Florida BigDoc directory page, finds all links containing `IID=` (Issue IDs), and takes the highest numeric ID as the latest issue. Compares it to the ID stored in `last_florida_issue.txt`. If a new (higher) ID is found, a change is flagged.

### New York Monitor (`monitor_ny.py`)

Fetches the New York State Register page at `https://dos.ny.gov/state-register`, parses the HTML with lxml, and scans for any link whose text contains "issue" followed by a number. The highest issue number found is taken as the latest weekly issue, and its href (prefixed with `https://dos.ny.gov` when relative) is captured as the direct link. The current number is compared to the value stored in `last_ny_issue.txt`; if it differs, a change is flagged, the file is updated, and an email alert is sent.
