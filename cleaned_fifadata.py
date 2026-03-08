"""
Clean all FIFA datasets in FIFA_DATA/ and save to FIFA_DATA/cleaned/.
Handles both detailed (FIFA17-22, 63+ cols) and compact (FIFA23, 29 cols) formats.
"""
import pandas as pd
import os

RAW_DIR = os.path.join(os.path.dirname(__file__), "FIFA_DATA")
OUT_DIR = os.path.join(RAW_DIR, "cleaned")
os.makedirs(OUT_DIR, exist_ok=True)

# Columns to drop (URL/image related)
DROP_PATTERNS = ["photo", "flag", "logo", "url", "face"]


def clean_player_file(path, year):
    print(f"  Loading FIFA{year}...")
    df = pd.read_csv(path, low_memory=False)

    # Drop image/URL columns
    drop_cols = [c for c in df.columns if any(p in c.lower() for p in DROP_PATTERNS)]
    df.drop(columns=drop_cols, inplace=True, errors="ignore")

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Parse Value/Wage strings like "€110.5M" or "€220K" → numeric
    for col in ["Value", "Wage", "Release Clause"]:
        if col in df.columns and df[col].dtype == object:
            df[col] = (
                df[col]
                .str.replace("€", "", regex=False)
                .str.replace(",", "", regex=False)
                .apply(_parse_money)
            )

    # Parse Height (e.g. "5'11" or "180cm") → cm
    if "Height" in df.columns and df["Height"].dtype == object:
        df["Height"] = df["Height"].apply(_parse_height)

    # Parse Weight (e.g. "154lbs" or "70kg") → kg
    if "Weight" in df.columns and df["Weight"].dtype == object:
        df["Weight"] = df["Weight"].apply(_parse_weight)

    # Clean position rating strings like "82+3" → 82
    for col in df.select_dtypes(include="object"):
        if df[col].astype(str).str.contains(r"\+\d+", na=False).any():
            df[col] = df[col].str.extract(r"(\d+)").astype(float)

    # Add year column for identification
    df["fifa_year"] = year

    out = os.path.join(OUT_DIR, f"fifa{year}_cleaned.csv")
    df.to_csv(out, index=False)
    print(f"  ✅ Saved → {out} ({len(df)} rows, {len(df.columns)} cols)")
    return df


def _parse_money(val):
    if pd.isna(val) or val == "" or val == "0":
        return 0
    val = str(val).strip()
    try:
        if val.endswith("M"):
            return float(val[:-1]) * 1_000_000
        elif val.endswith("K"):
            return float(val[:-1]) * 1_000
        return float(val)
    except ValueError:
        return 0


def _parse_height(val):
    if pd.isna(val):
        return None
    val = str(val).strip()
    if "cm" in val:
        return float(val.replace("cm", ""))
    if "'" in val:
        parts = val.replace('"', '').split("'")
        try:
            return round(float(parts[0]) * 30.48 + float(parts[1] if parts[1] else 0) * 2.54)
        except (ValueError, IndexError):
            return None
    return None


def _parse_weight(val):
    if pd.isna(val):
        return None
    val = str(val).strip()
    if "kg" in val:
        return float(val.replace("kg", ""))
    if "lbs" in val:
        return round(float(val.replace("lbs", "")) * 0.4536, 1)
    return None


if __name__ == "__main__":
    print("=" * 50)
    print("FIFA Data Cleaning Pipeline")
    print("=" * 50)

    files = sorted(
        [f for f in os.listdir(RAW_DIR) if f.endswith(".csv") and "official" in f.lower()]
    )
    print(f"Found {len(files)} datasets\n")

    for f in files:
        year = f.replace("FIFA", "").replace("_official_data.csv", "")
        clean_player_file(os.path.join(RAW_DIR, f), year)

    print("\n✅ All datasets cleaned and saved to FIFA_DATA/cleaned/")
