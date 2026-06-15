from __future__ import annotations

import streamlit as st

from quantum_panorama.database import read_table


def contains_route(df, route: str, column: str = "tech_routes"):
    if df.empty or column not in df.columns:
        return df
    return df[df[column].fillna("").str.contains(route, regex=False)]


def render() -> None:
    st.title("技术路线页")
    routes = read_table("tech_routes")
    selected = st.selectbox("选择技术路线", routes["name"].tolist())
    route = routes[routes["name"].eq(selected)].iloc[0]

    st.subheader(selected)
    c1, c2, c3 = st.columns(3)
    c1.metric("所属市场", route["market_segment"])
    c2.metric("成熟度", route["maturity"])
    c3.metric("商业化路径", route["commercialization_path"])

    st.markdown("**技术原理**")
    st.write(route["principle"])
    st.markdown("**核心系统构成 / 核心零部件**")
    st.write(route["core_components"])
    st.markdown("**关键性能指标**")
    st.write(route["key_metrics"])
    st.markdown("**工程化难点**")
    st.write(route["engineering_challenges"])

    orgs = contains_route(read_table("organizations"), selected)
    papers = contains_route(read_table("papers"), selected)
    patents = contains_route(read_table("patents"), selected)
    interviews = contains_route(read_table("interviews"), selected)

    st.subheader("上游核心零部件 / 整机企业 / 下游客户")
    cols = st.columns(3)
    for col, role, label in zip(cols, ["上游", "中游", "下游"], ["上游核心零部件", "整机/整体解决方案", "下游客户"]):
        with col:
            st.markdown(f"**{label}**")
            subset = orgs[orgs["industry_chain_role"].eq(role)]
            st.dataframe(subset[["name", "products_services", "commercialization_stage", "tracking_status"]], use_container_width=True)

    st.subheader("代表研究、专利、融资和访谈")
    tab1, tab2, tab3 = st.tabs(["近期论文", "近期专利", "访谈观点"])
    tab1.dataframe(papers, use_container_width=True)
    tab2.dataframe(patents, use_container_width=True)
    tab3.dataframe(interviews[["title", "interviewee", "key_points", "important_conclusions", "verification_status"]], use_container_width=True)

    st.subheader("发展趋势与投资判断")
    st.info(
        "MVP 判断框架：从论文活跃度、专利壁垒、核心部件国产替代、整机交付、下游真实需求和本团队相关性六个维度形成路线评分。"
    )

