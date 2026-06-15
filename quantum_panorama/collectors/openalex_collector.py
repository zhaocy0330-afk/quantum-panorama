from __future__ import annotations

from datetime import date

import requests


OPENALEX_URL = "https://api.openalex.org/works"


def inverted_index_to_text(index: dict | None) -> str:
    if not index:
        return ""
    pairs = []
    for word, positions in index.items():
        for position in positions:
            pairs.append((position, word))
    return " ".join(word for _, word in sorted(pairs))


def collect(query: str, limit: int = 20, start_date: date | None = None, end_date: date | None = None) -> list[dict]:
    """Search OpenAlex works and return normalized paper records."""
    filters = []
    if start_date:
        filters.append(f"from_publication_date:{start_date.isoformat()}")
    if end_date:
        filters.append(f"to_publication_date:{end_date.isoformat()}")
    params = {"search": query, "per-page": limit}
    if filters:
        params["filter"] = ",".join(filters)
    response = requests.get(OPENALEX_URL, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()
    records = []
    for item in data.get("results", []):
        authors = []
        institutions = []
        for authorship in item.get("authorships", []):
            author = authorship.get("author", {}).get("display_name")
            if author:
                authors.append(author)
            for inst in authorship.get("institutions", []):
                name = inst.get("display_name")
                if name:
                    institutions.append(name)
        records.append(
            {
                "title": item.get("display_name") or "",
                "authors": "; ".join(authors[:12]),
                "institutions": "; ".join(dict.fromkeys(institutions[:12])),
                "summary": inverted_index_to_text(item.get("abstract_inverted_index")),
                "published": item.get("publication_date") or str(item.get("publication_year") or ""),
                "year": item.get("publication_year"),
                "doi": item.get("doi") or "",
                "url": item.get("primary_location", {}).get("landing_page_url") or item.get("id") or "",
                "source": "OpenAlex",
                "source_name": "OpenAlex",
                "raw": {"openalex_id": item.get("id")},
            }
        )
    return records
