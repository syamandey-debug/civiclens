import pandas as pd


def clean_feedback_data(df):

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Remove rows where comment is missing
    df = df[df["comment"].notna()]

    # Remove extra spaces from comments
    df["comment"] = df["comment"].str.strip()

    # Remove rows where comment is empty after cleaning
    df = df[df["comment"] != ""]

    # Clean language
    df["language"] = df["language"].fillna("").str.strip()

    # Clean location
    df["location"] = df["location"].fillna("").str.strip()

    return df