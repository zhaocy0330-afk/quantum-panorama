from __future__ import annotations

import pandas as pd


def verification_counts(df: pd.DataFrame) -> pd.Series:
    if df.empty or "verification_status" not in df.columns:
        return pd.Series(dtype=int)
    return df["verification_status"].value_counts()

