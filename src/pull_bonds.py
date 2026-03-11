# src/pull_bonds.py
"""
Pulls monthly bond data from WRDS Bond Returns.
"""

from pathlib import Path
import pandas as pd
import wrds

from settings import config

DATA_DIR = Path(config("DATA_DIR"))
WRDS_USERNAME = config("WRDS_USERNAME")

START_DATE = config('START_DATE')
END_DATE = "2024-08-31" # Last date range in database

description_bonds = {
    "date": "Observation date",
    "issue_id": "Mergent FISD issue identifier",
    "cusip": "Bond CUSIP",
    "company_symbol": "Issuer ticker",
    "bond_type": "Corporate bond type",
    "conv": "Convertible flag",
    "coupon": "Coupon rate",
    "maturity": "Bond maturity date",
    "tmt": "Time to maturity (years)",
    "price_eom": "End-of-month price",
    "yield": "Yield",
    "rating_class": "0 = IG, 1 = HY",
}

def pull_bonds(wrds_username=WRDS_USERNAME):
    sql = f"""
        SELECT
            date,
            issue_id,
            cusip,
            company_symbol,
            bond_type,
            conv,
            coupon,
            maturity,
            tmt,
            price_eom,
            yield,
            rating_class
        FROM wrdsapps.bondret
        WHERE date BETWEEN '{START_DATE}' AND '{END_DATE}'
    """

    db = wrds.Connection(wrds_username=wrds_username)
    bonds = db.raw_sql(sql, date_cols=["date", "maturity"])
    db.close()

    bonds = bonds.sort_values(["issue_id", "date"]).reset_index(drop=True)
    return bonds

if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    bonds = pull_bonds()
    bonds.to_parquet(DATA_DIR / "bond_prices.parquet")