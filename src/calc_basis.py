# src/calc_basis.py

import pandas as pd
from pathlib import Path
from settings import config

DATA_DIR = Path(config('DATA_DIR'))

def calc_basis():
    """
    Compute CDS-bond basis from PECDS:
        - basis = cds_spread - pecds

    Input:
        - pecds.parquet (output of calc_pecds.py)

    Output:
        - basis.parquet
    """
    df = pd.read_parquet(DATA_DIR / 'matched_bond_cds.parquet').copy()
    df['basis'] = df['cds_spread'] - df['pecds']
    df.to_parquet(DATA_DIR / 'basis.parquet', index=False)

if __name__ == '__main__':
    calc_basis()