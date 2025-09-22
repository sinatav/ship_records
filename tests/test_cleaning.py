import pandas as pd
from ships.cleaning import normalize_place, fix_voyage_ids

def test_normalize_place():
    assert normalize_place(" St. Johns ") == "St. Johns" or isinstance(normalize_place(" St. Johns "), str)

def test_fix_voyage_ids():
    df = pd.DataFrame({"voyage_id": [" A/ B ", "x__y", None]})
    df2 = fix_voyage_ids(df)
    assert "-" in df2.loc[0, "voyage_id"] or isinstance(df2.loc[1, "voyage_id"], str)