"""
Calculate bond-implied CDS spreads (PECDS) following the simplified approach.

Bai, Collin-Dufresne (2019) - Simplified Implementation

Instead of the full Appendix A methodology (which requires daily TRACE prices
and swap rate curves), we use monthly bond yields from WRDS Bond Returns as
a direct proxy for PECDS.

Input:
    - matched_bond_cds.parquet (from prepare_data.py)

Output:
    - pecds.parquet (bond-CDS pairs with PECDS spread)

Simplified PECDS calculation:
    - PECDS = bond yield
    - Monthly bond yield is used for all days in that month
"""

from pathlib import Path
import pandas as pd

from settings import config

DATA_DIR = Path(config("DATA_DIR"))


def load_matched_data():
    """Load matched bond-CDS data from prepare_data.py."""
    matched = pd.read_parquet(DATA_DIR / "matched_bond_cds.parquet")
    
    print(f"Loaded {len(matched):,} matched bond-CDS observations")
    print(f"Unique bonds:     {matched['cusip'].nunique():,}")
    print(f"Unique CDS names: {matched['ticker'].nunique():,}")
    print(f"Date range:       {matched['date'].min()} to {matched['date'].max()}")
    
    return matched


def calculate_pecds(matched_df):
    """
    Calculate PECDS as the monthly bond yield.
    
    In the simplified approach, we use the bond yield directly as the
    bond-implied CDS spread (PECDS), applied to all days in that month.
    
    Parameters
    ----------
    matched_df : pd.DataFrame
        Matched bond-CDS data from prepare_data.py
    
    Returns
    -------
    pd.DataFrame
        Data with PECDS column added
    """
    df = matched_df.copy()
    
    # Bond yield is our PECDS proxy
    df['pecds'] = df['yield']
    
    # Select relevant columns for output
    output_cols = [
        'date',           # Daily date (from CDS)
        'bond_date',      # Monthly bond observation date
        'ticker',         # CDS ticker / company identifier
        'cusip',          # Bond CUSIP
        'issue_id',       # Mergent issue ID
        'cds_spread',     # 5Y CDS spread
        'pecds',          # Bond-implied CDS spread (= bond yield)
        'price_eom',      # End of month bond price
        'coupon',         # Bond coupon
        'tmt',            # Time to maturity
        'rating_class',   # Rating class
        'sp_rating',      # S&P rating
        'moodys_rating',  # Moody's rating
    ]
    
    # Keep only columns that exist
    output_cols = [c for c in output_cols if c in df.columns]
    df = df[output_cols]
    
    print(f"\nPECDS calculation complete")
    print(f"Total observations: {len(df):,}")
    print(f"CDS spread range:   {df['cds_spread'].min():.4f} to {df['cds_spread'].max():.4f}")
    print(f"PECDS range:        {df['pecds'].min():.4f} to {df['pecds'].max():.4f}")
    
    return df


def load_pecds(data_dir=DATA_DIR):
    """Load saved PECDS data."""
    path = Path(data_dir) / "pecds.parquet"
    return pd.read_parquet(path)


if __name__ == "__main__":
    # Load matched data
    matched = load_matched_data()
    
    # Calculate PECDS
    pecds = calculate_pecds(matched)
    
    # Save
    output_path = DATA_DIR / "pecds.parquet"
    pecds.to_parquet(output_path)
    print(f"\nSaved PECDS data to {output_path}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total observations:  {len(pecds):,}")
    print(f"Unique bonds:        {pecds['cusip'].nunique():,}")
    print(f"Unique CDS names:    {pecds['ticker'].nunique():,}")
    print(f"Date range:          {pecds['date'].min()} to {pecds['date'].max()}")
























