"""
- splitting slash-separated indices
- extracting structured details from free-text remarks
"""

import pandas as pd
from typing import Dict

def explode_slash_indices(df: pd.DataFrame, column: str, new_column: str = None) -> pd.DataFrame:
    """
    If a column contains slash-separated values (e.g. 'A/B/C'),
    explode to multiple rows, preserving other columns.
    """
    new_column = new_column or column
    df = df.copy()
    # split into lists
    df['_split_list'] = df[column].astype(str).apply(lambda s: [x.strip() for x in s.split('/') if x.strip()])
    df = df.explode('_split_list')
    df[new_column] = df['_split_list']
    df = df.drop(columns=['_split_list'])
    return df

def extract_from_remarks(remarks: pd.Series, patterns: Dict[str, str]) -> pd.DataFrame:
    """
    Given a series of free-text remarks and patterns dict of {field: regex},
    return dataframe of extracted fields (NaN when not matched).
    """
    out = {}
    for name, pat in patterns.items():
        out[name] = remarks.str.extract(pat, expand=False)
    return pd.DataFrame(out)
