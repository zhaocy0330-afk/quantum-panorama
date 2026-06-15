from __future__ import annotations

import pandas as pd

from .utils.classifier import infer_market_segment, infer_tech_routes
from .utils.text_cleaner import normalize_text


def clean_and_tag_records(df: pd.DataFrame, text_columns: list[str]) -> pd.DataFrame:
    result = df.copy()
    combined = result[text_columns].fillna("").agg(" ".join, axis=1)
    result["_normalized_text"] = combined.map(normalize_text)
    result["market_segment"] = result["_normalized_text"].map(infer_market_segment)
    result["tech_routes"] = result["_normalized_text"].map(lambda text: ";".join(infer_tech_routes(text)))
    return result.drop(columns=["_normalized_text"])

