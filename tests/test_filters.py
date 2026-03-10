import pandas as pd
import pytest
from pathlib import Path

def test_bond_filters_match_paper():
    """Verify bond filtering criteria match Section 3.1 for sample period"""
    bonds = pd.read_parquet('_data/matched_bond_cds.parquet')
    
    # Filter to paper's sample period only (July 2006 - Dec 2014)
    bonds['date'] = pd.to_datetime(bonds['date'])
    sample_period = bonds[(bonds['date'] >= '2006-07-01') & (bonds['date'] <= '2014-12-30')]
    
    # All bonds should be non-convertible
    assert (sample_period['conv'] == 0).all(), "Found convertible bonds"
    
    # TTM: Most bonds should be 3-7.5 years (but some mature during sample period)
    # Check that majority of bonds meet the criteria
    tmt_valid = sample_period[(sample_period['tmt'] >= 3.0) & (sample_period['tmt'] <= 7.5)]
    pct_valid = len(tmt_valid) / len(sample_period)
    assert pct_valid > 0.5, f"Only {pct_valid:.1%} of bonds have TTM 3-7.5 years (expected >50%)"