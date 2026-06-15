from __future__ import annotations

import sys
from importlib import import_module, reload
from typing import Callable

import streamlit as st

from quantum_panorama.database import init_database as init_legacy_database
from quantum_panorama.storage.database import init_db as init_research_database


st.set_page_config(
    page_title="量子行业全景展示系统",
    page_icon="QP",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --qp-bg: #f7f8fb;
            --qp-panel: #ffffff;
            --qp-text: #19202a;
            --qp-muted: #667085;
            --qp-line: #d8dee9;
            --qp-accent: #0f766e;
        }
        .main .block-container { padding-top: 1.6rem; padding-bottom: 3rem; }
        h1, h2, h3 { letter-spacing: 0 !important; color: var(--qp-text); }
        div[data-testid="stMetric"] {
            background: var(--qp-panel);
            border: 1px solid var(--qp-line);
            border-radius: 8px;
            padding: 14px 16px;
        }
        .qp-card {
            background: #ffffff;
            border: 1px solid #d8dee9;
            border-radius: 8px;
            padding: 16px 18px;
            min-height: 120px;
        }
        .qp-card h4 { margin: 0 0 8px 0; color: #19202a; }
        .qp-muted { color: #667085; font-size: 0.92rem; }
        .qp-tag {
            display: inline-block;
            padding: 2px 8px;
            margin: 2px 4px 2px 0;
            border-radius: 999px;
            border: 1px solid #cbd5e1;
            background: #f8fafc;
            font-size: 0.78rem;
            color: #334155;
        }
        .qp-stage {
            background: #ecfdf5;
            border-left: 3px solid #0f766e;
            padding: 10px 12px;
            margin-bottom: 8px;
            border-radius: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_loader(module_name: str) -> Callable[[], None]:
    def _render() -> None:
        try:
            for dependency in (
                "quantum_panorama.collectors.source_registry",
                "quantum_panorama.storage.database",
            ):
                if dependency in sys.modules:
                    reload(sys.modules[dependency])
            module = import_module(f"quantum_panorama.dashboards.{module_name}")
            module = reload(module)
            module.render()
        except Exception as exc:
            st.error(f"页面加载失败：{module_name}")
            st.exception(exc)

    return _render


def main() -> None:
    try:
        init_legacy_database()
        init_research_database()
    except Exception as exc:
        st.error(f"数据库初始化失败：{exc}")
    inject_style()

    st.sidebar.title("量子 AI 投研系统")
    st.sidebar.caption("采集 · 审核 · 投研数据库 · AI分析 · 研报生成")

    pages = {
        "首页总览": page_loader("overview_page"),
        "数据源管理": page_loader("data_sources_page"),
        "手动采集中心": page_loader("manual_collect_page"),
        "自动检索中心": page_loader("auto_search_page"),
        "采集结果审核池": page_loader("staging_review_page"),
        "投研数据库": page_loader("research_items_page"),
        "AI研报生成中心": page_loader("ai_report_page"),
        "使用说明": page_loader("help_page"),
        "市场分析页": page_loader("market_page"),
        "技术路线页": page_loader("tech_route_page"),
        "核心企业库": page_loader("organization_page"),
        "核心专家库": page_loader("expert_page"),
        "访谈纪要库": page_loader("interview_page"),
        "量子产业链网络": page_loader("industry_network_page"),
        "统计看板": page_loader("statistics_page"),
        "调研任务管理": page_loader("research_task_page"),
        "旧版AI行研报告": page_loader("report_page"),
    }
    selected = st.sidebar.radio("功能模块", list(pages.keys()))
    st.sidebar.divider()
    st.sidebar.info("所有采集结果先进入审核池；AI 研报只基于已审核入库资料生成。")
    pages[selected]()


if __name__ == "__main__":
    main()
