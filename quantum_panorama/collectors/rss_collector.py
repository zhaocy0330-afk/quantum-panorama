from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date

import feedparser
import requests


DEFAULT_RSS_FEEDS = [
    "https://quantumcomputingreport.com/feed/",
    "https://thequantuminsider.com/feed/",
]


def parse_date(value: str) -> str:
    if not value:
        return ""
    try:
        from email.utils import parsedate_to_datetime

        return parsedate_to_datetime(value).date().isoformat()
    except Exception:
        return value[:10]


def collect(
    query: str,
    limit: int = 20,
    start_date: date | None = None,
    end_date: date | None = None,
    feeds: list[str] | None = None,
) -> list[dict]:
    """Fetch RSS/Atom feeds and filter entries by query words."""
    query_terms = [term.lower() for term in query.replace("/", " ").split() if len(term) > 2]
    records = []
    for feed_url in feeds or DEFAULT_RSS_FEEDS:
        response = requests.get(feed_url, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        channel_items = root.findall(".//item")
        atom_entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        for item in channel_items:
            title = item.findtext("title", default="")
            summary = item.findtext("description", default="")
            link = item.findtext("link", default="")
            published = parse_date(item.findtext("pubDate", default=""))
            haystack = f"{title} {summary}".lower()
            if query_terms and not any(term in haystack for term in query_terms):
                continue
            if start_date and published and published < start_date.isoformat():
                continue
            if end_date and published and published > end_date.isoformat():
                continue
            records.append(
                {
                    "title": title,
                    "summary": summary,
                    "published": published,
                    "url": link,
                    "source": feed_url,
                    "source_name": "RSS/新闻源",
                    "raw": {"feed_url": feed_url},
                }
            )
            if len(records) >= limit:
                return records
        for entry in atom_entries:
            title = entry.findtext("{http://www.w3.org/2005/Atom}title", default="")
            summary = entry.findtext("{http://www.w3.org/2005/Atom}summary", default="")
            link_node = entry.find("{http://www.w3.org/2005/Atom}link")
            link = link_node.attrib.get("href", "") if link_node is not None else ""
            published = (entry.findtext("{http://www.w3.org/2005/Atom}published", default="") or "")[:10]
            haystack = f"{title} {summary}".lower()
            if query_terms and not any(term in haystack for term in query_terms):
                continue
            records.append(
                {
                    "title": title,
                    "summary": summary,
                    "published": published,
                    "url": link,
                    "source": feed_url,
                    "source_name": "RSS/新闻源",
                    "raw": {"feed_url": feed_url},
                }
            )
            if len(records) >= limit:
                return records
    return records


def collect_feed(feed_url: str, source_name: str = "", timeout: int = 15, limit: int = 30) -> tuple[list[dict], list[str]]:
    """Collect one RSS/Atom feed with requests timeout and feedparser parsing."""
    errors: list[str] = []
    records: list[dict] = []
    try:
        response = requests.get(
            feed_url,
            timeout=timeout,
            headers={"User-Agent": "QuantumPanoramaResearchBot/0.1 (+manual research workflow)"},
        )
        response.raise_for_status()
        parsed = feedparser.parse(response.content)
        if parsed.bozo:
            errors.append(f"{source_name or feed_url}: RSS解析警告：{parsed.bozo_exception}")
        for entry in parsed.entries[:limit]:
            records.append(
                {
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source_name": source_name or parsed.feed.get("title", feed_url),
                    "source_type": "rss",
                    "published_at": parse_date(entry.get("published", "") or entry.get("updated", "")),
                    "raw_summary": entry.get("summary", ""),
                    "content_excerpt": entry.get("summary", "")[:1000],
                }
            )
    except Exception as exc:
        errors.append(f"{source_name or feed_url}: {exc}")
    return records, errors
