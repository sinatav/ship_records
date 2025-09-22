"""
I/O helpers: load CSV/Parquet safely, small-sample creation helpers.
"""

from pathlib import Path
import pandas as pd
from typing import Union

def load_csv(path: Union[str, Path], **kwargs) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    return pd.read_csv(path, **kwargs)

def load_parquet(path: Union[str, Path], **kwargs) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    return pd.read_parquet(path, **kwargs)

def save_parquet(df: pd.DataFrame, path: Union[str, Path], index: bool=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=index)
