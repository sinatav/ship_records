"""
Construct voyage routes and graphs.
Functions here follow the route-building / route_visual / routes_graph intent.
"""

from typing import List, Tuple
import pandas as pd
import networkx as nx
import logging

logger = logging.getLogger(__name__)

def route_coordinates_from_voyage(voyage_df: pd.DataFrame, place_col='place', order_col='date') -> List[Tuple]:
    """
    Given a voyage-level DataFrame with ordered place visits, return list of coordinates (if available)
    or place names in sequence. This function expects either lat/lon columns or a place name column.
    """
    # prefer lat/lon if present
    if {'lat', 'lon'}.issubset(voyage_df.columns):
        coords = list(voyage_df.sort_values(order_col)[['lat','lon']].itertuples(index=False, name=None))
        return coords
    else:
        seq = list(voyage_df.sort_values(order_col)[place_col].astype(str))
        return seq

def build_routes_graph(all_voyages: pd.DataFrame, from_col='from_place', to_col='to_place') -> nx.DiGraph:
    """
    Build directed graph of routes where edges between places accumulate counts.
    Expects rows represent voyage legs.
    """
    G = nx.DiGraph()
    for _, row in all_voyages.iterrows():
        a = row.get(from_col)
        b = row.get(to_col)
        if pd.isna(a) or pd.isna(b):
            continue
        if G.has_edge(a, b):
            G[a][b]['count'] += 1
        else:
            G.add_edge(a, b, count=1)
    return G
