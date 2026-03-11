"""
Pulls monthly CRSP Treasury data from WRDS.
"""

from pathlib import Path
import pandas as pd
import wrds

from settings import config

DATA_DIR = Path(config('DATA_DIR'))
WRDS_USERNAME = config('WRDS_USERNAME')

START_DATE = config('START_DATE')
END_DATE = config('END_DATE')

description_CRSP_treasuries = {
    'kytreasno': 'CRSP Treasury identifier',
    'kycrspid': 'CRSP Treasury issue identifier',
    'mcaldt': 'Observation date',
    'tmyld': 'Treasury yield',
    'tmduratn': 'Treasury duration'
}

def pull_CRSP_treasuries(wrds_username=WRDS_USERNAME):
    db = wrds.Connection(wrds_username=wrds_username)

    sql = f"""
        SELECT
            kytreasno,
            kycrspid,
            mcaldt,
            tmyld,
            tmduratn
        FROM
            crsp.tfz_mth
        WHERE
            mcaldt BETWEEN '{START_DATE}' AND '{END_DATE}'
            AND tmyld IS NOT NULL
            AND tmduratn IS NOT NULL
    """

    treasuries = db.raw_sql(sql, date_cols=['mcaldt'])
    db.close()

    # Keep only Treasury notes and bonds
    treasuries = treasuries.sort_values(['mcaldt', 'tmduratn']).reset_index(drop=True)

    return treasuries

def load_CRSP_treasuries(data_dir=DATA_DIR):
    return pd.read_parquet(data_dir / 'CRSP_treasuries.parquet')

if __name__ == '__main__':
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    treasuries = pull_CRSP_treasuries(wrds_username=WRDS_USERNAME)
    treasuries.to_parquet(DATA_DIR / 'CRSP_treasuries.parquet')