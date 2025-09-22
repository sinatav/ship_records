"""
Join and table-making helpers
"""

import pandas as pd
from typing import List

def join_ship_record_tables(ship_df: pd.DataFrame, record_df: pd.DataFrame,
                            left_on='ship_id', right_on='ship_id',
                            how: str='inner') -> pd.DataFrame:
    return ship_df.merge(record_df, left_on=left_on, right_on=right_on, how=how)

def make_joined_table(tables: List[pd.DataFrame], on: str='voyage_id', how: str='outer') -> pd.DataFrame:
    """
    Sequentially join list of tables on a common key.
    """
    if not tables:
        raise ValueError("tables list is empty")
    out = tables[0].copy()
    for t in tables[1:]:
        out = out.merge(t, on=on, how=how)
    return out