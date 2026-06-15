from __future__ import annotations

import pandas as pd


def round_distribution(financing: pd.DataFrame) -> pd.Series:
    if financing.empty:
        return pd.Series(dtype=int)
    return financing["round"].value_counts()

