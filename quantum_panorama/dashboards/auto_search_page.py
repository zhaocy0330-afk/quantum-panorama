from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from quantum_panorama.collectors.pipeline import collect_sources
from quantum_panorama.storage import database as db


def hours_since(value: str) -> float | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        return (datetime.now() - dt).total_seconds() / 3600
    except Exception:
        return None


def render() -> None:
    st.title("自动检索中心")
    st.caption("Streamlit Cloud 不适合长期后台常驻任务；当前 MVP 为页面按钮触发的一次性低频采集，并预留 GitHub Actions。")
    db.init_db()

    sources = db.get_data_sources(enabled_only=False)
    if sources.empty:
        st.info("暂无数据源。请先到“数据源管理”添加或一键添加默认数据源。")
        return

    jobs = db.list_crawl_jobs(200)
    latest_by_source = {}
    if not jobs.empty:
        for _, row in jobs.dropna(subset=["source_id"]).iterrows():
            sid = int(row["source_id"])
            latest_by_source.setdefault(sid, row.get("finished_at") or row.get("started_at") or "")

    display = sources.copy()
    display["距离上次采集小时"] = display["id"].map(lambda sid: hours_since(latest_by_source.get(int(sid), "")))
    display["更新建议"] = display.apply(
        lambda row: "建议更新"
        if pd.isna(row["距离上次采集小时"]) or float(row["距离上次采集小时"] or 0) >= int(row["crawl_interval_hours"] or 24)
        else "暂不需要",
        axis=1,
    )
    st.dataframe(display, use_container_width=True, hide_index=True)

    enabled_sources = sources[sources["enabled"].eq(1)]
    selected_labels = st.multiselect(
        "选择数据源",
        (enabled_sources["id"].astype(str) + " | " + enabled_sources["name"].astype(str)).tolist(),
    )
    selected_ids = [int(label.split(" | ")[0]) for label in selected_labels]
    c1, c2 = st.columns(2)
    limit = c1.number_input("每个数据源最大采集条数", min_value=1, max_value=50, value=10)
    keywords = c2.text_input("关键词过滤覆盖", placeholder="留空则使用数据源配置关键词")

    if st.button("运行一次自动采集", type="primary", use_container_width=True):
        with st.spinner("正在运行自动采集..."):
            try:
                result = collect_sources(selected_ids, limit=int(limit), override_keywords=keywords)
                st.success(f"采集完成：发现 {result['total_found']} 条，新增 staging {result['total_saved']} 条。")
                if result["errors"]:
                    st.warning("失败或警告数据源：")
                    st.write("\n".join(result["errors"]))
                rows = []
                for item in result["results"]:
                    rows.append(
                        {
                            "source": item["source"].get("name", ""),
                            "found": item["found"],
                            "saved": item["saved"],
                            "errors": "\n".join(item["errors"]),
                        }
                    )
                st.subheader("本次采集日志")
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            except Exception as exc:
                st.error(f"自动采集失败：{exc}")

    st.subheader("最近采集任务")
    jobs = db.list_crawl_jobs(50)
    if jobs.empty:
        st.info("暂无采集日志。")
    else:
        st.dataframe(jobs, use_container_width=True, hide_index=True)

