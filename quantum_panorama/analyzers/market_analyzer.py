from __future__ import annotations

import pandas as pd


def market_snapshot(organizations: pd.DataFrame, interviews: pd.DataFrame) -> dict[str, int]:
    return {
        "organizations": len(organizations),
        "upstream": int((organizations.get("industry_chain_role") == "上游").sum()) if not organizations.empty else 0,
        "midstream": int((organizations.get("industry_chain_role") == "中游").sum()) if not organizations.empty else 0,
        "downstream": int((organizations.get("industry_chain_role") == "下游").sum()) if not organizations.empty else 0,
        "interviews": len(interviews),
    }

