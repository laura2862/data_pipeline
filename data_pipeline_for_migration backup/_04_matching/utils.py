import pandas as pd

def clean_key(x):

    if pd.isna(x):
        return ""

    x = str(x).strip()

    if x.endswith(".0"):
        x = x[:-2]

    return x

def clean_text(x):

    if pd.isna(x):
        return ""

    return str(x).strip().upper()