from __future__ import annotations

import plotly.express as px
import streamlit as st

from quantum_panorama.config import MARKET_SEGMENTS
from quantum_panorama.database import read_table


def render() -> None:
    st.title("市场分析页")
    selected = st.selectbox("选择市场方向", MARKET_SEGMENTS[:-1])
    orgs = read_table("organizations")
    experts = read_table("experts")
    interviews = read_table("interviews")
    papers = read_table("papers")
    patents = read_table("patents")
    financing = read_table("financing_events")
    policies = read_table("policies")
    tech_routes = read_table("tech_routes")

    if selected != "量子市场总体":
        orgs = orgs[orgs["market_segment"].isin([selected, "综合"])]
        experts = experts[experts["market_segment"].isin([selected, "综合"])]
        interviews = interviews[interviews["market_segment"].isin([selected, "综合"])]
        papers = papers[papers["market_segment"].isin([selected, "综合"])]
        patents = patents[patents["market_segment"].isin([selected, "综合"])]
        policies = policies[policies["market_segment"].isin([selected, "综合"])]
        tech_routes = tech_routes[tech_routes["market_segment"].eq(selected)]

    cols = st.columns(5)
    for col, item in zip(cols, [("主体", len(orgs)), ("专家", len(experts)), ("访谈", len(interviews)), ("论文", len(papers)), ("专利", len(patents))]):
        col.metric(item[0], item[1])

    st.subheader("市场定义与主要技术路线")
    route_names = "、".join(tech_routes["name"].tolist()) if not tech_routes.empty else "跨市场综合分析"
    st.write(f"**{selected}**：当前样本重点覆盖 {route_names}。")
    st.dataframe(tech_routes[["name", "principle", "maturity", "commercialization_path"]], use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("代表企业")
        st.dataframe(orgs[["name", "organization_type", "industry_chain_role", "tech_routes", "commercialization_stage", "investment_priority"]], use_container_width=True)
    with c2:
        st.subheader("代表专家")
        st.dataframe(experts[["name", "institution", "tech_routes", "interview_value", "key_views"]], use_container_width=True)

    st.subheader("趋势样本")
    charts = st.columns(3)
    if not papers.empty:
        paper_year = papers.assign(year=papers["publish_date"].str[:4]).groupby("year").size().reset_index(name="论文数")
        charts[0].plotly_chart(px.line(paper_year, x="year", y="论文数", markers=True), use_container_width=True)
    if not patents.empty:
        patent_year = patents.assign(year=patents["application_date"].str[:4]).groupby("year").size().reset_index(name="专利数")
        charts[1].plotly_chart(px.line(patent_year, x="year", y="专利数", markers=True), use_container_width=True)
    if not financing.empty:
        financing_year = financing.assign(year=financing["financing_date"].str[:4]).groupby("year").size().reset_index(name="融资案例数")
        charts[2].plotly_chart(px.line(financing_year, x="year", y="融资案例数", markers=True), use_container_width=True)

    st.subheader("AI市场判断")
    st.info("MVP 预置判断：请结合企业真实收入、下游付费意愿、政策项目质量和供应链可控性，避免只用论文或融资热度判断市场成熟度。")

