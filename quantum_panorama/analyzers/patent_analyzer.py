from __future__ import annotations

import pandas as pd


def applicant_ranking(patents: pd.DataFrame) -> pd.Series:
    if patents.empty:
        return pd.Series(dtype=int)
    return patents["applicants"].value_counts()

