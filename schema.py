import streamlit as st

def normalize(col):
    return (
        str(col)
        .lower()
        .strip()
        .replace(" ", "_")
        .replace("-", "_")
    )


def auto_map_columns(df, alias_map, required=None):
    df = df.copy()

    # Normalisasi kolom asli
    original_cols = list(df.columns)
    norm_cols = {normalize(c): c for c in original_cols}

    mapped = {}

    for std_col, aliases in alias_map.items():
        for a in aliases:
            key = normalize(a)
            if key in norm_cols:
                mapped[std_col] = norm_cols[key]
                break

    # Rename yang ketemu
    df = df.rename(columns=mapped)

    # === TRUE SELF-HEALING ===
    if required:
        missing = [c for c in required if c not in df.columns]
        if missing:
            st.warning(
                f"⚠️ Kolom tidak ditemukan dan di-skip: {missing}. "
                f"Kolom tersedia: {original_cols}"
            )
            # Buat kolom kosong agar tidak crash
            for c in missing:
                df[c] = None

    return df
