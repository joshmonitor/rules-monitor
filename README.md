State Rules Monitor
An automated GitHub Actions workflow that monitors state administrative rule publications and sends email alerts when new content is posted.
What It Does
This repo watches two state regulatory sources daily and notifies you the moment something changes:
SourceWhat's MonitoredDetection MethodUtahIndex of Changes — the annual Excel file listing all rule changesMD5 hash comparisonFloridaFlorida Administrative Register (BigDoc) — daily issues of the FARIssue ID tracking
When a change is detected, the workflow commits the updated tracker file(s) to the repo and sends an email alert with a direct link to the new content.
Utah Monitor (monitor_utah.py)
Fetches the Utah Index of Changes page, scrapes the MD5 hash published alongside the 2027 Excel file, and compares it to the hash stored in last_hash.txt. If they differ, a change is flagged, the new hash is saved, and the latest .xlsx file is downloaded.
Florida Monitor (monitor_florida.py)
Fetches the Florida BigDoc directory page, finds all links containing IID= (Issue IDs), and takes the highest numeric ID as the latest issue. Compares it to the ID stored in last_florida_issue.txt. If a new (higher) ID is found, a change is flagged.
