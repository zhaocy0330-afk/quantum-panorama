from __future__ import annotations

from quantum_panorama.config import TECH_ROUTES


ROUTE_KEYWORDS = {
    "离子阱": ["ion trap", "trapped ion", "paul trap", "surface-electrode trap", "离子阱"],
    "超导量子": ["superconducting qubit", "transmon", "josephson junction", "superconducting", "超导"],
    "中性原子": ["neutral atom", "rydberg atom", "rydberg", "中性原子"],
    "光量子": ["photonic quantum", "linear optical", "光量子", "光子"],
    "硅自旋": ["silicon spin", "spin qubit", "硅自旋"],
    "QKD": ["qkd", "quantum key distribution", "量子密钥分发"],
    "量子随机数": ["quantum random", "qrng", "量子随机数"],
    "量子网络": ["quantum network", "quantum repeater", "量子网络", "量子中继"],
    "NV色心": ["nv center", "nv centre", "diamond magnetometer", "nitrogen-vacancy", "NV色心"],
    "冷原子传感": ["cold atom", "atom interferometer", "冷原子"],
    "原子钟": ["atomic clock", "optical clock", "原子钟"],
    "量子磁力仪": ["quantum magnetometer", "magnetometry", "量子磁力仪"],
    "量子重力仪": ["quantum gravimeter", "gravity gradiometer", "量子重力仪"],
    "量子惯性测量": ["quantum inertial", "atom gyroscope", "inertial sensing", "量子惯性"],
}

INFO_KEYWORDS = {
    "前沿论文": ["arxiv", "paper", "journal", "conference", "doi", "论文", "研究"],
    "专利信息": ["patent", "专利", "uspto", "授权", "申请"],
    "融资信息": ["funding", "financing", "investment", "series a", "融资", "投资", "估值"],
    "产业政策": ["policy", "government", "grant", "subsidy", "政策", "补贴", "专项"],
    "企业新闻": ["company", "startup", "partnership", "launch", "企业", "合作", "发布"],
    "产品动态": ["product", "prototype", "delivery", "platform", "产品", "交付", "样机"],
}

INFO_TO_TABLE = {
    "前沿论文": "papers",
    "专利信息": "patents",
    "融资信息": "financing_events",
    "产业政策": "policies",
    "企业新闻": "organizations",
    "产品动态": "products",
}


def infer_market_segment(text: str) -> str:
    lower = str(text or "").lower()
    if any(keyword in lower for keyword in ["qkd", "quantum key distribution", "quantum communication", "量子通信"]):
        return "量子通信"
    if any(keyword in lower for keyword in ["nv center", "magnetometer", "atomic clock", "cold atom", "gravimeter", "sensing", "量子精密测量", "磁力仪", "重力仪", "原子钟"]):
        return "量子精密测量"
    if any(keyword in lower for keyword in ["qubit", "quantum computing", "ion trap", "superconducting", "neutral atom", "量子计算"]):
        return "量子计算"
    for market, routes in TECH_ROUTES.items():
        if market in text or any(route in text for route in routes):
            return market
    return "综合"


def infer_tech_routes(text: str) -> list[str]:
    lower = str(text or "").lower()
    routes: list[str] = []
    for route, keywords in ROUTE_KEYWORDS.items():
        if any(keyword.lower() in lower for keyword in keywords):
            routes.append(route)
    for route_group in TECH_ROUTES.values():
        routes.extend([route for route in route_group if route in str(text or "")])
    return list(dict.fromkeys(routes))


def infer_information_type(text: str, source_name: str = "") -> str:
    lower = f"{text or ''} {source_name or ''}".lower()
    if "arxiv" in lower or "openalex" in lower:
        return "前沿论文"
    if "uspto" in lower:
        return "专利信息"
    for info_type, keywords in INFO_KEYWORDS.items():
        if any(keyword.lower() in lower for keyword in keywords):
            return info_type
    return "企业新闻"


def infer_industry_chain_role(text: str) -> str:
    lower = str(text or "").lower()
    if any(keyword in lower for keyword in ["laser", "vacuum", "cryogenic", "component", "supplier", "激光", "真空", "低温", "供应"]):
        return "上游"
    if any(keyword in lower for keyword in ["system", "platform", "device", "solution", "整机", "系统", "平台"]):
        return "中游"
    if any(keyword in lower for keyword in ["customer", "application", "utility", "operator", "客户", "应用", "运营商", "电网"]):
        return "下游"
    return "支撑机构"


def suggest_table(information_type: str, text: str = "") -> str:
    if information_type in INFO_TO_TABLE:
        return INFO_TO_TABLE[information_type]
    inferred = infer_information_type(text)
    return INFO_TO_TABLE.get(inferred, "papers")


def classify_record(record: dict, fallback_market: str = "", fallback_route: str = "", fallback_info_type: str = "") -> dict:
    text = " ".join(str(record.get(key, "")) for key in ["title", "summary", "content", "source", "source_name"])
    info_type = fallback_info_type if fallback_info_type and fallback_info_type != "全部" else infer_information_type(text, str(record.get("source_name", "")))
    routes = infer_tech_routes(text)
    return {
        "market_segment": fallback_market if fallback_market and fallback_market != "量子市场总体" else infer_market_segment(text),
        "tech_route": fallback_route or (";".join(routes) if routes else ""),
        "information_type": info_type,
        "industry_chain_role": infer_industry_chain_role(text),
        "suggested_table": suggest_table(info_type, text),
        "confidence": "高" if routes else "中",
    }
