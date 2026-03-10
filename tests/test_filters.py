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
    
    # TTM should be 3-7.5 years in sample period
    assert sample_period['tmt'].min() >= 3.0, f"Found bonds with TTM < 3 years in sample period"
    assert sample_period['tmt'].max() <= 7.5, f"Found bonds with TTM > 7.5 years in sample period"