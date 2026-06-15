from __future__ import annotations

import os
from pathlib import Path


def _read_setting(name: str, default: str = "") -> str:
    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.getenv(name, default)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = Path(_read_setting("QUANTUM_PANORAMA_DB_PATH", str(DATA_DIR / "quantum_panorama.sqlite3")))

MARKET_SEGMENTS = ["量子市场总体", "量子计算", "量子通信", "量子精密测量", "综合"]

TECH_ROUTES = {
    "量子计算": ["超导量子", "离子阱", "中性原子", "光量子", "硅自旋", "拓扑量子"],
    "量子通信": ["QKD", "量子随机数", "量子网络", "量子中继", "卫星量子通信", "量子安全通信"],
    "量子精密测量": ["原子钟", "量子磁力仪", "量子重力仪", "量子惯性测量", "NV色心", "冷原子传感", "离子阱精密测量"],
}

ORGANIZATION_TYPES = [
    "上游核心零部件企业",
    "整机或整体解决方案提供商",
    "下游客户或应用方",
    "投资机构",
    "高校科研院所",
    "政府平台",
    "产业园区",
    "其他",
]

CHAIN_ROLES = ["上游", "中游", "下游", "支撑机构"]
CREDIBILITY_LEVELS = ["高", "中", "低"]
VERIFICATION_STATUS = ["已验证", "待验证", "存疑"]
INFO_TYPES = ["事实", "判断", "推测", "观点"]
PRIORITIES = ["A", "B", "C", "D"]
TRACKING_STATUS = ["未接触", "已接触", "已访谈", "已尽调", "已合作", "已放弃", "持续跟踪"]

AUTO_SEARCH_TECH_ROUTES = [
    "离子阱",
    "超导量子",
    "中性原子",
    "光量子",
    "硅自旋",
    "QKD",
    "量子随机数",
    "量子网络",
    "NV色心",
    "冷原子传感",
    "原子钟",
    "量子磁力仪",
    "量子重力仪",
    "量子惯性测量",
]

AUTO_SEARCH_INFO_TYPES = ["前沿论文", "专利信息", "融资信息", "产业政策", "企业新闻", "产品动态", "全部"]
AUTO_SEARCH_DATE_RANGES = ["近7天", "近30天", "近90天", "自定义时间"]


def get_secret(name: str, default: str = "") -> str:
    """Read a setting from Streamlit secrets when available, then env vars."""
    return _read_setting(name, default)
