from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date
from urllib.parse import urlencode

import requests


ARXIV_API_URL = "https://export.arxiv.org/api/query"


def collect(query: str, limit: int = 20, start_date: date | None = None, end_date: date | None = None) -> list[dict]:
    """Search arXiv and return normalized paper records."""
    params = {
        "search_query": f'all:"{query}"',
        "start": 0,
        "max_results": limit,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API_URL}?{urlencode(params)}"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    records = []
    for entry in root.findall("atom:entry", ns):
        title = " ".join(entry.findtext("atom:title", default="", namespaces=ns).split())
        summary = " ".join(entry.findtext("atom:summary", default="", namespaces=ns).split())
        published = entry.findtext("atom:published", default="", namespaces=ns)
        updated = entry.findtext("atom:updated", default="", namespaces=ns)
        if start_date and published[:10] and published[:10] < start_date.isoformat():
            continue
        if end_date and published[:10] and published[:10] > end_date.isoformat():
            continue
        authors = [author.findtext("atom:name", default="", namespaces=ns) for author in entry.findall("atom:author", ns)]
        categories = [cat.attrib.get("term", "") for cat in entry.findall("atom:category", ns)]
        url_value = entry.findtext("atom:id", default="", namespaces=ns)
        records.append(
            {
                "title": title,
                "authors": "; ".join([a for a in authors if a]),
                "summary": summary,
                "published": published[:10],
                "updated": updated[:10],
                "url": url_value,
                "categories": "; ".join([c for c in categories if c]),
                "source": "arXiv",
                "source_name": "arXiv",
                "raw": {"query_url": url},
            }
        )
    return records
