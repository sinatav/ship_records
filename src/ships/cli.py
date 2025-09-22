"""Simple CLI entrypoint using argparse for common operations."""

import argparse
import logging
from pathlib import Path

from .data_io import load_csv, save_parquet
from .cleaning import clean_places_df, fix_voyage_ids
from .joins import make_joined_table

logger = logging.getLogger(__name__)

def _setup_logging(level=logging.INFO):
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def main():
    parser = argparse.ArgumentParser(prog="ships", description="Ships dataset utilities")
    parser.add_argument("--input", "-i", required=True, help="Input CSV (or multiple, comma-separated)")
    parser.add_argument("--out", "-o", required=True, help="Output parquet path")
    parser.add_argument("--clean-places", action="store_true", help="Run place cleaning")
    parser.add_argument("--fix-voyage-ids", action="store_true", help="Normalize voyage IDs")
    args = parser.parse_args()
    _setup_logging()
    inputs = [p.strip() for p in args.input.split(",")]
    dfs = []
    for p in inputs:
        logger.info("Loading %s", p)
        df = load_csv(p)
        dfs.append(df)
    if len(dfs) == 1:
        df = dfs[0]
    else:
        df = make_joined_table(dfs)
    if args.clean_places:
        logger.info("Cleaning place names")
        df = clean_places_df(df, column='place')
    if args.fix_voyage_ids:
        logger.info("Fixing voyage ids")
        df = fix_voyage_ids(df, id_col='voyage_id')
    out_path = Path(args.out)
    save_parquet(df, out_path)
    logger.info("Saved %s", out_path)
