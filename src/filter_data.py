"""
Data preparation pipeline for Bai, Collin-Dufresne (2019) replication.

This script combines:
1. Bond filtering (from filter_bonds.py)
2. CDS filtering (from calc_PECDS.py)
3. Bond-CDS matching

Inputs:
    - bond_prices.parquet (from WRDS Bond Returns)
    - Mergent_FISD_ratings.parquet (from pull_LSEG_Mergent.py)
    - CDS.parquet (from pull_CDS.py)

Outputs:
    - qualified_bonds.parquet
    - matched_bond_cds.parquet (ready for PECDS calculation)
"""

from pathlib import Path
import pandas as pd

from settings import config

DATA_DIR = Path(config("DATA_DIR"))

START_DATE = "2006-07-01"
END_DATE = "2014-12-30"
MIN_TTM = 3.0
MAX_TTM = 7.5


# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================

def load_all_data():
    """Load bond prices, ratings, and CDS data."""
    print("="*60)
    print("LOADING DATA")
    print("="*60)
    
    bond_prices = pd.read_parquet(DATA_DIR / "bond_prices.parquet")
    ratings = pd.read_parquet(DATA_DIR / "Mergent_FISD_ratings.parquet")
    cds = pd.read_parquet(DATA_DIR / "CDS.parquet")
    
    print(f"Loaded {len(bond_prices):,} bond-month observations")
    print(f"Loaded {len(ratings):,} rating records")
    print(f"Loaded {len(cds):,} CDS observations")
    
    return bond_prices, ratings, cds


# ============================================================================
# STEP 2: FILTER BONDS
# ============================================================================

def filter_bonds(bond_prices):
    """
    Apply paper's filtering criteria to bond prices data.
    
    Criteria:
    1. Sample period: July 2006 - December 2014
    2. Remove convertible bonds
    3. Time-to-maturity: 3 to 7.5 years
    4. Remove bonds with missing prices or yields
    5. Remove bonds with missing company symbol
    6. Keep only rated bonds
    7. Keep only corporate bond types
    """
    print("\n" + "="*60)
    print("FILTERING BONDS")
    print("="*60)
    
    df = bond_prices.copy()
    print(f"Starting with {len(df):,} bond-month observations")
    
    # Filter 1: Sample period
    df = df[(df['date'] >= START_DATE) & (df['date'] <= END_DATE)]
    print(f"After date filter ({START_DATE} to {END_DATE}): {len(df):,}")
    
    # Filter 2: Remove convertible bonds
    df = df[df['conv'] == 0]
    print(f"After removing convertible bonds: {len(df):,}")
    
    # Filter 3: Time-to-maturity between 3 and 7.5 years
    df = df[(df['tmt'] >= MIN_TTM) & (df['tmt'] <= MAX_TTM)]
    print(f"After TTM filter ({MIN_TTM} to {MAX_TTM} years): {len(df):,}")
    
    # Filter 4: Remove bonds with missing prices or yields
    df = df[df['price_eom'].notna() & df['yield'].notna()]
    print(f"After removing missing prices/yields: {len(df):,}")
    
    # Filter 5: Remove bonds with missing company symbol
    df = df[df['company_symbol'].notna()]
    print(f"After removing missing company symbol: {len(df):,}")
    
    # Filter 6: Keep only rated bonds
    df = df[df['rating_class'].notna()]
    print(f"After removing unrated bonds: {len(df):,}")
    
    # Filter 7: Keep only corporate bond types
    corporate_bond_types = ['CDEB', 'CMTN', 'CMTZ', 'CZ', 'USBN']
    df = df[df['bond_type'].isin(corporate_bond_types)]
    print(f"After keeping only corporate bond types: {len(df):,}")
    
    print(f"\nFinal: {len(df):,} bond-month observations")
    print(f"  Unique bonds:   {df['cusip'].nunique():,}")
    print(f"  Unique issuers: {df['company_symbol'].nunique():,}")
    
    return df


def add_ratings(bond_df, ratings_df):
    """
    Add Mergent FISD ratings to bond data.
    
    Per the paper:
    - If rated by both Moody's and S&P, take average
    - If rated by only one agency, use that rating
    """
    print("\nAdding detailed ratings...")
    
    # Get most recent S&P rating per bond
    sp = ratings_df[ratings_df['rating_type'] == 'SPR'].copy()
    sp = sp.sort_values(['issue_id', 'rating_date']).groupby('issue_id').last()
    sp = sp[['rating', 'investment_grade']].rename(
        columns={'rating': 'sp_rating', 'investment_grade': 'sp_ig'}
    )
    
    # Get most recent Moody's rating per bond
    moodys = ratings_df[ratings_df['rating_type'] == 'MR'].copy()
    moodys = moodys.sort_values(['issue_id', 'rating_date']).groupby('issue_id').last()
    moodys = moodys[['rating', 'investment_grade']].rename(
        columns={'rating': 'moodys_rating', 'investment_grade': 'moodys_ig'}
    )
    
    # Merge ratings
    df = bond_df.merge(sp, on='issue_id', how='left')
    df = df.merge(moodys, on='issue_id', how='left')
    
    print(f"Ratings coverage:")
    print(f"  S&P only:     {(df['sp_rating'].notna() & df['moodys_rating'].isna()).sum():,}")
    print(f"  Moody's only: {(df['sp_rating'].isna() & df['moodys_rating'].notna()).sum():,}")
    print(f"  Both:         {(df['sp_rating'].notna() & df['moodys_rating'].notna()).sum():,}")
    print(f"  Neither:      {(df['sp_rating'].isna() & df['moodys_rating'].isna()).sum():,}")
    
    return df


# ============================================================================
# STEP 3: FILTER CDS
# ============================================================================

def filter_cds(cds_df):
    """
    Filter CDS data per paper's criteria:
    - USD only
    - 5-year tenor (most liquid)
    - Sample period
    
    Note: Paper uses MR (Modified Restructuring) clause, but our data
    only contains XR14 and XR. We skip docclause filtering to keep all data.
    """
    print("\n" + "="*60)
    print("FILTERING CDS")
    print("="*60)
    
    df = cds_df.copy()
    print(f"Starting with {len(df):,} observations")
    
    # USD only
    df = df[df['currency'] == 'USD']
    print(f"After USD filter: {len(df):,}")
    
    # Note: Skipping docclause filter (would be MR, but data has XR14/XR)
    print(f"Docclause distribution: {df['docclause'].value_counts().to_dict()}")
    
    # 5-year tenor
    df = df[df['tenor'] == '5Y']
    print(f"After 5Y tenor filter: {len(df):,}")
    
    # Sample period
    df = df[(df['date'] >= START_DATE) & (df['date'] <= END_DATE)]
    print(f"After date filter: {len(df):,}")
    
    # Drop missing CDS spreads
    df = df[df['cds_spread'].notna()]
    print(f"After removing missing spreads: {len(df):,}")
    
    print(f"\nFinal: {len(df):,} CDS observations")
    print(f"  Unique CDS tickers: {df['ticker'].nunique():,}")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    
    return df


# ============================================================================
# STEP 4: MATCH BONDS TO CDS
# ============================================================================

def match_bonds_to_cds(bonds_df, cds_df):
    """
    Match bonds to CDS entities via company_symbol = ticker.
    
    Monthly bond data is matched to daily CDS data by:
    1. Matching on company_symbol (bond) = ticker (CDS)
    2. For each day in a month, using that month's bond data
    """
    print("\n" + "="*60)
    print("MATCHING BONDS TO CDS")
    print("="*60)
    
    # Add year-month for merging
    bonds_df = bonds_df.copy()
    cds_df = cds_df.copy()
    
    bonds_df['year_month'] = bonds_df['date'].dt.to_period('M')
    cds_df['year_month'] = cds_df['date'].dt.to_period('M')
    
    # Rename bond date to avoid confusion
    bonds_df = bonds_df.rename(columns={'date': 'bond_date'})
    
    # Merge: CDS daily × bond monthly via ticker + year_month
    merged = cds_df.merge(
        bonds_df,
        left_on=['ticker', 'year_month'],
        right_on=['company_symbol', 'year_month'],
        how='inner'
    )
    
    print(f"Matching results:")
    print(f"  Matched observations: {len(merged):,}")
    print(f"  Unique bonds matched: {merged['cusip'].nunique():,}")
    print(f"  Unique CDS tickers:   {merged['ticker'].nunique():,}")
    print(f"  Date range:           {merged['date'].min()} to {merged['date'].max()}")
    
    # Check for unmatched bonds and CDS
    unmatched_bonds = bonds_df[~bonds_df['company_symbol'].isin(merged['company_symbol'])]
    unmatched_cds = cds_df[~cds_df['ticker'].isin(merged['ticker'])]
    
    print(f"\nUnmatched:")
    print(f"  Bond issuers without CDS: {unmatched_bonds['company_symbol'].nunique():,}")
    print(f"  CDS tickers without bonds: {unmatched_cds['ticker'].nunique():,}")
    
    return merged


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_pipeline():
    """Run the complete data preparation pipeline."""
    # Load data
    bond_prices, ratings, cds = load_all_data()
    
    # Filter bonds
    filtered_bonds = filter_bonds(bond_prices)
    qualified_bonds = add_ratings(filtered_bonds, ratings)
    
    # Save qualified bonds
    qualified_bonds.to_parquet(DATA_DIR / "qualified_bonds.parquet")
    print(f"\nSaved qualified bonds to {DATA_DIR / 'qualified_bonds.parquet'}")
    
    # Filter CDS
    filtered_cds = filter_cds(cds)
    
    # Match bonds to CDS
    matched = match_bonds_to_cds(qualified_bonds, filtered_cds)
    
    # Save matched data
    matched.to_parquet(DATA_DIR / "matched_bond_cds.parquet")
    print(f"\nSaved matched bond-CDS data to {DATA_DIR / 'matched_bond_cds.parquet'}")
    
    # Final summary
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    print(f"Qualified bonds:      {len(qualified_bonds):,} observations")
    print(f"                      {qualified_bonds['cusip'].nunique():,} unique bonds")
    print(f"                      {qualified_bonds['company_symbol'].nunique():,} unique issuers")
    print(f"\nFiltered CDS:         {len(filtered_cds):,} observations")
    print(f"                      {filtered_cds['ticker'].nunique():,} unique tickers")
    print(f"\nMatched bond-CDS:     {len(matched):,} observations")
    print(f"                      {matched['cusip'].nunique():,} unique bonds")
    print(f"                      {matched['ticker'].nunique():,} unique CDS names")
    print(f"\nFiles created:")
    print(f"  - qualified_bonds.parquet")
    print(f"  - matched_bond_cds.parquet")
    print(f"\nNext step: Run calc_PECDS.py to calculate PECDS and basis")


if __name__ == "__main__":
    run_pipeline()