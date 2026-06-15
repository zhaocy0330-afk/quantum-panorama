from __future__ import annotations

import pandas as pd


def route_heat(df: pd.DataFrame, column: str = "tech_routes") -> pd.Series:
    if df.empty or column not in df.columns:
        return pd.Series(dtype=int)
    return df[column].fillna("").str.split(";").explode().str.strip().replace("", pd.NA).dropna().value_counts()

