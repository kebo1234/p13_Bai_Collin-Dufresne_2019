# src/filter_data.py
"""
Data preparation pipeline for Bai, Collin-Dufresne (2019) replication.

This script has:
    - Bond filtering
    - CDS filtering
    - Bond-CDS matching

Inputs:
    - bond_prices.parquet (from pull_bonds.py)
    - Mergent_FISD_ratings.parquet (from pull_LSEG_Mergent.py)
    - CDS.parquet (from pull_CDS.py)

Outputs:
    - qualified_bonds.parquet
    - matched_bond_cds.parquet
"""

from pathlib import Path
import pandas as pd

from settings import config

DATA_DIR = Path(config("DATA_DIR"))

START_DATE = config('START_DATE')
END_DATE = config('SAMPLE_END_DATE')

def load_all_data():
    """Load bond prices, ratings, and CDS data."""
    bond_prices = pd.read_parquet(DATA_DIR / "bond_prices.parquet")
    ratings = pd.read_parquet(DATA_DIR / "Mergent_FISD_ratings.parquet")
    cds = pd.read_parquet(DATA_DIR / "CDS.parquet")
    
    return bond_prices, ratings, cds

def filter_bonds(bond_prices):
    """
    Filters bonds according to Section 3.1 of paper.

    Most of the filtering outlined in (3.1) is already handled by WRDS Bond Returns; bonds in our dataset are:
        - listed/traded in US public markets
        - NOT structured notes, mortgage backed, or asset backed
        - NOT agency-backed or equity-linked
        - NOT floating-rate bonds (sample consists of only fixed- or zero-coupon bonds)
        - NOT when-issued bonds
        - NOT locked-in bonds
        - NOT bonds with commission trading, special prices, or special sales conditions
        - NOT bonds w/ transaction records that are cancelled, and adjust records that are subsequently corrected or reversed
        - NOT bond trades with more than two-day settlements

    So, we simply need to filter:
        1. Sample period: July 2006 - December 2014
        2. Remove convertible bonds
        3. Time-to-maturity: 3 to 7.5 years
        4. Remove bonds with missing prices or yields
        5. Remove bonds with missing company symbol
    """
    df = bond_prices.copy()
    print(f"Starting with {len(df):,} observations")
    
    # Filter 1: Sample period
    df = df[(df['date'] >= START_DATE) & (df['date'] <= END_DATE)]
    print(f"After date filter ({START_DATE} to {END_DATE}): {len(df):,}")
    
    # Filter 2: Remove convertible bonds
    df = df[df['conv'] == 0]
    print(f"After removing convertible bonds: {len(df):,}")
    
    # Filter 3: Time-to-maturity between 3 and 7.5 years
    df = df[(df["tmt"] >= 3.0) & (df["tmt"] <= 7.5)]
    print(f"After filtering for TTM of 3 to 7.5 years: {len(df):,}")
    
    # Filter 4: Remove bonds with missing prices or yields
    df = df[df['price_eom'].notna() & df['yield'].notna()]
    print(f"After removing missing prices/yields: {len(df):,}")
    
    # Filter 5: Remove bonds with missing company symbol
    df = df[df['company_symbol'].notna()]
    print(f"After removing missing company symbol: {len(df):,}")
    
    # Filter 6: Keep only rated bonds
    # df = df[df['rating_class'].notna()]
    # print(f"After removing unrated bonds: {len(df):,}")
    
    # # Filter 7: Keep only corporate bond types
    # corporate_bond_types = ['CDEB', 'CMTN', 'CMTZ', 'CZ', 'USBN']
    # df = df[df['bond_type'].isin(corporate_bond_types)]
    # print(f"After keeping only corporate bond types: {len(df):,}")
    
    return df

def add_ratings(bond_df, ratings_df):
    """
    Add Mergent FISD ratings to bond data.
    
    Per the paper:
    - If rated by both Moody's and S&P, take average
    - If rated by only one agency, use that rating
    """
    # Get most recent S&P rating per bond
    sp = ratings_df[ratings_df['rating_type'] == 'SPR'].copy()
    sp = sp.sort_values(['issue_id', 'rating_date']).groupby('issue_id').last()
    sp = sp[['rating', 'investment_grade']].rename(columns={'rating': 'sp_rating', 'investment_grade': 'sp_ig'})
    
    # Get most recent Moody's rating per bond
    moodys = ratings_df[ratings_df['rating_type'] == 'MR'].copy()
    moodys = moodys.sort_values(['issue_id', 'rating_date']).groupby('issue_id').last()
    moodys = moodys[['rating', 'investment_grade']].rename(columns={'rating': 'moodys_rating', 'investment_grade': 'moodys_ig'})
    
    # Merge ratings
    df = bond_df.merge(sp, on='issue_id', how='left')
    df = df.merge(moodys, on='issue_id', how='left')
    
    return df


def filter_cds(cds_df):
    """
    Filter CDS data per paper's criteria:
        - USD only
        - 5-year tenor (most liquid)
        - Sample period
    
    Note: Paper uses MR (Modified Restructuring) clause, but our data
    only contains XR14 and XR. We skip docclause filtering to keep all data.
    """
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
    
    return df


def match_bonds_to_cds(bonds_df, cds_df):
    """
    Match bonds to CDS entities via company_symbol = ticker.
    
    Monthly bond data is matched to daily CDS data by:
        - Matching on company_symbol (bond) = ticker (CDS)
        - For each day in a month, using that month's bond data
    """
    bonds_df = bonds_df.copy()
    cds_df = cds_df.copy()

    # Add year-month for merging
    bonds_df['year_month'] = bonds_df['date'].dt.to_period('M')
    cds_df['year_month'] = cds_df['date'].dt.to_period('M')
    
    # Rename bond date col to avoid confusion in merge
    bonds_df = bonds_df.rename(columns={'date': 'bond_date'})
    
    # Merge: CDS daily w/ bond monthly via ticker + year_month
    merged = cds_df.merge(bonds_df, left_on=['ticker', 'year_month'], right_on=['company_symbol', 'year_month'], how='inner')
    
    print(f"Matched observations: {len(merged):,}")
    
    return merged

if __name__ == "__main__":
    bond_prices, ratings, cds = load_all_data()
    
    filtered_bonds = filter_bonds(bond_prices)
    qualified_bonds = add_ratings(filtered_bonds, ratings)
    qualified_bonds.to_parquet(DATA_DIR / "qualified_bonds.parquet")
    
    filtered_cds = filter_cds(cds)
    
    matched = match_bonds_to_cds(qualified_bonds, filtered_cds)
    matched.to_parquet(DATA_DIR / "matched_bond_cds.parquet")