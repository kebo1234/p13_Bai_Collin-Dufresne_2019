"""
Filter bonds according to Bai, Collin-Dufresne (2019) criteria.

Input: bond_prices.parquet (from WRDS Bond Returns)
Output: qualified_bonds.parquet

Filtering criteria from the paper:
1. Remove convertible bonds
2. Keep only fixed or zero coupon bonds (no floating)
3. Time-to-maturity: 3 to 7.5 years (to match 5-year CDS liquidity)
4. US public market bonds only
5. Investment grade and high yield (no unrated)

Sample period: July 1, 2006 to December 30, 2014
"""

from pathlib import Path
import pandas as pd

from settings import config

DATA_DIR = Path(config("DATA_DIR"))

START_DATE = "2006-07-01"
END_DATE = "2014-12-30"
MIN_TTM = 3.0
MAX_TTM = 7.5


def load_data():
    """Load bond prices and Mergent FISD ratings."""
    bond_prices = pd.read_parquet(DATA_DIR / "bond_prices.parquet")
    ratings = pd.read_parquet(DATA_DIR / "Mergent_FISD_ratings.parquet")
    
    print(f"Loaded {len(bond_prices):,} bond-month observations")
    print(f"Loaded {len(ratings):,} rating records")
    
    return bond_prices, ratings


def filter_bonds(bond_prices):
    """
    Apply paper's filtering criteria to bond prices data.
    
    Parameters
    ----------
    bond_prices : pd.DataFrame
        Raw bond prices from WRDS Bond Returns
    
    Returns
    -------
    pd.DataFrame
        Filtered bond data
    """
    df = bond_prices.copy()
    print(f"\nStarting with {len(df):,} bond-month observations")
    
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
    
    # Filter 5: Remove bonds with missing company symbol (needed for CDS matching)
    df = df[df['company_symbol'].notna()]
    print(f"After removing missing company symbol: {len(df):,}")
    
    # Filter 6: Keep only rated bonds (remove unrated)
    df = df[df['rating_class'].notna()]
    print(f"After removing unrated bonds: {len(df):,}")
    
    # Filter 7: Keep only corporate bond types
    # CDEB = Corporate Debenture, CMTN = Corporate MTN, 
    # CMTZ = Zero coupon MTN, CZ = Corporate Zero coupon
    corporate_bond_types = ['CDEB', 'CMTN', 'CMTZ', 'CZ', 'USBN']
    df = df[df['bond_type'].isin(corporate_bond_types)]
    print(f"After keeping only corporate bond types: {len(df):,}")
    
    print(f"\nFinal: {len(df):,} bond-month observations")
    print(f"Unique bonds:   {df['cusip'].nunique():,}")
    print(f"Unique issuers: {df['company_symbol'].nunique():,}")
    
    return df


def add_ratings(bond_df, ratings_df):
    """
    Add Mergent FISD ratings to bond data.
    
    Per the paper:
    - If rated by both Moody's and S&P, take average
    - If rated by only one agency, use that rating
    - bond_prices already has rating_class; this adds more granular S&P/Moody's info
    
    Parameters
    ----------
    bond_df : pd.DataFrame
        Filtered bond data
    ratings_df : pd.DataFrame
        Mergent FISD ratings
    
    Returns
    -------
    pd.DataFrame
        Bond data with S&P and Moody's ratings added
    """
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
    
    # Merge ratings in on issue_id
    df = bond_df.merge(sp, on='issue_id', how='left')
    df = df.merge(moodys, on='issue_id', how='left')
    
    print(f"\nRatings coverage:")
    print(f"  S&P only:     {(df['sp_rating'].notna() & df['moodys_rating'].isna()).sum():,}")
    print(f"  Moody's only: {(df['sp_rating'].isna() & df['moodys_rating'].notna()).sum():,}")
    print(f"  Both:         {(df['sp_rating'].notna() & df['moodys_rating'].notna()).sum():,}")
    print(f"  Neither:      {(df['sp_rating'].isna() & df['moodys_rating'].isna()).sum():,}")
    
    return df


def load_qualified_bonds(data_dir=DATA_DIR):
    """Load saved qualified bonds."""
    path = Path(data_dir) / "qualified_bonds.parquet"
    return pd.read_parquet(path)


if __name__ == "__main__":
    # Load data
    bond_prices, ratings = load_data()
    
    # Apply filters
    filtered_bonds = filter_bonds(bond_prices)
    
    # Add Mergent ratings
    qualified_bonds = add_ratings(filtered_bonds, ratings)
    
    # Save
    output_path = DATA_DIR / "qualified_bonds.parquet"
    qualified_bonds.to_parquet(output_path)
    print(f"\nSaved qualified bonds to {output_path}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total observations:  {len(qualified_bonds):,}")
    print(f"Unique bonds:        {qualified_bonds['cusip'].nunique():,}")
    print(f"Unique issuers:      {qualified_bonds['company_symbol'].nunique():,}")
    print(f"Date range:          {qualified_bonds['date'].min()} to {qualified_bonds['date'].max()}")
    print(f"\nRating class distribution:")
    print(qualified_bonds['rating_class'].value_counts())