from __future__ import annotations

import pandas as pd


def chain_layer_counts(organizations: pd.DataFrame) -> pd.Series:
    if organizations.empty:
        return pd.Series(dtype=int)
    return organizations["industry_chain_role"].value_counts()

