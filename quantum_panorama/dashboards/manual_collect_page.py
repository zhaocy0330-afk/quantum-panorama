from __future__ import annotations

import pandas as pd
import streamlit as st

from quantum_panorama.collectors.manual_collector import split_urls
from quantum_panorama.collectors.pipeline import stage_manual_urls
from quantum_panorama.storage import database as db


def render() -> None:
    st.title("手动采集中心")
    st.caption("输入单个或多个 URL，抓取 title、meta description 和正文前 1000 字，结果进入 staging 审核池。")
    db.init_db()

    single_url = st.text_input("单 URL")
    batch_urls = st.text_area("批量 URL", height=160, placeholder="每行一个 URL")
    c1, c2 = st.columns(2)
    keywords = c1.text_input("关键词过滤", placeholder="留空则不过滤")
    limit = c2.number_input("最大采集数量", min_value=1, max_value=100, value=20)

    if st.button("开始手动采集", type="primary", use_container_width=True):
        urls = split_urls("\n".join([single_url, batch_urls]))
        if not urls:
            st.warning("请至少输入一个 URL。")
            return
        with st.spinner("正在采集 URL..."):
            try:
                result = stage_manual_urls(urls, keywords=keywords, limit=int(limit))
                records = pd.DataFrame(result["records"])
                st.success(f"采集成功 {len(result['records'])} 条，写入 staging {result['saved']} 条。")
                if result["failures"]:
                    st.warning("部分 URL 采集失败：")
                    st.dataframe(pd.DataFrame(result["failures"]), use_container_width=True, hide_index=True)
                if not records.empty:
                    st.subheader("本次采集结果预览")
                    st.dataframe(records, use_container_width=True, hide_index=True)
                    st.download_button(
                        "导出本次采集结果 CSV",
                        records.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                        "manual_collect_results.csv",
                        "text/csv",
                    )
            except Exception as exc:
                st.error(f"手动采集失败：{exc}")

