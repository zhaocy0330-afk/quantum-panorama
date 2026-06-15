from __future__ import annotations

from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup


USER_AGENT = "QuantumPanoramaResearchBot/0.1 (+low frequency research collection)"


def normalize_link(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def same_domain(left: str, right: str) -> bool:
    return urlparse(left).netloc == urlparse(right).netloc


def fetch_page_summary(url: str, source_name: str, source_type: str = "web_list", timeout: int = 15) -> dict:
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
        "source_name": source_name,
        "source_type": source_type,
        "published_at": "",
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "raw_summary": description or body[:300],
        "content_excerpt": body[:1000],
    }


def collect_web_list(
    list_url: str,
    source_name: str = "",
    limit: int = 20,
    timeout: int = 15,
    same_domain_only: bool = True,
) -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    try:
        response = requests.get(list_url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
    except Exception as exc:
        return [], [f"{source_name or list_url}: {exc}"]

    soup = BeautifulSoup(response.text, "html.parser")
    links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(response.url, anchor["href"])
        if not href.startswith(("http://", "https://")):
            continue
        if same_domain_only and not same_domain(response.url, href):
            continue
        normalized = normalize_link(href)
        if normalized not in links:
            links.append(normalized)
        if len(links) >= limit:
            break

    records: list[dict] = []
    for link in links:
        try:
            records.append(fetch_page_summary(link, source_name or list_url, "web_list", timeout=timeout))
        except Exception as exc:
            errors.append(f"{link}: {exc}")
    return records, errors

