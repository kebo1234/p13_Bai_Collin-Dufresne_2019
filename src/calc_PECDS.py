# src/calc_PECDS.py
"""
Simplified calculation of bond-implied CDS spreads (PECDS).

Instead of the full Appendix A methodology (which would require daily TRACE prices
and swap rate curves), we match bond yields to Treasury yields using bond TTM and Treasury
duration. We then subtract treasury yields from bond yields to get bond credit spreads as a proxy for PECDS.

Simplified PECDS calculation:
    PECDS = bond yield - corresponding Treasury yield

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

def _match_one_month(bonds_month, treas_month):
    """
    Binary search on sorted Treasury durations to match within one month at a time (to limit memory usage).
    """
    bonds_month = bonds_month.copy()
    treas_month = treas_month.copy()

    treas_month = treas_month.sort_values('tmduratn').reset_index(drop=True)

    treasury_dur = treas_month['tmduratn'].to_numpy()
    bond_tmt = bonds_month['tmt'].to_numpy()

    pos = np.searchsorted(treasury_dur, bond_tmt)

    left_idx = np.clip(pos - 1, 0, len(treas_month) - 1)
    right_idx = np.clip(pos, 0, len(treas_month) - 1)

    left_dist = np.abs(bond_tmt - treasury_dur[left_idx])
    right_dist = np.abs(bond_tmt - treasury_dur[right_idx])

    choose_right = right_dist < left_dist
    match_idx = np.where(choose_right, right_idx, left_idx)

    matched = treas_month.iloc[match_idx].reset_index(drop=True)
    bonds_month = bonds_month.reset_index(drop=True)

    bonds_month['matched_treasury_no'] = matched['kytreasno'].to_numpy()
    bonds_month['matched_treasury_id'] = matched['kycrspid'].to_numpy()
    bonds_month['matched_treasury_yield'] = matched['tmyld'].to_numpy()
    bonds_month['matched_treasury_duration'] = matched['tmduratn'].to_numpy()
    bonds_month['match_dist'] = np.abs(
        bonds_month['tmt'].to_numpy() - bonds_month['matched_treasury_duration'].to_numpy()
    )

    return bonds_month


def calc_pecds(data_dir=DATA_DIR):
    df = pd.read_parquet(data_dir / 'matched_bond_cds.parquet').copy()
    treasuries = pd.read_parquet(data_dir / 'CRSP_treasuries.parquet').copy()

    df['date'] = pd.to_datetime(df['date'])
    treasuries['mcaldt'] = pd.to_datetime(treasuries['mcaldt'])

    # Annualize Treasury yields
    treasuries['tmyld'] = treasuries['tmyld'] * 365

    # Convert to year-month for matching
    df['year_month'] = df['date'].dt.to_period('M')
    treasuries['year_month'] = treasuries['mcaldt'].dt.to_period('M')

    df = df[df['tmt'].notna() & df['yield'].notna()].copy()
    treasuries = treasuries[treasuries['tmduratn'].notna() & treasuries['tmyld'].notna()].copy()

    out = []
    treasury_by_month = {ym: g for ym, g in treasuries.groupby('year_month', sort=False)}

    for ym, bonds_month in df.groupby('year_month', sort=False):
        treas_month = treasury_by_month.get(ym)
        if treas_month is None or treas_month.empty:
            print(f"Warning: No Treasury data for {ym}, skipping {len(bonds_month):,} bonds")
            continue
        out.append(_match_one_month(bonds_month, treas_month))

    if not out:
        raise ValueError('No bond observations could be matched to Treasury observations.')

    result = pd.concat(out, ignore_index=True)
    result['pecds'] = result['yield'] - result['matched_treasury_yield']

    # Drop the temporary year_month column and convert back to string (for Polars compatibility)
    result['year_month'] = result['year_month'].astype(str)

    result.to_parquet(data_dir / 'pecds.parquet', index=False)
    return result


if __name__ == '__main__':
    result = calc_pecds()
    print("\nPECDS calculation complete!")
    print(f"Output rows: {len(result):,}")
    print(f"\nSample statistics:")
    print(result[['date', 'yield', 'matched_treasury_yield', 'pecds']].describe())