from __future__ import annotations

import streamlit as st

from quantum_panorama.database import read_table
from quantum_panorama.dashboards.common import crud_panel, download_buttons, filter_by_sidebar, import_panel


def render() -> None:
    st.title("核心专家库")
    df = read_table("experts")
    tabs = st.tabs(["专家清单", "专家画像", "专家对比表", "新增/编辑/删除", "导入导出"])
    with tabs[0]:
        filtered = filter_by_sidebar(df, ["market_segment", "tech_routes", "institution", "country", "interview_value"])
        st.dataframe(filtered, use_container_width=True, hide_index=True)
    with tabs[1]:
        selected = st.selectbox("选择专家", df["name"].tolist())
        row = df[df["name"].eq(selected)].iloc[0]
        st.markdown(f"### {row['name']} | {row['title']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("机构", row["institution"])
        c2.metric("市场方向", row["market_segment"])
        c3.metric("可访谈价值", row["interview_value"])
        c4.metric("相关性", row["relevance_to_our_team"])
        st.write(f"**专业领域**：{row['expertise']}")
        st.write(f"**代表成果**：{row['representative_achievements']}")
        st.info(f"关键观点：{row['key_views']}")
        st.warning(f"风险备注：{row['risk_notes']}")
    with tabs[2]:
        st.dataframe(df[["name", "institution", "title", "market_segment", "tech_routes", "interview_value", "credibility", "relevance_to_our_team", "related_organizations"]], use_container_width=True, hide_index=True)
    with tabs[3]:
        crud_panel("experts", "专家")
    with tabs[4]:
        import_panel("experts")
        download_buttons(df, "experts")

