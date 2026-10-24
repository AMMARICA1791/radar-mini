"""Radar Mini: يجلب عناوين الأخبار من مصادر RSS ويحفظ الجديد في ملف radar.md"""
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEEDS = {
    "Hacker News (AI)": "https://hnrss.org/newest?q=AI",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "The Verge": "https://www.theverge.com/rss/index.xml",
}

KEYWORDS = ["ai", "llm", "model", "openai", "anthropic", "gpt", "agent", "robot"]
MAX_PER_FEED = 10
OUTPUT = "radar.md"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "radar-mini/0.1"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if title and link:
            items.append((title, link))
    ns = "{http://www.w3.org/2005/Atom}"
    for entry in root.iter(ns + "entry"):
        title = (entry.findtext(ns + "title") or "").strip()
        link_el = entry.find(ns + "link")
        link = link_el.get("href", "").strip() if link_el is not None else ""
        if title and link:
            items.append((title, link))
    return items


def matches(title):
    if not KEYWORDS:
        return True
    low = title.lower()
    return any(k in low for k in KEYWORDS)


def main():
    seen = set()
    lines = [f"# Radar Mini — {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC", ""]
    for name, url in FEEDS.items():
        try:
            items = parse(fetch(url))
        except Exception as exc:
            lines.append(f"## {name}\n\nفشل الجلب: {exc}\n")
            continue
        lines.append(f"## {name}")
        count = 0
        for title, link in items:
            if link in seen or not matches(title):
                continue
            seen.add(link)
            lines.append(f"- [{title}]({link})")
            count += 1
            if count >= MAX_PER_FEED:
                break
        if count == 0:
            lines.append("- (لا نتائج مطابقة)")
        lines.append("")
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"تم. افتح {OUTPUT}")


if __name__ == "__main__":
    main()
