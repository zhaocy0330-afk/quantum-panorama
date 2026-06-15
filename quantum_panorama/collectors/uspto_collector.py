from __future__ import annotations

from datetime import date


def collect(query: str, limit: int = 20, start_date: date | None = None, end_date: date | None = None) -> list[dict]:
    """Reserved USPTO Open Data Portal collector.

    The MVP returns structured mock records so the staging and ingestion workflow can
    be exercised before a real API key is configured.
    """
    return [
        {
            "title": f"{query} quantum patent landscape mock record",
            "summary": "USPTO 接口预留：后续接入 Open Data Portal 后返回专利摘要、申请人和法律状态。",
            "published": (end_date or date.today()).isoformat(),
            "url": "https://developer.uspto.gov/api-catalog",
            "patent_number": "US-MOCK-0001",
            "source": "USPTO",
            "source_name": "USPTO",
            "raw": {"mock": True, "query": query},
        }
    ][:limit]

