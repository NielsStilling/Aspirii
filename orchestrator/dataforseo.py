#!/usr/bin/env python3
"""
DataForSEO utility for the AI Blog Pipeline.
Used by the Analyst step to validate keywords and pull People Also Ask data.

Usage:
    python3 orchestrator/dataforseo.py keywords "Gemini AI 2026" "best AI models"
    python3 orchestrator/dataforseo.py related "Gemini AI"
    python3 orchestrator/dataforseo.py volume "keyword1" "keyword2" "keyword3"
"""

import sys
import os
import json
import base64
import requests

def get_credentials():
    login = os.environ.get("DATAFORSEO_LOGIN", "")
    password = os.environ.get("DATAFORSEO_PASSWORD", "")
    if not login or not password:
        # Try loading from .env
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DATAFORSEO_LOGIN="):
                        login = line.split("=", 1)[1]
                    elif line.startswith("DATAFORSEO_PASSWORD="):
                        password = line.split("=", 1)[1]
    if not login or not password:
        print("ERROR: DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD not set", file=sys.stderr)
        sys.exit(1)
    return base64.b64encode(f"{login}:{password}".encode()).decode()


def search_volume(keywords, location_code=2840, language_code="en"):
    """Get search volume for a list of keywords. Returns dict of keyword -> volume."""
    creds = get_credentials()
    resp = requests.post(
        "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live",
        headers={"Authorization": f"Basic {creds}", "Content-Type": "application/json"},
        json=[{"keywords": keywords, "language_code": language_code, "location_code": location_code}],
    )
    data = resp.json()
    results = {}
    if data.get("tasks"):
        for task in data["tasks"]:
            for r in task.get("result", []):
                results[r["keyword"]] = {
                    "volume": r.get("search_volume", 0),
                    "competition": r.get("competition", "N/A"),
                    "cpc": r.get("cpc"),
                    "trend": [
                        {"month": m["month"], "year": m["year"], "volume": m["search_volume"]}
                        for m in (r.get("monthly_searches") or [])[:6]
                    ],
                }
    return results


def related_keywords(seed_keywords, location_code=2840, language_code="en"):
    """Get related keyword suggestions with volume data."""
    creds = get_credentials()
    resp = requests.post(
        "https://api.dataforseo.com/v3/keywords_data/google_ads/keywords_for_keywords/live",
        headers={"Authorization": f"Basic {creds}", "Content-Type": "application/json"},
        json=[{"keywords": seed_keywords, "language_code": language_code, "location_code": location_code, "sort_by": "search_volume"}],
    )
    data = resp.json()
    results = []
    if data.get("tasks"):
        for task in data["tasks"]:
            for r in task.get("result", []):
                results.append({
                    "keyword": r["keyword"],
                    "volume": r.get("search_volume", 0),
                    "competition": r.get("competition", "N/A"),
                    "cpc": r.get("cpc"),
                })
    return sorted(results, key=lambda x: x["volume"], reverse=True)


def serp_paa(keyword, location_code=2840, language_code="en"):
    """Get People Also Ask questions from SERP results."""
    creds = get_credentials()
    resp = requests.post(
        "https://api.dataforseo.com/v3/serp/google/organic/live/regular",
        headers={"Authorization": f"Basic {creds}", "Content-Type": "application/json"},
        json=[{"keyword": keyword, "language_code": language_code, "location_code": location_code, "device": "desktop", "se_domain": "google.com"}],
    )
    data = resp.json()
    questions = []
    if data.get("tasks"):
        for task in data["tasks"]:
            for result in task.get("result", []):
                for item in result.get("items", []):
                    if item.get("type") == "people_also_ask":
                        for q in item.get("items", []):
                            questions.append(q.get("title", ""))
    return questions


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  dataforseo.py volume 'keyword1' 'keyword2'")
        print("  dataforseo.py related 'seed keyword'")
        print("  dataforseo.py paa 'keyword'")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "volume":
        results = search_volume(args)
        print(json.dumps(results, indent=2))

    elif command == "related":
        results = related_keywords(args)
        print(json.dumps(results[:20], indent=2))

    elif command == "paa":
        questions = serp_paa(args[0])
        if questions:
            for q in questions:
                print(f"  - {q}")
        else:
            print("No People Also Ask questions found for this keyword.")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
