"""
- normalize place names
- fix alternative names
- fix voyage ids, remove stray indices
"""

import re
from typing import Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

PLACE_NORMALIZATION = {
    "St. Johns": "St Johns",
    "St. John's": "St Johns",
    "N. York": "New York",
    # TODO: Add 
}

def normalize_place(name: Optional[str]) -> Optional[str]:
    if pd.isna(name):
        return None
    s = str(name).strip()
    # unify whitespace and punctuation
    s = re.sub(r"[‘’`]", "'", s)
    s = re.sub(r"[,;]+", "", s)
    s = re.sub(r"\s+", " ", s)
    # apply mapping
    mapped = PLACE_NORMALIZATION.get(s, s)
    return mapped

def clean_places_df(df: pd.DataFrame, column: str = "place") -> pd.DataFrame:
    df = df.copy()
    df[column] = df[column].astype(object).apply(normalize_place)
    return df

def fix_voyage_ids(df: pd.DataFrame, id_col: str = "voyage_id") -> pd.DataFrame:
    """
    Standardize voyage_id: strip whitespace, replace multiple delimiters,
    and attempt to produce a consistent string (used across notebooks).
    """
    df = df.copy()
    def _clean_id(x):
        if pd.isna(x):
            return x
        s = str(x).strip()
        # replace continuous separators with single dash
        s = re.sub(r"[\/\s_]+", "-", s)
        # remove duplicate dashes
        s = re.sub(r"-{2,}", "-", s)
        return s
    df[id_col] = df[id_col].apply(_clean_id)
    return df

def standardize_dates(df, col):
    """Convert dates to dd/mm/yyyy format."""
    df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d/%m/%Y")
    return df

def clean_text(text):
    """Remove extra spaces, normalize NaN markers."""
    if pd.isna(text):
        return None
    return str(text).replace("[nan]", "").strip()