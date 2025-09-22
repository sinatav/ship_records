import pandas as pd
from .extractor import split_remarks, extract_details

def process_rembarque(df):
    """Expand rows containing 'rembarqué' into multiple voyage legs."""
    expanded_rows = []
    for _, row in df.iterrows():
        remarks = row.get("Remarks", "")
        segments = split_remarks(remarks)
        for seg in segments:
            details = extract_details(seg)
            new_row = row.copy()
            new_row["Remarks"] = seg
            new_row["Emb_loc"] = details.get("embark_loc")
            new_row["Disemb_loc"] = details.get("disembark_loc")
            new_row["Emb_date"] = details.get("date")
            expanded_rows.append(new_row)
    return pd.DataFrame(expanded_rows)

def process_reembark(df):
    """Fill missing Emb_loc for rembarqué rows from previous disembark location."""
    df = df.sort_values(by=["Last Name", "First Name", "Function", "Emb_date"])
    for i in range(1, len(df)):
        if pd.isna(df.iloc[i]["Emb_loc"]) and "rembarqué" in str(df.iloc[i]["Remarks"]).lower():
            df.at[df.index[i], "Emb_loc"] = df.iloc[i-1]["Disemb_loc"]
    return df

def fill_emb_loc_for_rembarque(df):
    """Second pass: inherit Emb_loc from previous disembark if missing."""
    for i in range(1, len(df)):
        if pd.isna(df.iloc[i]["Emb_loc"]) and "rembarqué" in str(df.iloc[i]["Remarks"]).lower():
            df.at[df.index[i], "Emb_loc"] = df.iloc[i-1]["Disemb_loc"]
    return df