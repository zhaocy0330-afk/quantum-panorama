from __future__ import annotations

import hashlib
import re
from difflib import SequenceMatcher

import pandas as pd

from quantum_panorama.database import read_table


TABLE_FIELD_MAP = {
    "papers": {"title": "title", "url": "link", "identifier": None},
    "patents": {"title": "title", "url": None, "identifier": "patent_number"},
    "financing_events": {"title": None, "url": "source", "identifier": None},
    "policies": {"title": "title", "url": "link", "identifier": None},
    "products": {"title": "product_name", "url": None, "identifier": None},
    "organizations": {"title": "name", "url": "website", "identifier": None},
    "industry_relationships": {"title": "description", "url": "source", "identifier": None},
}


def normalize_for_match(value: str | None) -> str:
    text = str(value or "").lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[\W_]+", "", text, flags=re.UNICODE)
    return text


def fingerprint_record(title: str = "", url: str = "", identifier: str = "") -> str:
    base = "|".join([normalize_for_match(title), normalize_for_match(url), normalize_for_match(identifier)])
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def title_similarity(left: str, right: str) -> float:
    left_norm = normalize_for_match(left)
    right_norm = normalize_for_match(right)
    if not left_norm or not right_norm:
        return 0.0
    return SequenceMatcher(None, left_norm, right_norm).ratio()


def duplicate_status(record: dict, target_table: str) -> tuple[str, str]:
    """Return duplicate flag and duplicate reason for staging review."""
    field_map = TABLE_FIELD_MAP.get(target_table, TABLE_FIELD_MAP["papers"])
    try:
        df = read_table(target_table)
    except Exception:
        return "否", ""
    if df.empty:
        return "否", ""

    title = str(record.get("title") or "")
    url = str(record.get("source_url") or record.get("url") or "")
    identifier = str(record.get("doi") or record.get("arxiv_id") or record.get("patent_number") or "")

    title_col = field_map.get("title")
    url_col = field_map.get("url")
    identifier_col = field_map.get("identifier")

    if title_col and title_col in df.columns and title:
        titles = df[title_col].fillna("").map(normalize_for_match)
        if normalize_for_match(title) in set(titles):
            return "是", "标题完全一致"

    if url_col and url_col in df.columns and url:
        urls = df[url_col].fillna("").map(str.strip)
        if url.strip() in set(urls):
            return "是", "URL完全一致"

    if identifier_col and identifier_col in df.columns and identifier:
        identifiers = df[identifier_col].fillna("").map(normalize_for_match)
        if normalize_for_match(identifier) in set(identifiers):
            return "是", "DOI/arXiv ID/专利号一致"

    if title_col and title_col in df.columns and title:
        for old_title in df[title_col].dropna().astype(str).tolist():
            if title_similarity(title, old_title) > 0.9:
                return "疑似", "标题相似度高于0.9"

    return "否", ""


def dedupe_dataframe(df: pd.DataFrame, target_col: str = "suggested_table") -> pd.DataFrame:
    result = df.copy()
    flags = []
    for _, row in result.iterrows():
        flag, reason = duplicate_status(row.to_dict(), str(row.get(target_col) or "papers"))
        flags.append(f"{flag}：{reason}" if reason else flag)
    result["duplicate_flag"] = flags
    return result

