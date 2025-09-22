import pandas as pd
from ships.routes import build_routes_graph

def test_build_routes_graph():
    df = pd.DataFrame({"from_place":["A","A","B"], "to_place":["B","C","A"]})
    G = build_routes_graph(df)
    assert G.has_edge("A","B")
    assert G["A"]["B"]["count"] == 1
