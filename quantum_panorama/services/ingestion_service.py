from __future__ import annotations

import json
from datetime import datetime

import pandas as pd

from quantum_panorama.database import get_connection, insert_row, read_table, update_row
from quantum_panorama.utils.deduplication import duplicate_status, fingerprint_record


TABLE_INSERT_MAPPERS = {
    "papers": lambda row, raw: {
        "title": row["title"],
        "authors": raw.get("authors", ""),
        "institutions": raw.get("institutions", ""),
        "publish_date": row["published_at"],
        "source": row["source_name"],
        "abstract": row["summary"],
        "keywords": raw.get("categories", ""),
        "market_segment": row["market_segment"],
        "tech_routes": row["tech_route"],
        "link": row["source_url"],
        "industrial_relevance": "自动检索入库，待研究员补充产业化相关性。",
    },
    "patents": lambda row, raw: {
        "title": row["title"],
        "patent_number": raw.get("patent_number", ""),
        "applicants": raw.get("applicants", ""),
        "application_date": row["published_at"],
        "grant_status": raw.get("grant_status", "待补充"),
        "market_segment": row["market_segment"],
        "tech_routes": row["tech_route"],
        "abstract": row["summary"],
        "patent_type": raw.get("patent_type", "待补充"),
        "country": raw.get("country", ""),
        "related_organizations": raw.get("related_organizations", ""),
        "related_experts": raw.get("related_experts", ""),
    },
    "financing_events": lambda row, raw: {
        "organization_id": raw.get("organization_id"),
        "round": raw.get("round", "待补充"),
        "amount": raw.get("amount", ""),
        "currency": raw.get("currency", ""),
        "financing_date": row["published_at"],
        "investors": raw.get("investors", ""),
        "valuation": raw.get("valuation", ""),
        "use_of_funds": row["summary"],
        "source": row["source_url"] or row["source_name"],
        "credibility": row["confidence"],
    },
    "policies": lambda row, raw: {
        "title": row["title"],
        "region": raw.get("region", "待补充"),
        "issuing_body": raw.get("issuing_body", row["source_name"]),
        "publish_date": row["published_at"],
        "market_segment": row["market_segment"],
        "tech_routes": row["tech_route"],
        "policy_tools": raw.get("policy_tools", ""),
        "funding_support": raw.get("funding_support", ""),
        "target_entities": raw.get("target_entities", ""),
        "relevance_to_our_team": "待判断",
        "link": row["source_url"],
    },
    "products": lambda row, raw: {
        "organization_id": raw.get("organization_id"),
        "product_name": row["title"],
        "product_type": raw.get("product_type", row["information_type"]),
        "market_segment": row["market_segment"],
        "tech_routes": row["tech_route"],
        "maturity": "待补充",
        "application_scenario": raw.get("application_scenario", ""),
        "target_customers": raw.get("target_customers", ""),
        "delivery_status": row["summary"],
        "revenue_status": "",
    },
    "organizations": lambda row, raw: {
        "name": raw.get("organization_name") or row["title"][:80],
        "short_name": "",
        "organization_type": raw.get("organization_type", "其他"),
        "industry_chain_role": raw.get("industry_chain_role", "支撑机构"),
        "country": raw.get("country", ""),
        "city": raw.get("city", ""),
        "website": row["source_url"],
        "market_segment": row["market_segment"],
        "tech_routes": row["tech_route"],
        "products_services": row["summary"],
        "commercialization_stage": "待补充",
        "tracking_status": "未接触",
        "investment_priority": "C",
        "cooperation_priority": "C",
        "relevance_to_our_team": "待判断",
        "credibility": row["confidence"],
        "verification_status": "待验证",
        "source": row["source_name"],
        "source_link": row["source_url"],
        "entered_by": "自动检索",
        "information_type": "事实",
        "notes": "自动检索入库，待研究员完善画像。",
    },
    "industry_relationships": lambda row, raw: {
        "source_organization_id": raw.get("source_organization_id"),
        "target_organization_id": raw.get("target_organization_id"),
        "relationship_type": raw.get("relationship_type", "合作关系"),
        "market_segment": row["market_segment"],
        "tech_routes": row["tech_route"],
        "description": row["summary"] or row["title"],
        "event_date": row["published_at"],
        "source": row["source_url"] or row["source_name"],
        "credibility": row["confidence"],
        "verification_status": "待验证",
        "notes": "自动检索入库，待确认关系主体。",
    },
}


def parse_raw(raw_json: str) -> dict:
    try:
        return json.loads(raw_json or "{}")
    except Exception:
        return {}


def ingest_staging_records(staging_ids: list[int]) -> dict[str, int | list[str]]:
    if not staging_ids:
        return {"inserted": 0, "duplicates": 0, "failed": 0, "errors": ["未选择记录"]}
    staging = read_table("crawl_results_staging")
    selected = staging[staging["id"].isin(staging_ids)]
    inserted = 0
    duplicates = 0
    failed = 0
    errors: list[str] = []

    for _, row in selected.iterrows():
        target = str(row.get("suggested_table") or "papers")
        raw = parse_raw(str(row.get("raw_json") or "{}"))
        duplicate_flag, reason = duplicate_status(
            {
                "title": row.get("title", ""),
                "source_url": row.get("source_url", ""),
                "doi": raw.get("doi", ""),
                "arxiv_id": raw.get("arxiv_id", ""),
                "patent_number": raw.get("patent_number", ""),
            },
            target,
        )
        if duplicate_flag == "是":
            duplicates += 1
            update_row("crawl_results_staging", int(row["id"]), {"review_status": f"重复跳过：{reason}"})
            continue
        mapper = TABLE_INSERT_MAPPERS.get(target)
        if mapper is None:
            failed += 1
            errors.append(f"{row['id']}: unsupported target table {target}")
            update_row("crawl_results_staging", int(row["id"]), {"review_status": "入库失败"})
            continue
        try:
            payload = mapper(row, raw)
            new_id = insert_row(target, payload)
            fingerprint = fingerprint_record(str(row.get("title", "")), str(row.get("source_url", "")), str(raw.get("doi") or raw.get("patent_number") or ""))
            insert_row(
                "deduplication_records",
                {
                    "source_table": target,
                    "source_id": new_id,
                    "fingerprint": fingerprint,
                    "duplicate_of": "",
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                },
            )
            update_row("crawl_results_staging", int(row["id"]), {"review_status": "已入库"})
            inserted += 1
        except Exception as exc:
            failed += 1
            errors.append(f"{row['id']}: {exc}")
            update_row("crawl_results_staging", int(row["id"]), {"review_status": "入库失败"})

    return {"inserted": inserted, "duplicates": duplicates, "failed": failed, "errors": errors}


def discard_staging_records(staging_ids: list[int]) -> int:
    if not staging_ids:
        return 0
    with get_connection() as conn:
        conn.executemany(
            "UPDATE crawl_results_staging SET review_status='已丢弃' WHERE id=?",
            [(int(item),) for item in staging_ids],
        )
        conn.commit()
    return len(staging_ids)

