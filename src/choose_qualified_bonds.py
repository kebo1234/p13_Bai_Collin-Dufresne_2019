"""
Chooses qualified bonds according to Section 3.1 of paper.

Most of the filtering outlined in (3.1) is already handled by WRDS Bond Returns; bonds in our dataset are:
- listed/traded in US public markets
- NOT structured notes, mortgage backed, or asset backed
- NOT agency-backed or equity-linked
- NOT floating-rate bonds (sample consists of only fixed- or zero-coupon bonds)
- NOT when-issued bonds
- NOT locked-in bonds
- NOT bonds with commission trading, special prices, or special sales conditions
- NOT bonds w/ transaction records that are cancelled, and adjust records that are subsequently corrected or reversed
- NOT bond trades with more than two-day settlements

So, we simply need to filter for bonds that:
- have 3-7.5 years remaing to maturity
- are NOT convertible
"""

from pathlib import Path
import pandas as pd

from settings import config

DATA_DIR = Path(config("DATA_DIR"))

def choose_qualified_bonds(data_dir=DATA_DIR):
    bonds = pd.read_parquet(data_dir / "bondret.parquet")
    cds = pd.read_parquet(data_dir / "cds.parquet")

    # Ensure cusips standardized
    bonds["cusip6"] = bonds["cusip"].str[:6]
    cds["cusip6"] = cds["redcode"].str[:6]

    # Restrict to non-convertible bonds and ensure fixed (& positive) or zero coupons
    bonds = bonds[(bonds["conv"] == 0) & (bonds["coupon"] >= 0)].copy()

    # Restrict to 3 <= TTM <= 7.5
    bonds = bonds[(bonds["tmt"] >= 3.0) & (bonds["tmt"] <= 7.5)]

    # Restrict to issuers with CDS trading (CDS–bond basis trivially requires CDS availability)
    cds_firms = cds[["cusip6"]].drop_duplicates()
    bonds = bonds.merge(cds_firms.assign(has_cds=True), on="cusip6", how="inner")

    bonds = bonds.sort_values(["cusip", "date"]).reset_index(drop=True)

    return bonds

if __name__ == "__main__":
    qualified = choose_qualified_bonds(DATA_DIR)
    qualified.to_parquet(DATA_DIR / "qualified_bonds.parquet")