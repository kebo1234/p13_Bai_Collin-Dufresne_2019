from pathlib import Path
import pytest
import pandas as pd
import pyarrow.parquet as pq

def test_all_output_files_exist():
    """Verify pipeline produces expected outputs"""
    assert Path('_output/table1_replication.tex').exists()
    assert Path('_output/replication_figure1.png').exists()
    assert Path('_output/extension_figure1.png').exists()
def test_data_row_counts():
    """Verify no data loss in pipeline"""
    # Just check row counts without loading full data into memory
    import pyarrow.parquet as pq
    
    matched_rows = pq.read_metadata('_data/matched_bond_cds.parquet').num_rows
    pecds_rows = pq.read_metadata('_data/pecds.parquet').num_rows
    basis_rows = pq.read_metadata('_data/basis.parquet').num_rows
    
    # Should maintain same row count through pipeline
    assert matched_rows == pecds_rows == basis_rows, \
        f"Row count mismatch: matched={matched_rows}, pecds={pecds_rows}, basis={basis_rows}"