from pathlib import Path
import pytest
import pandas as pd
def test_all_output_files_exist():
    """Verify pipeline produces expected outputs"""
    assert Path('_output/table1_replication.tex').exists()
    assert Path('_output/replication_figure1.png').exists()
    assert Path('_output/extension_figure1.png').exists()

def test_data_row_counts():
    """Verify no data loss in pipeline"""
    matched = pd.read_parquet('_data/matched_bond_cds.parquet')
    pecds = pd.read_parquet('_data/pecds.parquet')
    basis = pd.read_parquet('_data/basis.parquet')
    
    # Should maintain same row count through pipeline
    assert len(matched) == len(pecds) == len(basis)

