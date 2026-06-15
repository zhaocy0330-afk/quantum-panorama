from __future__ import annotations

import streamlit as st

from quantum_panorama.database import read_table
from quantum_panorama.dashboards.common import crud_panel, download_buttons, filter_by_sidebar, import_panel


def render() -> None:
    st.title("调研任务管理")
    df = read_table("research_tasks")
    tabs = st.tabs(["任务清单", "任务维护", "导入导出"])
    with tabs[0]:
        filtered = filter_by_sidebar(df, ["task_type", "related_market_segment", "related_tech_route", "owner", "status"])
        st.dataframe(filtered, use_container_width=True, hide_index=True)
    with tabs[1]:
        crud_panel("research_tasks", "调研任务")
    with tabs[2]:
        import_panel("research_tasks")
        download_buttons(df, "research_tasks")

