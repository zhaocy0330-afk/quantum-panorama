from __future__ import annotations

import pandas as pd


def policy_region_counts(policies: pd.DataFrame) -> pd.Series:
    if policies.empty:
        return pd.Series(dtype=int)
    return policies["region"].value_counts()

