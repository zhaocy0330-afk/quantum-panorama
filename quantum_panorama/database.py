from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from .config import DATA_DIR, DB_PATH
from .collectors.source_registry import DEFAULT_DATA_SOURCES


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        create_schema(conn)
        ensure_default_data_sources(conn)
        if table_count(conn, "organizations") == 0:
            from .seed_data import seed_database

            seed_database(conn)
        export_seed_csvs()


def create_schema(conn: sqlite3.Connection) -> None:
    statements = [
        """
        CREATE TABLE IF NOT EXISTS market_segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            parent_id INTEGER,
            description TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS tech_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            market_segment TEXT,
            principle TEXT,
            core_components TEXT,
            key_metrics TEXT,
            maturity TEXT,
            engineering_challenges TEXT,
            commercialization_path TEXT,
            notes TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            short_name TEXT,
            organization_type TEXT,
            industry_chain_role TEXT,
            country TEXT,
            city TEXT,
            founded_year TEXT,
            website TEXT,
            market_segment TEXT,
            tech_routes TEXT,
            products_services TEXT,
            commercialization_stage TEXT,
            financing_stage TEXT,
            total_financing TEXT,
            latest_financing_date TEXT,
            investors TEXT,
            valuation_range TEXT,
            revenue_status TEXT,
            key_team TEXT,
            customers TEXT,
            suppliers TEXT,
            competitors TEXT,
            advantages TEXT,
            risks TEXT,
            tracking_status TEXT,
            investment_priority TEXT,
            cooperation_priority TEXT,
            relevance_to_our_team TEXT,
            credibility TEXT,
            verification_status TEXT,
            source TEXT,
            source_link TEXT,
            entered_by TEXT,
            information_type TEXT,
            created_at TEXT,
            updated_at TEXT,
            notes TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS upstream_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER,
            component_category TEXT,
            product_name TEXT,
            supported_tech_routes TEXT,
            key_metrics TEXT,
            domestic_substitution TEXT,
            substitution_maturity TEXT,
            bottleneck_level TEXT,
            supply_capacity TEXT,
            delivery_cycle TEXT,
            price_range TEXT,
            major_customers TEXT,
            competitors TEXT,
            technical_barriers TEXT,
            supply_chain_risks TEXT,
            interview_value TEXT,
            relevance_to_our_team TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS solution_providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER,
            system_product_name TEXT,
            product_form TEXT,
            supported_tech_routes TEXT,
            self_developed_parts TEXT,
            outsourced_parts TEXT,
            system_metrics TEXT,
            product_maturity TEXT,
            commercialization_stage TEXT,
            delivery_cases TEXT,
            order_status TEXT,
            revenue_status TEXT,
            core_competence TEXT,
            main_risks TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS downstream_customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER,
            customer_type TEXT,
            industry TEXT,
            application_scenario TEXT,
            specific_needs TEXT,
            purchased_quantum_products TEXT,
            potential_products TEXT,
            budget_capacity TEXT,
            procurement_cycle TEXT,
            decision_chain TEXT,
            pain_points TEXT,
            quantum_acceptance TEXT,
            demonstration_projects TEXT,
            suppliers TEXT,
            customer_feedback TEXT,
            demand_strength TEXT,
            willingness_to_pay TEXT,
            interview_value TEXT,
            relevance_to_our_team TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS experts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            institution TEXT,
            title TEXT,
            country TEXT,
            market_segment TEXT,
            tech_routes TEXT,
            expertise TEXT,
            representative_achievements TEXT,
            representative_papers TEXT,
            representative_patents TEXT,
            related_organizations TEXT,
            industrialization_experience TEXT,
            interview_value TEXT,
            credibility TEXT,
            relevance_to_our_team TEXT,
            contact TEXT,
            key_views TEXT,
            risk_notes TEXT,
            source TEXT,
            source_link TEXT,
            created_at TEXT,
            updated_at TEXT,
            notes TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            interviewee TEXT,
            interviewee_type TEXT,
            interview_date TEXT,
            interviewer TEXT,
            market_segment TEXT,
            tech_routes TEXT,
            related_organizations TEXT,
            related_experts TEXT,
            topic TEXT,
            raw_notes TEXT,
            key_points TEXT,
            verifiable_facts TEXT,
            subjective_judgments TEXT,
            important_conclusions TEXT,
            risks TEXT,
            follow_up_actions TEXT,
            credibility TEXT,
            sensitivity TEXT,
            information_type TEXT,
            verification_status TEXT,
            source TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS industry_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_organization_id INTEGER,
            target_organization_id INTEGER,
            relationship_type TEXT,
            market_segment TEXT,
            tech_routes TEXT,
            description TEXT,
            event_date TEXT,
            source TEXT,
            credibility TEXT,
            verification_status TEXT,
            notes TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            authors TEXT,
            institutions TEXT,
            publish_date TEXT,
            source TEXT,
            abstract TEXT,
            keywords TEXT,
            market_segment TEXT,
            tech_routes TEXT,
            link TEXT,
            industrial_relevance TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS patents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            patent_number TEXT,
            applicants TEXT,
            application_date TEXT,
            grant_status TEXT,
            market_segment TEXT,
            tech_routes TEXT,
            abstract TEXT,
            patent_type TEXT,
            country TEXT,
            related_organizations TEXT,
            related_experts TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS financing_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER,
            round TEXT,
            amount TEXT,
            currency TEXT,
            financing_date TEXT,
            investors TEXT,
            valuation TEXT,
            use_of_funds TEXT,
            source TEXT,
            credibility TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            region TEXT,
            issuing_body TEXT,
            publish_date TEXT,
            market_segment TEXT,
            tech_routes TEXT,
            policy_tools TEXT,
            funding_support TEXT,
            target_entities TEXT,
            relevance_to_our_team TEXT,
            link TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER,
            product_name TEXT,
            product_type TEXT,
            market_segment TEXT,
            tech_routes TEXT,
            maturity TEXT,
            application_scenario TEXT,
            target_customers TEXT,
            delivery_status TEXT,
            revenue_status TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS research_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_title TEXT NOT NULL,
            task_type TEXT,
            related_market_segment TEXT,
            related_tech_route TEXT,
            related_organization TEXT,
            related_expert TEXT,
            question_to_verify TEXT,
            owner TEXT,
            status TEXT,
            due_date TEXT,
            created_at TEXT,
            updated_at TEXT,
            notes TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS data_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL UNIQUE,
            source_type TEXT,
            base_url TEXT,
            requires_api_key TEXT,
            enabled TEXT,
            last_run_at TEXT,
            notes TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS search_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_segment TEXT,
            tech_route TEXT,
            information_type TEXT,
            source_name TEXT,
            query_text TEXT,
            enabled TEXT,
            notes TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS crawl_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT,
            source_name TEXT,
            market_segment TEXT,
            tech_route TEXT,
            information_type TEXT,
            date_range TEXT,
            status TEXT,
            started_at TEXT,
            finished_at TEXT,
            total_count INTEGER,
            new_count INTEGER,
            duplicate_count INTEGER,
            failed_count INTEGER,
            error_message TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS crawl_results_staging (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            title TEXT,
            summary TEXT,
            content TEXT,
            source_name TEXT,
            source_url TEXT,
            published_at TEXT,
            market_segment TEXT,
            tech_route TEXT,
            information_type TEXT,
            suggested_table TEXT,
            confidence TEXT,
            duplicate_flag TEXT,
            review_status TEXT,
            raw_json TEXT,
            created_at TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS deduplication_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_table TEXT,
            source_id INTEGER,
            fingerprint TEXT,
            duplicate_of TEXT,
            created_at TEXT
        )
        """,
    ]
    for statement in statements:
        conn.execute(statement)
    conn.commit()


def ensure_default_data_sources(conn: sqlite3.Connection) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    for source in DEFAULT_DATA_SOURCES:
        conn.execute(
            """
            INSERT INTO data_sources
                (source_name, source_type, base_url, requires_api_key, enabled, last_run_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_name) DO UPDATE SET
                source_type=excluded.source_type,
                base_url=excluded.base_url,
                requires_api_key=excluded.requires_api_key,
                notes=excluded.notes
            """,
            (
                source["source_name"],
                source["source_type"],
                source["base_url"],
                "是" if source["requires_api_key"] else "否",
                "是" if source["enabled"] else "否",
                source.get("last_run_at") or now,
                source["description"],
            ),
        )
    conn.commit()


def table_count(conn: sqlite3.Connection, table_name: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0])


def read_table(table_name: str) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)


def execute_query(query: str, params: Iterable | None = None) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params or [])


def get_columns(table_name: str) -> list[str]:
    with get_connection() as conn:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [row["name"] for row in rows]


def insert_row(table_name: str, data: dict) -> int:
    columns = [c for c in get_columns(table_name) if c != "id"]
    payload = {k: v for k, v in data.items() if k in columns}
    now = datetime.now().isoformat(timespec="seconds")
    if "created_at" in columns and not payload.get("created_at"):
        payload["created_at"] = now
    if "updated_at" in columns:
        payload["updated_at"] = now
    names = list(payload.keys())
    placeholders = ", ".join(["?"] * len(names))
    with get_connection() as conn:
        cursor = conn.execute(
            f"INSERT INTO {table_name} ({', '.join(names)}) VALUES ({placeholders})",
            [payload[name] for name in names],
        )
        conn.commit()
        return int(cursor.lastrowid)


def update_row(table_name: str, row_id: int, data: dict) -> None:
    columns = [c for c in get_columns(table_name) if c != "id"]
    payload = {k: v for k, v in data.items() if k in columns}
    if "updated_at" in columns:
        payload["updated_at"] = datetime.now().isoformat(timespec="seconds")
    assignments = ", ".join([f"{name}=?" for name in payload.keys()])
    with get_connection() as conn:
        conn.execute(
            f"UPDATE {table_name} SET {assignments} WHERE id=?",
            [payload[name] for name in payload.keys()] + [row_id],
        )
        conn.commit()


def delete_row(table_name: str, row_id: int) -> None:
    with get_connection() as conn:
        conn.execute(f"DELETE FROM {table_name} WHERE id=?", (row_id,))
        conn.commit()


def append_dataframe(table_name: str, df: pd.DataFrame) -> int:
    columns = [c for c in get_columns(table_name) if c != "id"]
    clean = df[[c for c in df.columns if c in columns]].copy()
    if clean.empty:
        return 0
    with get_connection() as conn:
        clean.to_sql(table_name, conn, if_exists="append", index=False)
    return len(clean)


def export_seed_csvs() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    for table in [
        "organizations",
        "experts",
        "interviews",
        "industry_relationships",
        "financing_events",
        "policies",
        "tech_routes",
        "papers",
        "patents",
        "products",
    ]:
        path = Path(DATA_DIR) / f"{table}.csv"
        if not path.exists():
            read_table(table).to_csv(path, index=False, encoding="utf-8-sig")
