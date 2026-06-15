from __future__ import annotations

import json
from datetime import date, datetime, timedelta

import pandas as pd

from quantum_panorama.collectors import arxiv_collector, openalex_collector, rss_collector, uspto_collector
from quantum_panorama.database import get_connection, insert_row, read_table, update_row
from quantum_panorama.utils.classifier import classify_record
from quantum_panorama.utils.deduplication import duplicate_status


SOURCE_ALIASES = {
    "arXiv": "arXiv",
    "OpenAlex": "OpenAlex",
    "USPTO": "USPTO",
    "RSS/新闻源": "RSS/新闻源",
}


def resolve_date_range(date_range: str, custom_start: date | None = None, custom_end: date | None = None) -> tuple[date | None, date | None]:
    today = date.today()
    if date_range == "近7天":
        return today - timedelta(days=7), today
    if date_range == "近30天":
        return today - timedelta(days=30), today
    if date_range == "近90天":
        return today - timedelta(days=90), today
    return custom_start, custom_end


def build_query(market_segment: str, tech_route: str, information_type: str) -> str:
    route_terms = {
        "离子阱": "trapped ion quantum",
        "超导量子": "superconducting qubit",
        "中性原子": "neutral atom Rydberg quantum",
        "光量子": "photonic quantum",
        "硅自旋": "silicon spin qubit",
        "QKD": "quantum key distribution",
        "量子随机数": "quantum random number generator",
        "量子网络": "quantum network",
        "NV色心": "NV center diamond magnetometer",
        "冷原子传感": "cold atom quantum sensing",
        "原子钟": "atomic clock quantum",
        "量子磁力仪": "quantum magnetometer",
        "量子重力仪": "quantum gravimeter",
        "量子惯性测量": "quantum inertial sensing",
    }
    market_term = "" if market_segment == "量子市场总体" else market_segment
    info_term = "" if information_type == "全部" else information_type
    return " ".join([route_terms.get(tech_route, tech_route), market_term, info_term]).strip()


def selected_sources(sources: list[str]) -> list[str]:
    if "全部可用数据源" in sources:
        return ["arXiv", "OpenAlex", "USPTO", "RSS/新闻源"]
    return [SOURCE_ALIASES[source] for source in sources if source in SOURCE_ALIASES]


def collect_from_source(source: str, query: str, limit: int, start_date: date | None, end_date: date | None) -> list[dict]:
    if source == "arXiv":
        return arxiv_collector.collect(query, limit=limit, start_date=start_date, end_date=end_date)
    if source == "OpenAlex":
        return openalex_collector.collect(query, limit=limit, start_date=start_date, end_date=end_date)
    if source == "USPTO":
        return uspto_collector.collect(query, limit=limit, start_date=start_date, end_date=end_date)
    if source == "RSS/新闻源":
        return rss_collector.collect(query, limit=limit, start_date=start_date, end_date=end_date)
    return []


def normalize_record(record: dict, job_id: int, market_segment: str, tech_route: str, information_type: str) -> dict:
    classified = classify_record(record, fallback_market=market_segment, fallback_route=tech_route, fallback_info_type=information_type)
    title = str(record.get("title") or "")
    summary = str(record.get("summary") or record.get("abstract") or "")
    suggested_table = classified["suggested_table"]
    duplicate_flag, duplicate_reason = duplicate_status(
        {
            "title": title,
            "source_url": record.get("url", ""),
            "doi": record.get("doi", ""),
            "arxiv_id": record.get("arxiv_id", ""),
            "patent_number": record.get("patent_number", ""),
        },
        suggested_table,
    )
    return {
        "job_id": job_id,
        "title": title,
        "summary": summary,
        "content": record.get("content") or summary,
        "source_name": record.get("source_name") or record.get("source") or "",
        "source_url": record.get("url") or "",
        "published_at": record.get("published") or record.get("updated") or "",
        "market_segment": classified["market_segment"],
        "tech_route": classified["tech_route"],
        "information_type": classified["information_type"],
        "suggested_table": suggested_table,
        "confidence": classified["confidence"],
        "duplicate_flag": f"{duplicate_flag}：{duplicate_reason}" if duplicate_reason else duplicate_flag,
        "review_status": "待审核",
        "raw_json": json.dumps(record, ensure_ascii=False),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def write_staging(records: list[dict]) -> int:
    count = 0
    for record in records:
        insert_row("crawl_results_staging", record)
        count += 1
    return count


def run_auto_search(
    market_segment: str,
    tech_route: str,
    information_type: str,
    sources: list[str],
    date_range: str,
    custom_start: date | None = None,
    custom_end: date | None = None,
    limit_per_source: int = 10,
) -> tuple[int, pd.DataFrame]:
    started = datetime.now().isoformat(timespec="seconds")
    source_names = selected_sources(sources)
    try:
        enabled = read_table("data_sources")
        enabled_names = set(enabled.loc[enabled["enabled"].eq("是"), "source_name"].tolist())
        source_names = [source for source in source_names if source in enabled_names]
    except Exception:
        pass
    query = build_query(market_segment, tech_route, information_type)
    job_id = insert_row(
        "crawl_jobs",
        {
            "job_name": f"{market_segment}-{tech_route}-{information_type}",
            "source_name": ";".join(source_names),
            "market_segment": market_segment,
            "tech_route": tech_route,
            "information_type": information_type,
            "date_range": date_range,
            "status": "运行中",
            "started_at": started,
            "total_count": 0,
            "new_count": 0,
            "duplicate_count": 0,
            "failed_count": 0,
            "error_message": "",
        },
    )

    start_date, end_date = resolve_date_range(date_range, custom_start, custom_end)
    staging_records: list[dict] = []
    errors: list[str] = []
    failed_count = 0

    for source in source_names:
        try:
            raw_records = collect_from_source(source, query, limit_per_source, start_date, end_date)
            staging_records.extend(
                normalize_record(raw, job_id, market_segment, tech_route, information_type) for raw in raw_records
            )
        except Exception as exc:
            failed_count += 1
            errors.append(f"{source}: {exc}")

    if not staging_records:
        mock = {
            "title": f"{query} 自动检索占位结果",
            "summary": "外部数据源暂不可用时生成的占位结果，用于演示 staging 审核和入库流程。",
            "published": date.today().isoformat(),
            "url": "",
            "source": "系统Mock",
            "source_name": "系统Mock",
            "raw": {"errors": errors, "mock": True},
        }
        staging_records.append(normalize_record(mock, job_id, market_segment, tech_route, information_type))

    write_staging(staging_records)
    duplicate_count = sum(str(item["duplicate_flag"]).startswith("是") for item in staging_records)
    new_count = len(staging_records) - duplicate_count
    finished = datetime.now().isoformat(timespec="seconds")
    update_row(
        "crawl_jobs",
        job_id,
        {
            "status": "完成" if not errors else "部分失败",
            "finished_at": finished,
            "total_count": len(staging_records),
            "new_count": new_count,
            "duplicate_count": duplicate_count,
            "failed_count": failed_count,
            "error_message": "\n".join(errors),
        },
    )

    with get_connection() as conn:
        for source in source_names:
            conn.execute("UPDATE data_sources SET last_run_at=? WHERE source_name=?", (finished, source))
        conn.commit()

    return job_id, pd.DataFrame(staging_records)
