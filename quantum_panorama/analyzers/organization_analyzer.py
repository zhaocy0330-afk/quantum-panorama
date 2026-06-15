from __future__ import annotations

import pandas as pd


def organization_counts(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=int)
    return df["organization_type"].value_counts()

