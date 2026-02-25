# src/calc_PECDS.py
"""
Calculate bond-implied CDS spreads (PECDS).

Bai, Collin-Dufresne (2019) - Simplified Implementation

Instead of the full Appendix A methodology (which requires daily TRACE prices
and swap rate curves), we use monthly bond yields from WRDS Bond Returns as
a direct proxy for PECDS.

(Tentative) simplified PECDS calculation:
    - PECDS = bond yield
    - Monthly bond yield is used for all days in that month

Params:
    - matched_bond_cds.parquet

Returns:
    - pecds.parquet
"""

from pathlib import Path
import pandas as pd

from settings import config

DATA_DIR = Path(config("DATA_DIR"))

def calc_pecds(data_dir=DATA_DIR):
    df = pd.read_parquet(data_dir / "matched_bond_cds.parquet").copy()

    # Simplified PECDS proxy
    df["pecds"] = df["yield"]

    df.to_parquet(data_dir / "pecds.parquet", index=False)
    return df


if __name__ == "__main__":
    calc_pecds()