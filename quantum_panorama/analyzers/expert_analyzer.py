from __future__ import annotations

import pandas as pd


def high_value_experts(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "interview_value" not in df.columns:
        return df
    return df[df["interview_value"].eq("高")]

