# src/calc_basis.py
"""
Compute CDS-bond basis from PECDS according to Equation (1) in Section 2 of the paper:
    - basis = cds_spread - pecds

Additionally, to be used in figures/tables:
    - basis_bps = 10,000 * basis

Input:
    - pecds.parquet

Output:
    - basis.parquet
"""

import pandas as pd
from pathlib import Path
from settings import config

DATA_DIR = Path(config('DATA_DIR'))

def calc_basis():
    df = pd.read_parquet(DATA_DIR / 'pecds.parquet')
    df['basis'] = df['cds_spread'] - df['pecds']
    df['basis_bps'] = df['basis'] * 10000
    df.to_parquet(DATA_DIR / 'basis.parquet', index=False)

if __name__ == '__main__':
    calc_basis()