import os
import requests
import re
from datetime import datetime, timedelta

USERNAME = "jatingarg36"
README_FILE = "README.md"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json",
}

if GITHUB_TOKEN:
    headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

# Fetch recent events
events_resp = requests.get(
    f"https://api.github.com/users/{USERNAME}/events",
    headers=headers
)
events_resp.raise_for_status()
events = events_resp.json()

commits = 0
prs_opened = 0
prs_merged = 0

for event in events:
    event_type = event.get("type")

    # ✅ Handle PushEvent using compare API
    if event_type == "PushEvent":
        repo_name = event["repo"]["name"]
        payload = event.get("payload", {})
        before = payload.get("before")
        head = payload.get("head")

        if before and head:
            compare_url = f"https://api.github.com/repos/{repo_name}/compare/{before}...{head}"
            compare_resp = requests.get(compare_url, headers=headers)

            if compare_resp.status_code == 200:
                compare_data = compare_resp.json()
                commits += compare_data.get("total_commits", 0)

    # ✅ Handle PR events
    elif event_type == "PullRequestEvent":
        action = event["payload"].get("action")

        if action == "opened":
            prs_opened += 1

        if action == "closed" and event["payload"]["pull_request"].get("merged"):
            prs_merged += 1

# Update README
with open(README_FILE, "r") as f:
    content = f.read()

new_metrics = f"""
- Commits (last 30 days): **{commits}**
- Pull Requests opened: **{prs_opened}**
- Pull Requests merged: **{prs_merged}**
"""

content = re.sub(
    r"<!-- METRICS_START -->(.*?)<!-- METRICS_END -->",
    f"<!-- METRICS_START -->\n{new_metrics}\n<!-- METRICS_END -->",
    content,
    flags=re.DOTALL
)

with open(README_FILE, "w") as f:
    f.write(content)