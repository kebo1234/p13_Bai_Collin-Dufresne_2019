import pandas as pd
import pytest
from pathlib import Path
def test_table1_values_within_tolerance():
    """Test Table 1 values match paper within tolerance"""
    # Paper's published values (Table 1)
    paper_values = {
        'ALL': {
            'Before Crisis': {'mean': -10, 'sd': 59},
            'Crisis I': {'mean': -118, 'sd': 192},
            'Crisis II': {'mean': -324, 'sd': 369},
            'Post-crisis': {'mean': -137, 'sd': 152}
        },
        'IG': {
            'Before Crisis': {'mean': -17, 'sd': 30},
            'Crisis I': {'mean': -83, 'sd': 108},
            # ... etc
        }
    }
    
    # Your replicated values
    table1 = pd.read_csv('_output/table1_replication.csv')
    
    # Tolerance: ±50 bps for mean, ±20% for SD (adjust based on your approach)
    tolerance_mean = 50
    tolerance_sd_pct = 0.20
    
    for category in ['ALL', 'IG', 'HY']:
        for phase in ['Before Crisis', 'Crisis I', 'Crisis II', 'Post-crisis']:
            our_mean = table1[table1['Category'] == category][f'{phase}_Mean'].values[0]
            paper_mean = paper_values[category][phase]['mean']
            
            diff = abs(our_mean - paper_mean)
            assert diff < tolerance_mean, \
                f"{category} {phase}: mean difference {diff} exceeds tolerance {tolerance_mean}"

def test_figure1_trend_matches_paper():
    """Test that Figure 1 shows same qualitative trends as paper"""
    basis = pd.read_parquet('_data/basis.parquet')
    basis['date'] = pd.to_datetime(basis['date'])
    
    # Before crisis: basis should be slightly negative (~-10 to -50 bps)
    before_crisis = basis[basis['date'] < '2007-07-01']
    ig_before = before_crisis[before_crisis['is_investment_grade'] == True]
    median_before = ig_before.groupby('date')['basis_bps'].median().median()
    
    # Should be negative but not too extreme
    assert median_before < 0, "Before crisis basis should be negative"
    assert median_before > -200, "Before crisis basis too negative (check PECDS)"
    
    # Crisis II: basis should be most negative
    crisis2 = basis[(basis['date'] >= '2008-09-01') & (basis['date'] < '2009-10-01')]
    ig_crisis2 = crisis2[crisis2['is_investment_grade'] == True]
    median_crisis2 = ig_crisis2.groupby('date')['basis_bps'].median().median()
    
    assert median_crisis2 < median_before, "Crisis II should be more negative than Before Crisis"