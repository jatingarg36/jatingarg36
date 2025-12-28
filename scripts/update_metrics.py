import requests
import re
from datetime import datetime, timedelta

USERNAME = "jatingarg36"
README_FILE = "README.md"

headers = {
    "Accept": "application/vnd.github+json"
}

since = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"

events = requests.get(
    f"https://api.github.com/users/{USERNAME}/events",
    headers=headers
).json()

commits = 0
prs_opened = 0
prs_merged = 0

for event in events:
    if event["type"] == "PushEvent":
        commits += len(event["payload"]["commits"])
    if event["type"] == "PullRequestEvent":
        action = event["payload"]["action"]
        if action == "opened":
            prs_opened += 1
        if action == "closed" and event["payload"]["pull_request"]["merged"]:
            prs_merged += 1

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