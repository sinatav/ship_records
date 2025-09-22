import pandas as pd
from .cleaning import clean_text
from .processor import process_rembarque, process_reembark, fill_emb_loc_for_rembarque
from .classification import classify_embark, classify_disembark
from .extractor import extract_date, extract_details

def run_pipeline(input_path, joined_path, output_path):
    df = pd.read_csv(input_path)

    # Step 1: Cleaning
    df = df.dropna(how="all", axis=0).dropna(how="all", axis=1)
    for col in ["Remarks", "Emb_loc", "Disemb_loc"]:
        if col in df.columns:
            df[col] = df[col].map(clean_text)

    # Step 2: Expansion
    df = process_rembarque(df)
    df = process_reembark(df)
    df = fill_emb_loc_for_rembarque(df)

    # Step 3: Extraction
    df["Emb_date"] = df["Remarks"].map(extract_date)
    df["Disemb_date"] = df["Remarks"].map(extract_date)
    df["details"] = df["Remarks"].map(extract_details)

    # Step 4: Classification
    df["emb_class"] = df["Remarks"].map(classify_embark)
    df["disemb_class"] = df.apply(
        lambda row: classify_disembark(row["Remarks"], row.get("Emb_loc"), row.get("Disemb_loc")),
        axis=1
    )

    # Step 5: Save
    df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    run_pipeline(
        input_path="data/raw/splitted.csv",
        joined_path="data/raw/_SELECT_r_p_v_vd_FROM_record_r_JOIN_person_p_202408261231.csv",
        output_path="data/processed/crew_movements_processed.csv"
    )
