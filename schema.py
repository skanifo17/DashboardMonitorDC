def normalize(col):
    return (
        col.lower()
        .strip()
        .replace(" ", "_")
        .replace("-", "_")
    )


def auto_map_columns(df, alias_map, required=None):
    df = df.copy()

    # Normalisasi semua kolom asli
    norm_cols = {normalize(c): c for c in df.columns}

    mapped = {}

    for std_col, aliases in alias_map.items():
        for a in aliases:
            key = normalize(a)
            if key in norm_cols:
                mapped[std_col] = norm_cols[key]
                break

    # Rename yang ketemu
    df = df.rename(columns=mapped)

    # Validasi minimal
    if required:
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(
                f"Kolom wajib tidak ditemukan: {missing}. "
                f"Kolom tersedia: {list(df.columns)}"
            )

    return df
