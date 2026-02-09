"""
Pull CDS spreads from WRDS Markit Credit Default Swaps.
"""

from pathlib import Path
import pandas as pd
import wrds

from settings import config

DATA_DIR = Path(config("DATA_DIR"))
WRDS_USERNAME = config("WRDS_USERNAME")

START_YEAR = 2006
END_YEAR = 2026

def pull_CDS(wrds_username=WRDS_USERNAME):
    db = wrds.Connection(wrds_username=wrds_username)

    dfs = []
    for year in range(START_YEAR, END_YEAR + 1):
        table = f"markit.cds{year}"

        sql = f"""
            SELECT
                date,
                ticker,
                redcode,
                tenor,
                currency,
                docclause,
                parspread AS cds_spread
            FROM
                {table}
            WHERE
                currency = 'USD'
                AND tenor IN ('1Y', '3Y', '5Y', '7Y', '10Y')
                AND docclause LIKE 'XR%%'
        """

        try: # Ensure all tables (i.e., for each year) are loaded
            df = db.raw_sql(sql, date_cols=["date"])
            dfs.append(df)
            print(f"Loaded {table}")
        except Exception as e:
            print(f"Skipping {table}: {e}")

    db.close()

    cds = pd.concat(dfs, ignore_index=True)
    cds = cds.sort_values(["date", "redcode", "tenor"]).reset_index(drop=True)

    return cds

def load_CDS(data_dir=DATA_DIR):
    return pd.read_parquet(data_dir / "CDS.parquet")

if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cds = pull_CDS(wrds_username=WRDS_USERNAME)
    cds.to_parquet(DATA_DIR / "CDS.parquet")