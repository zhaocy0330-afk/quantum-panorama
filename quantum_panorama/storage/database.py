from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_DB_PATH = DATA_DIR / "quantum_research.db"


def get_db_path() -> Path:
    value = os.getenv("QUANTUM_RESEARCH_DB_PATH")
    if value:
        return Path(value)
    try:
        import streamlit as st

        secret_value = st.secrets.get("QUANTUM_RESEARCH_DB_PATH")
        if secret_value:
            return Path(str(secret_value))
    except Exception:
        pass
    return DEFAULT_DB_PATH


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        create_schema(conn)


def create_schema(conn: sqlite3.Connection) -> None:
    statements = [
        """
        CREATE TABLE IF NOT EXISTS data_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            source_type TEXT,
            url TEXT,
            enabled INTEGER,
            category_hint TEXT,
            keywords TEXT,
            crawl_interval_hours INTEGER,
            created_at TEXT,
            updated_at TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS crawl_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,
            job_type TEXT,
            status TEXT,
            started_at TEXT,
            finished_at TEXT,
            items_found INTEGER,
            items_saved INTEGER,
            error_message TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS crawl_results_staging (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            source_name TEXT,
            source_type TEXT,
            published_at TEXT,
            fetched_at TEXT,
            raw_summary TEXT,
            content_excerpt TEXT,
            category TEXT,
            matched_keywords TEXT,
            importance INTEGER,
            status TEXT,
            title_hash TEXT,
            url_hash TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS research_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            source_name TEXT,
            source_type TEXT,
            published_at TEXT,
            fetched_at TEXT,
            summary TEXT,
            content_excerpt TEXT,
            category TEXT,
            matched_keywords TEXT,
            importance INTEGER,
            title_hash TEXT,
            url_hash TEXT,
            created_at TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ai_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_type TEXT,
            title TEXT,
            time_range TEXT,
            filters TEXT,
            content_markdown TEXT,
            model_name TEXT,
            created_at TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ai_item_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            research_item_id INTEGER,
            one_sentence_summary TEXT,
            key_entities TEXT,
            industry_segment TEXT,
            impact_analysis TEXT,
            risk_flags TEXT,
            confidence_level TEXT,
            created_at TEXT
        )
        """,
    ]
    for statement in statements:
        conn.execute(statement)
    conn.commit()


def read_sql(query: str, params: Iterable | None = None) -> pd.DataFrame:
    init_db()
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params or [])


def execute(query: str, params: Iterable | None = None) -> None:
    init_db()
    with get_connection() as conn:
        conn.execute(query, tuple(params or []))
        conn.commit()


def executemany(query: str, params: list[tuple]) -> None:
    init_db()
    with get_connection() as conn:
        conn.executemany(query, params)
        conn.commit()


def insert_row(table: str, payload: dict) -> int:
    init_db()
    keys = list(payload.keys())
    placeholders = ",".join(["?"] * len(keys))
    with get_connection() as conn:
        cursor = conn.execute(
            f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({placeholders})",
            [payload[key] for key in keys],
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_data_sources(enabled_only: bool = False) -> pd.DataFrame:
    if enabled_only:
        return read_sql("SELECT * FROM data_sources WHERE enabled=1 ORDER BY name")
    return read_sql("SELECT * FROM data_sources ORDER BY id DESC")


def add_data_source(
    name: str,
    source_type: str,
    url: str,
    keywords: str = "",
    category_hint: str = "",
    enabled: int = 1,
    crawl_interval_hours: int = 24,
) -> int:
    return insert_row(
        "data_sources",
        {
            "name": name,
            "source_type": source_type,
            "url": url,
            "enabled": int(enabled),
            "category_hint": category_hint,
            "keywords": keywords,
            "crawl_interval_hours": int(crawl_interval_hours),
            "created_at": now_iso(),
            "updated_at": now_iso(),
        },
    )


def add_default_sources(defaults: list[dict]) -> int:
    existing = set(get_data_sources()["url"].dropna().astype(str).tolist())
    added = 0
    for source in defaults:
        if source["url"] in existing:
            continue
        add_data_source(**source)
        added += 1
    return added


def set_data_source_enabled(source_id: int, enabled: int) -> None:
    execute("UPDATE data_sources SET enabled=?, updated_at=? WHERE id=?", (int(enabled), now_iso(), int(source_id)))


def delete_data_source(source_id: int) -> None:
    execute("DELETE FROM data_sources WHERE id=?", (int(source_id),))


def create_crawl_job(source_id: int | None, job_type: str) -> int:
    return insert_row(
        "crawl_jobs",
        {
            "source_id": source_id,
            "job_type": job_type,
            "status": "running",
            "started_at": now_iso(),
            "finished_at": "",
            "items_found": 0,
            "items_saved": 0,
            "error_message": "",
        },
    )


def finish_crawl_job(job_id: int, status: str, items_found: int, items_saved: int, error_message: str = "") -> None:
    execute(
        """
        UPDATE crawl_jobs
        SET status=?, finished_at=?, items_found=?, items_saved=?, error_message=?
        WHERE id=?
        """,
        (status, now_iso(), int(items_found), int(items_saved), error_message, int(job_id)),
    )


def list_crawl_jobs(limit: int = 100) -> pd.DataFrame:
    return read_sql("SELECT * FROM crawl_jobs ORDER BY id DESC LIMIT ?", (int(limit),))


def hashes_exist(title_hash: str, url_hash: str) -> bool:
    query = """
    SELECT 1 FROM research_items
    WHERE (url_hash<>'' AND url_hash=?) OR (title_hash<>'' AND title_hash=?)
    UNION
    SELECT 1 FROM crawl_results_staging
    WHERE status IN ('pending','approved')
      AND ((url_hash<>'' AND url_hash=?) OR (title_hash<>'' AND title_hash=?))
    LIMIT 1
    """
    df = read_sql(query, (url_hash, title_hash, url_hash, title_hash))
    return not df.empty


def insert_staging_records(records: list[dict]) -> int:
    saved = 0
    for record in records:
        if hashes_exist(record.get("title_hash", ""), record.get("url_hash", "")):
            continue
        payload = {
            "title": record.get("title", ""),
            "url": record.get("url", ""),
            "source_name": record.get("source_name", ""),
            "source_type": record.get("source_type", ""),
            "published_at": record.get("published_at", ""),
            "fetched_at": record.get("fetched_at", now_iso()),
            "raw_summary": record.get("raw_summary", ""),
            "content_excerpt": record.get("content_excerpt", ""),
            "category": record.get("category", "未分类"),
            "matched_keywords": record.get("matched_keywords", ""),
            "importance": int(record.get("importance") or 1),
            "status": record.get("status", "pending"),
            "title_hash": record.get("title_hash", ""),
            "url_hash": record.get("url_hash", ""),
        }
        insert_row("crawl_results_staging", payload)
        saved += 1
    return saved


def get_staging(status: str | None = None) -> pd.DataFrame:
    if status and status != "全部":
        return read_sql("SELECT * FROM crawl_results_staging WHERE status=? ORDER BY id DESC", (status,))
    return read_sql("SELECT * FROM crawl_results_staging ORDER BY id DESC")


def approve_staging_records(ids: list[int]) -> dict:
    if not ids:
        return {"approved": 0, "skipped": 0}
    staging = read_sql(
        f"SELECT * FROM crawl_results_staging WHERE id IN ({','.join(['?'] * len(ids))})",
        tuple(int(item) for item in ids),
    )
    approved = 0
    skipped = 0
    for _, row in staging.iterrows():
        if row["status"] == "approved":
            skipped += 1
            continue
        if hashes_exist(str(row["title_hash"]), str(row["url_hash"])):
            # The staging row itself can make hashes_exist true, so check research_items directly.
            existing = read_sql(
                """
                SELECT 1 FROM research_items
                WHERE (url_hash<>'' AND url_hash=?) OR (title_hash<>'' AND title_hash=?)
                LIMIT 1
                """,
                (row["url_hash"], row["title_hash"]),
            )
            if not existing.empty:
                skipped += 1
                continue
        insert_row(
            "research_items",
            {
                "title": row["title"],
                "url": row["url"],
                "source_name": row["source_name"],
                "source_type": row["source_type"],
                "published_at": row["published_at"],
                "fetched_at": row["fetched_at"],
                "summary": row["raw_summary"],
                "content_excerpt": row["content_excerpt"],
                "category": row["category"],
                "matched_keywords": row["matched_keywords"],
                "importance": int(row["importance"] or 1),
                "title_hash": row["title_hash"],
                "url_hash": row["url_hash"],
                "created_at": now_iso(),
            },
        )
        execute("UPDATE crawl_results_staging SET status='approved' WHERE id=?", (int(row["id"]),))
        approved += 1
    return {"approved": approved, "skipped": skipped}


def reject_staging_records(ids: list[int]) -> int:
    if not ids:
        return 0
    executemany("UPDATE crawl_results_staging SET status='rejected' WHERE id=?", [(int(item),) for item in ids])
    return len(ids)


def clear_rejected_staging() -> int:
    df = read_sql("SELECT COUNT(*) AS count FROM crawl_results_staging WHERE status='rejected'")
    count = int(df.iloc[0]["count"]) if not df.empty else 0
    execute("DELETE FROM crawl_results_staging WHERE status='rejected'")
    return count


def get_research_items(
    category: str | None = None,
    source: str | None = None,
    keyword: str | None = None,
    min_importance: int = 1,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    clauses = ["importance >= ?"]
    params: list = [int(min_importance)]
    if category and category != "全部":
        clauses.append("category=?")
        params.append(category)
    if source and source != "全部":
        clauses.append("source_name=?")
        params.append(source)
    if keyword:
        clauses.append("(title LIKE ? OR summary LIKE ? OR content_excerpt LIKE ? OR matched_keywords LIKE ?)")
        like = f"%{keyword}%"
        params.extend([like, like, like, like])
    if start_date:
        clauses.append("COALESCE(NULLIF(published_at,''), fetched_at) >= ?")
        params.append(start_date)
    if end_date:
        clauses.append("COALESCE(NULLIF(published_at,''), fetched_at) <= ?")
        params.append(end_date)
    where = " AND ".join(clauses)
    return read_sql(f"SELECT * FROM research_items WHERE {where} ORDER BY importance DESC, id DESC", params)


def get_research_item(item_id: int) -> pd.DataFrame:
    return read_sql("SELECT * FROM research_items WHERE id=?", (int(item_id),))


def save_ai_report(report_type: str, title: str, time_range: str, filters: str, content: str, model_name: str) -> int:
    return insert_row(
        "ai_reports",
        {
            "report_type": report_type,
            "title": title,
            "time_range": time_range,
            "filters": filters,
            "content_markdown": content,
            "model_name": model_name,
            "created_at": now_iso(),
        },
    )


def list_ai_reports() -> pd.DataFrame:
    return read_sql("SELECT * FROM ai_reports ORDER BY id DESC")


def save_item_summary(item_id: int, summary: dict) -> int:
    return insert_row(
        "ai_item_summaries",
        {
            "research_item_id": int(item_id),
            "one_sentence_summary": summary.get("one_sentence_summary", ""),
            "key_entities": summary.get("key_entities", ""),
            "industry_segment": summary.get("industry_segment", ""),
            "impact_analysis": summary.get("impact_analysis", ""),
            "risk_flags": summary.get("risk_flags", ""),
            "confidence_level": summary.get("confidence_level", ""),
            "created_at": now_iso(),
        },
    )


def get_item_summaries() -> pd.DataFrame:
    return read_sql("SELECT * FROM ai_item_summaries ORDER BY id DESC")


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="research_items")
    return buffer.getvalue()


def research_items_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "# 投研数据库导出\n\n暂无数据。\n"
    lines = ["# 投研数据库导出", ""]
    for _, row in df.iterrows():
        lines.extend(
            [
                f"## {row['title']}",
                f"- 分类：{row.get('category', '')}",
                f"- 来源：{row.get('source_name', '')}",
                f"- 重要性：{row.get('importance', '')}",
                f"- URL：{row.get('url', '')}",
                "",
                str(row.get("summary", "")),
                "",
            ]
        )
    return "\n".join(lines)

