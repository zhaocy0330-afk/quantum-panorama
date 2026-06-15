from __future__ import annotations

import streamlit as st

from quantum_panorama.database import read_table
from quantum_panorama.dashboards.common import crud_panel, download_buttons, filter_by_sidebar, import_panel


def render_profile(row) -> None:
    st.markdown(f"### {row['name']}")
    cols = st.columns(4)
    cols[0].metric("主体类型", row.get("organization_type", ""))
    cols[1].metric("产业链环节", row.get("industry_chain_role", ""))
    cols[2].metric("市场方向", row.get("market_segment", ""))
    cols[3].metric("投资优先级", row.get("investment_priority", ""))
    st.write(row.get("products_services", ""))
    st.info(f"优势：{row.get('advantages', '')}")
    st.warning(f"风险：{row.get('risks', '')}")
    st.caption(f"跟踪状态：{row.get('tracking_status', '')} | 可信度：{row.get('credibility', '')} | 验证状态：{row.get('verification_status', '')}")


def render() -> None:
    st.title("核心企业库")
    df = read_table("organizations")
    tabs = st.tabs(["主体清单", "企业画像", "企业对比表", "新增/编辑/删除", "导入导出"])

    with tabs[0]:
        filtered = filter_by_sidebar(df, ["organization_type", "market_segment", "tech_routes", "industry_chain_role", "country", "financing_stage", "commercialization_stage", "tracking_status", "investment_priority"])
        st.dataframe(filtered, use_container_width=True, hide_index=True)
    with tabs[1]:
        selected = st.selectbox("选择主体", df["name"].tolist())
        render_profile(df[df["name"].eq(selected)].iloc[0])
        st.subheader("关联关系")
        relationships = read_table("industry_relationships")
        related = relationships[
            relationships["source_organization_id"].eq(int(df[df["name"].eq(selected)].iloc[0]["id"]))
            | relationships["target_organization_id"].eq(int(df[df["name"].eq(selected)].iloc[0]["id"]))
        ]
        st.dataframe(related, use_container_width=True)
    with tabs[2]:
        st.dataframe(df[["name", "organization_type", "market_segment", "tech_routes", "commercialization_stage", "financing_stage", "total_financing", "tracking_status", "investment_priority", "relevance_to_our_team"]], use_container_width=True, hide_index=True)
    with tabs[3]:
        crud_panel("organizations", "主体")
    with tabs[4]:
        import_panel("organizations")
        download_buttons(df, "organizations")

