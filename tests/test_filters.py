import pandas as pd
import pytest
from pathlib import Path
def test_bond_filters_match_paper():
    """Verify bond filtering criteria match Section 3.1"""
    bonds = pd.read_parquet('_data/matched_bond_cds.parquet')
    
    # All bonds should be non-convertible
    assert (bonds['conv'] == 0).all(), "Found convertible bonds"
    
    # TTM should be 3-7.5 years
    assert bonds['tmt'].min() >= 3.0, "Found bonds with TTM < 3 years"
    assert bonds['tmt'].max() <= 7.5, "Found bonds with TTM > 7.5 years"

def test_cds_filters():
    """Verify CDS filtering (USD, 5Y tenor)"""
    matched = pd.read_parquet('_data/matched_bond_cds.parquet')
    assert (matched['currency'] == 'USD').all()
    assert (matched['tenor'] == '5Y').all()