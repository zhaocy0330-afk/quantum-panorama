from __future__ import annotations

from datetime import datetime

import requests
from bs4 import BeautifulSoup


USER_AGENT = "QuantumPanoramaResearchBot/0.1 (+manual user supplied URLs)"


def split_urls(text: str) -> list[str]:
    urls = []
    for line in str(text or "").replace(",", "\n").splitlines():
        value = line.strip()
        if value:
            urls.append(value)
    return list(dict.fromkeys(urls))


def fetch_url(url: str, timeout: int = 15) -> dict:
    response = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else url
    description_node = soup.find("meta", attrs={"name": "description"})
    description = description_node.get("content", "").strip() if description_node else ""
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    body = " ".join(soup.get_text(" ", strip=True).split())
    return {
        "title": title,
        "url": response.url,
        "source_name": "手动采集",
        "source_type": "single_url",
        "published_at": "",
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "raw_summary": description or body[:300],
        "content_excerpt": body[:1000],
    }


def collect_urls(urls: list[str], limit: int = 20, timeout: int = 15) -> tuple[list[dict], list[dict]]:
    results: list[dict] = []
    failures: list[dict] = []
    for url in urls[:limit]:
        try:
            results.append(fetch_url(url, timeout=timeout))
        except Exception as exc:
            failures.append({"url": url, "error": str(exc)})
    return results, failures

