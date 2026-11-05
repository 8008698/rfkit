#!/usr/bin/env python3
"""Cleanup old GitHub releases if the video date is not today's Nepal date."""
import os, sys, json, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

def main():
    # 1. Determine today's date in Nepal timezone
    now_nepal = datetime.now(ZoneInfo("Asia/Kathmandu")).date()
    print(f"आजको नेपाल मिति (Today in Nepal): {now_nepal}")

    # 2. Get repository and token from environment
    repo = os.environ.get("GITHUB_REPOSITORY", "8008698/rfkit")
    token = os.environ.get("GITHUB_TOKEN", "")

    if not token:
        print("सूचना: GITHUB_TOKEN उपलब्ध नभएकाले पुराना भिडियो हटाउने चरण छाडियो।")
        return

    # 3. List releases from GitHub API
    url = f"https://api.github.com/repos/{repo}/releases?per_page=100"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "NepDate-Rashifal-Kit"
    })

    try:
        with urllib.request.urlopen(req) as resp:
            releases = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Releases सूची तान्न सकिएन: {e}")
        return

    print(f"कुल भेटिएका Releases: {len(releases)}")

    # 4. Check each release against today's Nepal date
    for rel in releases:
        rel_id = rel.get("id")
        tag = rel.get("tag_name")
        created_at_str = rel.get("created_at") or rel.get("published_at")

        if not created_at_str:
            continue

        try:
            dt_utc = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            rel_date_nepal = dt_utc.astimezone(ZoneInfo("Asia/Kathmandu")).date()
        except Exception as e:
            print(f"मिति पार्स गर्न सकिएन ({tag}): {e}")
            continue

        print(f"- Release: {tag} | मिति (नेपाल): {rel_date_nepal}")

        # If date is not today's Nepal date, delete the release & tag
        if rel_date_nepal != now_nepal:
            print(f"  -> पुरानो मितिको भिडियो भेटियो ({rel_date_nepal} != {now_nepal})। हटाउँदै: {tag} (ID: {rel_id})")
            del_url = f"https://api.github.com/repos/{repo}/releases/{rel_id}"
            del_req = urllib.request.Request(del_url, method="DELETE", headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "NepDate-Rashifal-Kit"
            })
            try:
                with urllib.request.urlopen(del_req) as del_resp:
                    print(f"     सफल: Release {tag} मेटाइयो।")
            except Exception as e:
                print(f"     त्रुटि (Release delete): {e}")

            # Also delete Git Tag
            tag_url = f"https://api.github.com/repos/{repo}/git/refs/tags/{tag}"
            tag_req = urllib.request.Request(tag_url, method="DELETE", headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "NepDate-Rashifal-Kit"
            })
            try:
                with urllib.request.urlopen(tag_req) as tag_resp:
                    print(f"     सफल: Git Tag {tag} मेटाइयो।")
            except Exception:
                pass
        else:
            print(f"  -> आजकै मितिको भिडियो भएकाले सुरक्षित राखियो: {tag}")

if __name__ == "__main__":
    main()
