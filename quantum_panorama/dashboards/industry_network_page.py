from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from quantum_panorama.database import read_table
from quantum_panorama.dashboards.common import download_buttons, filter_by_sidebar


def relationship_view() -> pd.DataFrame:
    rel = read_table("industry_relationships")
    orgs = read_table("organizations")[["id", "name", "short_name", "industry_chain_role", "organization_type"]]
    rel = rel.merge(orgs.add_prefix("source_"), left_on="source_organization_id", right_on="source_id", how="left")
    rel = rel.merge(orgs.add_prefix("target_"), left_on="target_organization_id", right_on="target_id", how="left")
    return rel


def render() -> None:
    st.title("量子产业链网络")
    df = relationship_view()
    orgs = read_table("organizations")
    tabs = st.tabs(["分层结构", "关系表", "企业上下游", "网络统计"])

    with tabs[0]:
        selected_market = st.selectbox("按市场方向查看", ["全部"] + sorted(orgs["market_segment"].dropna().unique().tolist()))
        selected_route = st.selectbox("按技术路线查看", ["全部"] + sorted(set(";".join(orgs["tech_routes"].fillna("")).split(";")) - {""}))
        subset = orgs.copy()
        if selected_market != "全部":
            subset = subset[subset["market_segment"].isin([selected_market, "综合"])]
        if selected_route != "全部":
            subset = subset[subset["tech_routes"].fillna("").str.contains(selected_route, regex=False)]
        for role in ["上游", "中游", "下游", "支撑机构"]:
            st.markdown(f"#### {role}")
            role_df = subset[subset["industry_chain_role"].eq(role)]
            st.dataframe(role_df[["name", "organization_type", "tech_routes", "products_services", "tracking_status"]], use_container_width=True, hide_index=True)
            if role != "支撑机构":
                st.markdown("<div style='text-align:center;font-size:24px;'>↓</div>", unsafe_allow_html=True)

    with tabs[1]:
        filtered = filter_by_sidebar(df, ["market_segment", "tech_routes", "relationship_type", "credibility", "verification_status"])
        st.dataframe(
            filtered[["source_name", "relationship_type", "target_name", "market_segment", "tech_routes", "description", "event_date", "credibility", "verification_status"]],
            use_container_width=True,
            hide_index=True,
        )
        download_buttons(filtered, "industry_relationships")

    with tabs[2]:
        selected = st.selectbox("选择企业查看上下游关系", orgs["name"].tolist())
        org_id = int(orgs[orgs["name"].eq(selected)].iloc[0]["id"])
        upstream = df[df["target_organization_id"].eq(org_id)]
        downstream = df[df["source_organization_id"].eq(org_id)]
        c1, c2 = st.columns(2)
        c1.subheader("指向该主体的关系")
        c1.dataframe(upstream[["source_name", "relationship_type", "description", "credibility"]], use_container_width=True, hide_index=True)
        c2.subheader("该主体发出的关系")
        c2.dataframe(downstream[["target_name", "relationship_type", "description", "credibility"]], use_container_width=True, hide_index=True)

    with tabs[3]:
        st.plotly_chart(px.sunburst(orgs, path=["industry_chain_role", "organization_type", "short_name"], title="产业链主体分布"), use_container_width=True)
        counts = df["relationship_type"].value_counts().reset_index()
        counts.columns = ["关系类型", "数量"]
        st.plotly_chart(px.bar(counts, x="关系类型", y="数量", color="关系类型"), use_container_width=True)
