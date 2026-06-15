from __future__ import annotations

import pandas as pd


def priority_targets(organizations: pd.DataFrame) -> pd.DataFrame:
    if organizations.empty or "investment_priority" not in organizations.columns:
        return organizations
    return organizations[organizations["investment_priority"].isin(["A", "B"])]

