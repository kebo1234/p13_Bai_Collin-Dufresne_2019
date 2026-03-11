# src/calc_PECDS.py
"""
Calculate bond-implied CDS spreads (PECDS).

Bai, Collin-Dufresne (2019) - Simplified Implementation

Instead of the full Appendix A methodology (which requires daily TRACE prices
and swap rate curves), we use monthly bond yields from WRDS Bond Returns 
and match them to treasuries using bond TTM and treasury duration, then 
subtract treasury yields (risk-free rate) to get bond credit spreads as a proxy for PECDS.

Simplified PECDS calculation:
    PECDS = bond yield - corresponding treasury yield

Params:
    - matched_bond_cds.parquet
    - CRSP_treasuries.parquet

Returns:
    - pecds.parquet
"""

from pathlib import Path
import pandas as pd
import numpy as np

from settings import config

DATA_DIR = Path(config("DATA_DIR"))

def _match_one_date(bonds_date, treas_date):
    """
    Binary search on sorted Treasury durations to match within one month at a time (to limit memory usage).
    """
    bonds_date = bonds_date.copy()
    treas_date = treas_date.copy()

    treas_date = treas_date.sort_values('tmduratn').reset_index(drop=True)

    treasury_dur = treas_date['tmduratn'].to_numpy()
    bond_tmt = bonds_date['tmt'].to_numpy()

    pos = np.searchsorted(treasury_dur, bond_tmt)

    left_idx = np.clip(pos - 1, 0, len(treas_date) - 1)
    right_idx = np.clip(pos, 0, len(treas_date) - 1)

    left_dist = np.abs(bond_tmt - treasury_dur[left_idx])
    right_dist = np.abs(bond_tmt - treasury_dur[right_idx])

    choose_right = right_dist < left_dist
    match_idx = np.where(choose_right, right_idx, left_idx)

    matched = treas_date.iloc[match_idx].reset_index(drop=True)
    bonds_date = bonds_date.reset_index(drop=True)

    bonds_date['matched_treasury_no'] = matched['kytreasno'].to_numpy()
    bonds_date['matched_treasury_id'] = matched['kycrspid'].to_numpy()
    bonds_date['matched_treasury_yield'] = matched['tmyld'].to_numpy()
    bonds_date['matched_treasury_duration'] = matched['tmduratn'].to_numpy()
    bonds_date['match_dist'] = np.abs(
        bonds_date['tmt'].to_numpy() - bonds_date['matched_treasury_duration'].to_numpy()
    )

    return bonds_date


def calc_pecds(data_dir=DATA_DIR):
    df = pd.read_parquet(data_dir / 'matched_bond_cds.parquet').copy()
    treasuries = pd.read_parquet(data_dir / 'CRSP_treasuries.parquet').copy()

    df['date'] = pd.to_datetime(df['date'])
    treasuries['mcaldt'] = pd.to_datetime(treasuries['mcaldt'])

    df = df[df['tmt'].notna() & df['yield'].notna()].copy()
    treasuries = treasuries[treasuries['tmduratn'].notna() & treasuries['tmyld'].notna()].copy()

    out = []

    treasury_by_date = {d: g for d, g in treasuries.groupby('mcaldt', sort=False)}

    for dt, bonds_date in df.groupby('date', sort=False):
        treas_date = treasury_by_date.get(dt)
        if treas_date is None or treas_date.empty:
            continue
        out.append(_match_one_date(bonds_date, treas_date))

    if not out:
        raise ValueError('No bond observations could be matched to Treasury observations.')

    result = pd.concat(out, ignore_index=True)

    result['pecds'] = result['yield'] - result['matched_treasury_yield']

    result.to_parquet(data_dir / 'pecds.parquet', index=False)
    return result


if __name__ == '__main__':
    calc_pecds()