"""
Visualization helpers for routes and graphs.
Uses matplotlib for portability and compatibility.
"""

import matplotlib.pyplot as plt
import networkx as nx
from typing import Any, List

def plot_route_map(coords: List[tuple], title: str = "Route", ax: Any = None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(8,6))
    else:
        fig = None
    # coords: list of (lat, lon) or place names
    # if coordinates appear numeric, plot them
    if coords and isinstance(coords[0], (list, tuple)) and len(coords[0]) == 2 and all(isinstance(x, (int,float)) for x in coords[0]):
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        ax.plot(lons, lats, marker='o')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
    else:
        # fallback: simple ordered scatter with names on x-axis
        ax.plot(range(len(coords)), [0]*len(coords), marker='o')
        for i, name in enumerate(coords):
            ax.text(i, 0, str(name), rotation=45, ha='right', va='bottom')
    ax.set_title(title)
    return fig, ax

def plot_routes_graph(G, top_n=50, figsize=(10,8)):
    plt.figure(figsize=figsize)
    # create a subgraph of top edges by weight
    edges = sorted(G.edges(data=True), key=lambda e: e[2].get('count',1), reverse=True)[:top_n]
    H = nx.DiGraph()
    for u,v,d in edges:
        H.add_edge(u,v,weight=d.get('count',1))
    pos = nx.spring_layout(H, seed=42)
    weights = [H[u][v]['weight'] for u,v in H.edges()]
    nx.draw(H, pos, with_labels=True, node_size=300, arrowsize=15, width=[max(0.5, w/5) for w in weights])