from __future__ import annotations

import hashlib
import re
from datetime import datetime
from difflib import SequenceMatcher
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import pandas as pd

from quantum_panorama.collectors import manual_collector, rss_collector, web_collector
from quantum_panorama.storage import database as db


CATEGORIES = {
    "量子计算": ["quantum computing", "量子计算", "qubit", "离子阱", "trapped ion", "superconducting", "neutral atom", "中性原子", "超导", "量子门", "量子纠错"],
    "量子通信": ["quantum communication", "qkd", "量子密钥", "量子通信", "quantum network", "quantum internet"],
    "量子传感": ["quantum sensing", "atomic clock", "magnetometer", "gravimeter", "量子传感", "原子钟", "磁力计", "重力仪", "精密测量"],
    "量子材料": ["quantum material", "量子材料", "topological", "拓扑", "superconductivity", "超导材料"],
    "政策监管": ["policy", "政策", "工信部", "发改委", "科技部", "government", "regulation", "规划", "指导意见"],
    "融资并购": ["financing", "funding", "融资", "并购", "investment", "venture", "round", "capital", "投资"],
    "论文进展": ["paper", "arxiv", "nature", "science", "prl", "physical review", "论文", "发表", "research"],
    "公司动态": ["company", "launch", "product", "partnership", "公司", "产品", "发布", "合作", "commercial", "customer"],
    "产业链": ["supply chain", "supplier", "component", "产业链", "供应链", "零部件", "客户"],
    "风险事件": ["delay", "failure", "lawsuit", "sanctions", "restriction", "风险", "失败", "延期", "制裁", "限制", "争议"],
}

IMPORTANT_TERMS = ["融资", "政策", "突破", "首个", "重大", "发布", "量子计算机", "commercial", "funding", "breakthrough", "launch", "partnership"]
AUTHORITY_TERMS = ["government", "ministry", "nature", "science", "ibm", "google", "microsoft", "ionq", "quantinuum", "工信部", "科技部", "发改委"]


def normalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url.strip())
    kept_params = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=False) if not k.lower().startswith("utm_")]
    query = urlencode(kept_params)
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", query, ""))


def stable_hash(value: str) -> str:
    normalized = re.sub(r"\s+", " ", str(value or "").strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest() if normalized else ""


def title_similar_to_existing(title: str, existing_titles: list[str]) -> bool:
    title_norm = str(title or "").strip().lower()
    if not title_norm:
        return False
    for existing in existing_titles:
        if SequenceMatcher(None, title_norm, str(existing or "").strip().lower()).ratio() > 0.9:
            return True
    return False


def classify_text(text: str, category_hint: str = "") -> str:
    if category_hint:
        return category_hint
    haystack = str(text or "").lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword.lower() in haystack for keyword in keywords):
            return category
    return "未分类"


def match_keywords(text: str, configured_keywords: str = "") -> list[str]:
    candidates: list[str] = []
    for value in configured_keywords.replace("，", ",").replace(";", ",").split(","):
        if value.strip():
            candidates.append(value.strip())
    for keywords in CATEGORIES.values():
        candidates.extend(keywords)
    haystack = str(text or "").lower()
    matched = [keyword for keyword in dict.fromkeys(candidates) if keyword.lower() in haystack]
    return matched


def score_importance(record: dict, matched: list[str]) -> int:
    text = " ".join(str(record.get(k, "")) for k in ["title", "raw_summary", "content_excerpt", "source_name"]).lower()
    score = 1
    if any(term.lower() in text for term in IMPORTANT_TERMS):
        score += 2
    if any(term.lower() in text for term in AUTHORITY_TERMS):
        score += 2
    if len(matched) >= 2:
        score += 1
    return max(1, min(score, 5))


def enrich_records(records: list[dict], keywords: str = "", category_hint: str = "") -> list[dict]:
    enriched = []
    for record in records:
        text = " ".join(str(record.get(k, "")) for k in ["title", "raw_summary", "content_excerpt"])
        matched = match_keywords(text, keywords)
        normalized_url = normalize_url(record.get("url", ""))
        title = record.get("title", "").strip() or normalized_url
        enriched.append(
            {
                **record,
                "title": title,
                "url": normalized_url,
                "fetched_at": record.get("fetched_at") or datetime.now().isoformat(timespec="seconds"),
                "category": classify_text(text, category_hint),
                "matched_keywords": ",".join(matched),
                "importance": score_importance(record, matched),
                "status": "pending",
                "title_hash": stable_hash(title),
                "url_hash": stable_hash(normalized_url),
            }
        )
    return enriched


def filter_records(records: list[dict], keywords: str = "") -> list[dict]:
    if not keywords.strip():
        return records
    filtered = []
    for record in records:
        text = " ".join(str(record.get(k, "")) for k in ["title", "raw_summary", "content_excerpt"]).lower()
        if match_keywords(text, keywords):
            filtered.append(record)
    return filtered


def stage_manual_urls(urls: list[str], keywords: str = "", limit: int = 20) -> dict:
    job_id = db.create_crawl_job(None, "manual")
    records, failures = manual_collector.collect_urls(urls, limit=limit)
    enriched = enrich_records(filter_records(records, keywords), keywords)
    saved = db.insert_staging_records(enriched)
    db.finish_crawl_job(job_id, "success" if not failures else "partial_failed", len(records), saved, "\n".join(f"{f['url']}: {f['error']}" for f in failures))
    return {"job_id": job_id, "records": enriched, "failures": failures, "saved": saved}


def collect_source(source: dict, limit: int = 20, override_keywords: str = "", timeout: int = 10) -> dict:
    job_id = db.create_crawl_job(int(source["id"]), "auto")
    errors: list[str] = []
    records: list[dict] = []
    keywords = override_keywords or str(source.get("keywords") or "")
    try:
        if source["source_type"] == "rss":
            records, errors = rss_collector.collect_feed(source["url"], source["name"], limit=limit, timeout=timeout)
        elif source["source_type"] == "web_list":
            records, errors = web_collector.collect_web_list(source["url"], source["name"], limit=limit, timeout=timeout)
        elif source["source_type"] == "single_url":
            records, failures = manual_collector.collect_urls([source["url"]], limit=1, timeout=timeout)
            errors = [f"{item['url']}: {item['error']}" for item in failures]
        else:
            errors = [f"Unsupported source_type: {source['source_type']}"]
    except Exception as exc:
        errors = [str(exc)]
    filtered = filter_records(records, keywords)
    enriched = enrich_records(filtered, keywords, str(source.get("category_hint") or ""))
    saved = db.insert_staging_records(enriched)
    status = "success" if not errors else ("partial_failed" if records else "failed")
    db.finish_crawl_job(job_id, status, len(records), saved, "\n".join(errors))
    return {"source": source, "job_id": job_id, "found": len(records), "saved": saved, "errors": errors, "records": enriched}


def collect_sources(source_ids: list[int], limit: int = 20, override_keywords: str = "", timeout: int = 10) -> dict:
    sources_df = db.get_data_sources(enabled_only=False)
    if source_ids:
        sources_df = sources_df[sources_df["id"].isin(source_ids)]
    else:
        sources_df = sources_df[sources_df["enabled"].eq(1)]
    results = []
    for _, source in sources_df.iterrows():
        results.append(collect_source(source.to_dict(), limit=limit, override_keywords=override_keywords, timeout=timeout))
    return {
        "results": results,
        "total_found": sum(item["found"] for item in results),
        "total_saved": sum(item["saved"] for item in results),
        "errors": [err for item in results for err in item["errors"]],
    }


def research_items_dataframe() -> pd.DataFrame:
    return db.get_research_items()
