"""
This module pulls and saves bond ratings data from Mergent FISD 
(Fixed Income Securities Database).

The Mergent FISD database contains comprehensive information on publicly offered
U.S. corporate bonds, including:
- Bond characteristics (issue date, maturity, coupon, etc.)
- Credit ratings from major agencies (S&P, Moody's, Fitch)
- Issuer information

For information about Mergent FISD variables, see:
https://wrds-www.wharton.upenn.edu/documents/1364/Mergent_FISD_Manual.pdf

"""

from pathlib import Path

import pandas as pd
import wrds
from pandas.tseries.offsets import MonthEnd

from settings import config

OUTPUT_DIR = Path(config("OUTPUT_DIR"))
DATA_DIR = Path(config("DATA_DIR"))
WRDS_USERNAME = config("WRDS_USERNAME")


description_mergent_fisd_issue = {
    "complete_cusip": "Complete CUSIP - 9-character CUSIP identifier",
    "issuer_cusip": "Issuer CUSIP - 6-character issuer identifier",
    "issue_id": "Issue ID - Unique identifier for the bond issue in FISD",
    "issuer_id": "Issuer ID - Unique identifier for the issuer in FISD",
    "prospectus_issuer_name": "Issuer Name - Name of the issuing company",
    "offering_date": "Offering Date - Date when the bond was first offered",
    "maturity": "Maturity Date - Date when the bond matures",
}


description_mergent_fisd_ratings = {
    "issue_id": "Issue ID - Unique identifier for the bond issue",
    "rating_type": "Rating Type - Type of rating (SPR=S&P, MR=Moody's, FR=Fitch)",
    "rating_date": "Rating Date - Date of the rating",
    "rating": "Rating - The credit rating assigned",
    "rating_status": "Rating Status - Status of the rating",
    "investment_grade": "Investment Grade Flag - Whether rating is investment grade",
}


def pull_mergent_fisd_issue(wrds_username=WRDS_USERNAME, start_date="01/01/1990"):
    """
    Pull bond issue information from Mergent FISD.
    
    Parameters
    ----------
    wrds_username : str
        WRDS username for database connection
    start_date : str
        Starting date for data pull (format: 'MM/DD/YYYY')
    
    Returns
    -------
    pd.DataFrame
        DataFrame containing bond issue characteristics
    """
    sql_query = f"""
        SELECT 
            issue_id, issuer_id, complete_cusip, issuer_cusip,
            prospectus_issuer_name, offering_date, maturity
        FROM 
            fisd.fisd_mergedissue
        WHERE 
            offering_date >= '{start_date}'
        """
    
    db = wrds.Connection(wrds_username=wrds_username)
    fisd_issue = db.raw_sql(
        sql_query, 
        date_cols=["offering_date", "maturity"]
    )
    db.close()
    
    return fisd_issue


def pull_mergent_fisd_ratings(wrds_username=WRDS_USERNAME, start_date="01/01/1990"):
    """
    Pull bond ratings from Mergent FISD.
    
    This includes ratings from:
    - S&P (rating_type = 'SPR')
    - Moody's (rating_type = 'MR')
    - Fitch (rating_type = 'FR')
    
    Parameters
    ----------
    wrds_username : str
        WRDS username for database connection
    start_date : str
        Starting date for data pull (format: 'MM/DD/YYYY')
    
    Returns
    -------
    pd.DataFrame
        DataFrame containing bond ratings
    """
    sql_query = f"""
        SELECT 
            issue_id, rating_type, rating_date, rating,
            rating_status, investment_grade
        FROM 
            fisd.fisd_ratings
        WHERE 
            rating_date >= '{start_date}'
        ORDER BY 
            issue_id, rating_date
        """
    
    db = wrds.Connection(wrds_username=wrds_username)
    fisd_ratings = db.raw_sql(sql_query, date_cols=["rating_date"])
    db.close()
    
    return fisd_ratings


def merge_issue_ratings(issue_df, ratings_df):
    """
    Merge issue and ratings data.
    
    Parameters
    ----------
    issue_df : pd.DataFrame
        DataFrame from pull_mergent_fisd_issue
    ratings_df : pd.DataFrame
        DataFrame from pull_mergent_fisd_ratings
    
    Returns
    -------
    pd.DataFrame
        Merged DataFrame with bond characteristics and ratings
    """
    merged = ratings_df.merge(issue_df, on='issue_id', how='left')
    return merged


def get_sp_rating_numeric(rating):
    """
    Convert S&P letter ratings to numeric scores.
    
    Higher numbers represent better credit quality.
    
    Parameters
    ----------
    rating : str
        S&P rating (e.g., 'AAA', 'BB+', 'D')
    
    Returns
    -------
    int
        Numeric score (1-22, or 0 for unrated/unknown)
    """
    if pd.isna(rating):
        return 0
    
    rating_map = {
        'AAA': 22, 'AA+': 21, 'AA': 20, 'AA-': 19,
        'A+': 18, 'A': 17, 'A-': 16,
        'BBB+': 15, 'BBB': 14, 'BBB-': 13,
        'BB+': 12, 'BB': 11, 'BB-': 10,
        'B+': 9, 'B': 8, 'B-': 7,
        'CCC+': 6, 'CCC': 5, 'CCC-': 4,
        'CC': 3, 'C': 2, 'D': 1
    }
    return rating_map.get(rating, 0)


def get_moodys_rating_numeric(rating):
    """
    Convert Moody's letter ratings to numeric scores.
    
    Higher numbers represent better credit quality.
    
    Parameters
    ----------
    rating : str
        Moody's rating (e.g., 'Aaa', 'Ba1', 'C')
    
    Returns
    -------
    int
        Numeric score (1-21, or 0 for unrated/unknown)
    """
    if pd.isna(rating):
        return 0
    
    rating_map = {
        'Aaa': 21, 'Aa1': 20, 'Aa2': 19, 'Aa3': 18,
        'A1': 17, 'A2': 16, 'A3': 15,
        'Baa1': 14, 'Baa2': 13, 'Baa3': 12,
        'Ba1': 11, 'Ba2': 10, 'Ba3': 9,
        'B1': 8, 'B2': 7, 'B3': 6,
        'Caa1': 5, 'Caa2': 4, 'Caa3': 3,
        'Ca': 2, 'C': 1
    }
    return rating_map.get(rating, 0)


def filter_sp_ratings(ratings_df):
    """
    Filter to S&P ratings only and add numeric rating.
    
    Parameters
    ----------
    ratings_df : pd.DataFrame
        DataFrame with ratings
    
    Returns
    -------
    pd.DataFrame
        Filtered to S&P ratings with numeric score added
    """
    sp = ratings_df[ratings_df['rating_type'] == 'SPR'].copy()
    sp['rating_numeric'] = sp['rating'].apply(get_sp_rating_numeric)
    return sp


def filter_moodys_ratings(ratings_df):
    """
    Filter to Moody's ratings only and add numeric rating.
    
    Parameters
    ----------
    ratings_df : pd.DataFrame
        DataFrame with ratings
    
    Returns
    -------
    pd.DataFrame
        Filtered to Moody's ratings with numeric score added
    """
    moodys = ratings_df[ratings_df['rating_type'] == 'MR'].copy()
    moodys['rating_numeric'] = moodys['rating'].apply(get_moodys_rating_numeric)
    return moodys


def process_ratings_to_monthly(ratings_df, rating_type='SPR'):
    """
    Convert ratings to monthly panel format.
    
    For each bond-month, assigns the most recent rating as of that month-end.
    
    Parameters
    ----------
    ratings_df : pd.DataFrame
        DataFrame from pull_mergent_fisd_ratings (or merged data)
    rating_type : str
        Rating type to filter ('SPR' for S&P, 'MR' for Moody's, 'FR' for Fitch)
    
    Returns
    -------
    pd.DataFrame
        Monthly panel with columns: issue_id, month_end, rating, rating_numeric
    """
    # Filter to specific rating type
    df = ratings_df[ratings_df['rating_type'] == rating_type].copy()
    
    # Add month-end date
    df['month_end'] = df['rating_date'] + MonthEnd(0)
    
    # Sort by issue_id and date
    df = df.sort_values(['issue_id', 'rating_date'])
    
    # For each month, keep the last rating observation
    df = df.drop_duplicates(['issue_id', 'month_end'], keep='last')
    
    # Add numeric rating
    if rating_type == 'SPR':
        df['rating_numeric'] = df['rating'].apply(get_sp_rating_numeric)
    elif rating_type == 'MR':
        df['rating_numeric'] = df['rating'].apply(get_moodys_rating_numeric)
    
    cols = ['issue_id', 'month_end', 'rating', 'rating_numeric', 'investment_grade']
    
    # Include complete_cusip if available
    if 'complete_cusip' in df.columns:
        cols = ['issue_id', 'complete_cusip'] + cols[1:]
    
    return df[cols]


def load_mergent_fisd_issue(data_dir=DATA_DIR):
    """Load saved Mergent FISD issue data."""
    path = Path(data_dir) / "Mergent_FISD_issue.parquet"
    fisd_issue = pd.read_parquet(path)
    return fisd_issue


def load_mergent_fisd_ratings(data_dir=DATA_DIR):
    """Load saved Mergent FISD ratings data."""
    path = Path(data_dir) / "Mergent_FISD_ratings.parquet"
    fisd_ratings = pd.read_parquet(path)
    return fisd_ratings


def _demo():
    """Demonstrate loading and processing the saved data."""
    fisd_issue = load_mergent_fisd_issue(data_dir=DATA_DIR)
    fisd_ratings = load_mergent_fisd_ratings(data_dir=DATA_DIR)
    
    # Merge issue and ratings
    merged = merge_issue_ratings(fisd_issue, fisd_ratings)
    
    # Show example of S&P ratings
    sp_ratings = filter_sp_ratings(merged)

    # Show example of monthly panel
    monthly_sp = process_ratings_to_monthly(merged, rating_type='SPR')
    
if __name__ == "__main__":
    # Pull and save Mergent FISD issue data
    print("Pulling Mergent FISD issue data...")
    fisd_issue = pull_mergent_fisd_issue(wrds_username=WRDS_USERNAME)
    fisd_issue.to_parquet(DATA_DIR / "Mergent_FISD_issue.parquet")
    
    # Pull and save Mergent FISD ratings
    fisd_ratings = pull_mergent_fisd_ratings(wrds_username=WRDS_USERNAME)
    fisd_ratings.to_parquet(DATA_DIR / "Mergent_FISD_ratings.parquet")
    
    