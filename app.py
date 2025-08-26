import argparse
import csv
import json
import re
import sys
from typing import List, Dict
import requests
import feedparser

API_ENDPOINT = "https://jvndb.jvn.jp/myjvn"

def search_jvn(keyword: str, lang: str = "ja", limit: int = 30) -> List[Dict]:
    params = {
        "method": "getVulnOverviewList",
        "feed": "hnd",
        "keyword": keyword,
        "lang": lang,
        "rangeDatePublic": "n",
        "rangeDatePublished": "n",
        "rangeDateFirstPublished": "n",
        "max": str(max(limit, 50))
    }
    r = requests.get(API_ENDPOINT, params=params, timeout=30)
    r.raise_for_status()
    feed = feedparser.parse(r.text)
    results = []
    for entry in feed.entries[:limit]:
        title = entry.get("title", "")
        link = entry.get("link", "")
        published = (
            entry.get("published")
            or entry.get("updated")
            or entry.get("issued")
            or ""
        )
        m = re.search(r"(JVNDB-\d{4}-\d+)", f"{title} {link}")
        jvndb_id = m.group(1) if m else ""
        summary = entry.get("summary", "")
        results.append({
            "keyword": keyword,
            "jvndb_id": jvndb_id,
            "title": title,
            "url": link,
            "published": published,
            "summary": summary
        })
    return results

def main():
    parser = argparse.ArgumentParser(description="JVN iPedia キーワード検索 (MyJVN API)")
    parser.add_argument("--input", "-i", required=True, help="キーワードCSVファイル（1列のみ、複数行）")
    args = parser.parse_args()

    all_results = []
    try:
        with open(args.input, encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or not row[0].strip():
                    continue
                keyword = row[0].strip()
                items = search_jvn(keyword, lang="ja", limit=30)
                all_results.extend(items)
        with open("results.json", "w", encoding="utf-8") as out_f:
            json.dump(all_results, out_f, ensure_ascii=False, indent=2)
        print("検索結果を results.json に出力しました。")
    except Exception as e:
        print(f"[Error] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
