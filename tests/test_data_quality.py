import pandas as pd
import pytest
from pathlib import Path
def test_no_extreme_yields():
    """Ensure yield filter removed all unrealistic values"""
    matched = pd.read_parquet('_data/matched_bond_cds.parquet')
    assert matched['yield'].max() < 1.0, "Found yields > 100%"
    assert matched['yield'].min() > -0.05, "Found yields < -5%"

def test_no_missing_required_fields():
    """Verify no missing values in key fields"""
    matched = pd.read_parquet('_data/matched_bond_cds.parquet')
    assert matched['yield'].notna().all()
    assert matched['cds_spread'].notna().all()
    assert matched['company_symbol'].notna().all()