"""
Calculate bond-implied CDS spreads (PECDS) following the simplified approach.

Bai, Collin-Dufresne (2019) - Simplified Implementation

Instead of the full Appendix A methodology (which requires daily TRACE prices
and swap rate curves), we use monthly bond yields from WRDS Bond Returns as
a direct proxy for PECDS.

Inputs:
    - qualified_bonds.parquet (from filter_bonds.py)
    - CDS.parquet (from pull_CDS.py)

Output:
    - pecds.parquet (bond-CDS pairs with PECDS spread)

Matching logic:
    - Bond company_symbol → CDS ticker (direct match)
    - CDS filtered to: currency=USD, docclause=MR, tenor=5Y
    - Monthly bond yield used for all days in that month
"""

from pathlib import Path
import pandas as pd

from settings import config

DATA_DIR = Path(config("DATA_DIR"))

# Paper's sample period
START_DATE = "2006-07-01"
END_DATE = "2014-12-30"


def load_data():
    """Load qualified bonds and CDS data."""
    bonds = pd.read_parquet(DATA_DIR / "qualified_bonds.parquet")
    cds = pd.read_parquet(DATA_DIR / "CDS.parquet")
    
    print(f"Loaded {len(bonds):,} qualified bond-month observations")
    print(f"Loaded {len(cds):,} CDS observations")
    print(f"Unique bond issuers:  {bonds['company_symbol'].nunique():,}")
    print(f"Unique CDS tickers:   {cds['ticker'].nunique():,}")
    
    return bonds, cds


def filter_cds(cds_df):
    """
    Filter CDS data per paper's criteria:
    - USD only
    - Modified Restructuring (MR) documentation clause
    - 5-year tenor (most liquid, used in paper)
    
    Parameters
    ----------
    cds_df : pd.DataFrame
        Raw CDS data
    
    Returns
    -------
    pd.DataFrame
        Filtered CDS data
    """
    df = cds_df.copy()
    print(f"\nFiltering CDS data...")
    print(f"Starting with {len(df):,} observations")
    
    # USD only
    df = df[df['currency'] == 'USD']
    print(f"After USD filter: {len(df):,}")
    
    # Modified Restructuring clause
    # df = df[df['docclause'] == 'MR']
    # print(f"After MR filter: {len(df):,}")
    # seem to be missing MR values and only have XR and XR14
    
    # 5-year tenor
    df = df[df['tenor'] == '5Y']
    print(f"After 5Y tenor filter: {len(df):,}")
    
    # Sample period
    df = df[(df['date'] >= START_DATE) & (df['date'] <= END_DATE)]
    print(f"After date filter: {len(df):,}")
    
    # Drop rows with missing CDS spread
    df = df[df['cds_spread'].notna()]
    print(f"After removing missing spreads: {len(df):,}")
    
    print(f"\nUnique CDS tickers after filtering: {df['ticker'].nunique():,}")
    
    return df


def match_bonds_to_cds(bonds_df, cds_df):
    """
    Match bonds to CDS entities via company_symbol = ticker.
    
    Monthly bond data is matched to daily CDS data by:
    1. Matching on company_symbol (bond) = ticker (CDS)
    2. For each day in a month, using that month's bond yield
    
    Parameters
    ----------
    bonds_df : pd.DataFrame
        Qualified bonds (monthly)
    cds_df : pd.DataFrame
        Filtered CDS data (daily)
    
    Returns
    -------
    pd.DataFrame
        Merged bond-CDS pairs
    """
    # Add year-month to both for merging
    bonds_df = bonds_df.copy()
    cds_df = cds_df.copy()
    
    bonds_df['year_month'] = bonds_df['date'].dt.to_period('M')
    cds_df['year_month'] = cds_df['date'].dt.to_period('M')
    
    # Rename bond date to avoid confusion after merge
    bonds_df = bonds_df.rename(columns={'date': 'bond_date'})
    
    # Merge: CDS daily × bond monthly via ticker + year_month
    merged = cds_df.merge(
        bonds_df,
        left_on=['ticker', 'year_month'],
        right_on=['company_symbol', 'year_month'],
        how='inner'
    )
    
    print(f"\nMatching results:")
    print(f"  Matched observations:    {len(merged):,}")
    print(f"  Unique bonds matched:    {merged['cusip'].nunique():,}")
    print(f"  Unique CDS tickers:      {merged['ticker'].nunique():,}")
    print(f"  Date range:              {merged['date'].min()} to {merged['date'].max()}")
    
    return merged


def calculate_pecds(merged_df):
    """
    Assign PECDS as the monthly bond yield.
    
    In the simplified approach, we use the bond yield directly as the
    bond-implied CDS spread (PECDS), applied to all days in that month.
    
    Parameters
    ----------
    merged_df : pd.DataFrame
        Merged bond-CDS data
    
    Returns
    -------
    pd.DataFrame
        Data with PECDS column added
    """
    df = merged_df.copy()
    
    # Bond yield is our PECDS proxy
    df['pecds'] = df['yield']
    
    # Select and rename relevant columns for output
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
    # Load data
    bonds, cds = load_data()
    
    # Filter CDS to paper's criteria
    cds_filtered = filter_cds(cds)
    
    # Match bonds to CDS
    merged = match_bonds_to_cds(bonds, cds_filtered)
    
    # Calculate PECDS
    pecds = calculate_pecds(merged)
    
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