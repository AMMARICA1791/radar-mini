"""Radar Mini v2: عناوين تهم المطورين (ذكاء اصطناعي، مفتوح المصدر، GitHub)."""
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEEDS = {
    "Show HN (مشاريع جديدة)": "https://hnrss.org/show?q=AI",
    "Hugging Face Blog": "https://huggingface.co/blog/feed.xml",
    "GitHub Changelog": "https://github.blog/changelog/feed/",
    "GitHub Blog": "https://github.blog/feed/",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/technology-lab",
}

KEYWORDS = [
    "ai", "llm", "agent", "agents", "open source", "open-source", "model",
    "copilot", "claude", "gpt", "gemini", "llama", "mcp", "rag",
    "python", "coding", "developer", "api", "security", "release",
]
PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in KEYWORDS) + r")\b", re.IGNORECASE
)

MAX_PER_FEED = 8
OUTPUT = "radar.md"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "radar-mini/0.2"})
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
    return bool(PATTERN.search(title))


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
