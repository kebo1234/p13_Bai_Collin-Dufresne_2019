"""
This module pulls and saves bond ratings data from LSEG (formerly Thomson Reuters)
and Mergent FISD (Fixed Income Securities Database).

The Mergent FISD database contains comprehensive information on publicly offered
U.S. corporate bonds, including:
- Bond characteristics (issue date, maturity, coupon, etc.)
- Credit ratings from major agencies (S&P, Moody's, Fitch)
- Issuer information

LSEG Datastream provides additional bond market data and can supplement FISD data.

For information about Mergent FISD variables, see:
https://wrds-www.wharton.upenn.edu/documents/1364/Mergent_FISD_Manual.pdf

Useful WRDS support pages:
- Mergent FISD Overview: https://wrds-www.wharton.upenn.edu/pages/get-data/mergent-fixed-income-securities-database-fisd/
- LSEG Datastream: https://wrds-www.wharton.upenn.edu/pages/get-data/lseg-datastream/

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
    "issuer_cusip": "Issuer CUSIP - 6-character issuer identifier (first 6 digits of CUSIP)",
    "issue_id": "Issue ID - Unique identifier for the bond issue in FISD",
    "issuer_id": "Issuer ID - Unique identifier for the issuer in FISD",
    "prospectus_issuer_name": "Issuer Name - Name of the issuing company",
    "offering_date": "Offering Date - Date when the bond was first offered",
    "dated_date": "Dated Date - Date from which interest starts accruing",
    "maturity": "Maturity Date - Date when the bond matures",
    "offering_amt": "Offering Amount - Original principal amount of the issue (in thousands)",
    "offering_price": "Offering Price - Original offering price (as percentage of par)",
    "coupon": "Coupon Rate - Annual coupon rate (as percentage)",
    "coupon_type": "Coupon Type - Type of coupon (e.g., Fixed, Variable)",
    "interest_frequency": "Interest Payment Frequency - Number of coupon payments per year",
    "day_count_basis": "Day Count Basis - Convention for calculating accrued interest",
    "callable": "Callable Flag - Whether the bond is callable",
    "putable": "Putable Flag - Whether the bond is putable",
    "convertible": "Convertible Flag - Whether the bond is convertible",
    "security_level": "Security Level - Seniority level of the bond",
    "security_pledge": "Security Pledge - Type of collateral/security",
    "bond_type": "Bond Type - Classification of bond type",
    "private_placement": "Private Placement Flag - Whether privately placed",
    "defaulted": "Defaulted Flag - Whether the bond has defaulted",
    "settlement": "Settlement Type - Settlement convention",
}


description_mergent_fisd_ratings = {
    "complete_cusip": "Complete CUSIP - 9-character CUSIP identifier",
    "issue_id": "Issue ID - Unique identifier for the bond issue",
    "rating_date": "Rating Date - Date of the rating",
    "rating_type": "Rating Type - Type of rating (e.g., SPR for S&P, MR for Moody's, FR for Fitch)",
    "rating": "Rating - The credit rating assigned",
    "investment_grade": "Investment Grade Flag - Whether the rating is investment grade",
    "rating_status": "Rating Status - Status of the rating (e.g., Current, Withdrawn)",
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
            complete_cusip, issuer_cusip, issue_id, issuer_id,
            prospectus_issuer_name, offering_date, dated_date, maturity,
            offering_amt, offering_price, coupon, coupon_type,
            interest_frequency, day_count_basis,
            callable, putable, convertible,
            security_level, security_pledge, bond_type,
            private_placement, defaulted, settlement
        FROM 
            fisd.fisd_mergedissue
        WHERE 
            offering_date >= '{start_date}'
        """
    
    db = wrds.Connection(wrds_username=wrds_username)
    fisd_issue = db.raw_sql(
        sql_query, 
        date_cols=["offering_date", "dated_date", "maturity"]
    )
    db.close()
    
    return fisd_issue


def pull_mergent_fisd_ratings(wrds_username=WRDS_USERNAME, start_date="01/01/1990"):
    """
    Pull bond ratings history from Mergent FISD.
    
    This includes ratings from:
    - S&P (SPR - S&P Rating)
    - Moody's (MR - Moody's Rating)
    - Fitch (FR - Fitch Rating)
    
    Parameters
    ----------
    wrds_username : str
        WRDS username for database connection
    start_date : str
        Starting date for data pull (format: 'MM/DD/YYYY')
    
    Returns
    -------
    pd.DataFrame
        DataFrame containing bond ratings history
    """
    sql_query = f"""
        SELECT 
            complete_cusip, issue_id, rating_date,
            rating_type, rating, investment_grade, rating_status
        FROM 
            fisd.fisd_mergedratings
        WHERE 
            rating_date >= '{start_date}'
        ORDER BY 
            complete_cusip, rating_date
        """
    
    db = wrds.Connection(wrds_username=wrds_username)
    fisd_ratings = db.raw_sql(sql_query, date_cols=["rating_date"])
    db.close()
    
    return fisd_ratings


def pull_mergent_fisd_ratings_current(wrds_username=WRDS_USERNAME):
    """
    Pull current (most recent) bond ratings from Mergent FISD.
    
    This is useful for getting the latest rating for each bond without
    the full history.
    
    Parameters
    ----------
    wrds_username : str
        WRDS username for database connection
    
    Returns
    -------
    pd.DataFrame
        DataFrame containing current bond ratings
    """
    sql_query = """
        SELECT 
            complete_cusip, issue_id, rating_date,
            rating_type, rating, investment_grade, rating_status
        FROM 
            fisd.fisd_mergedratings
        WHERE 
            rating_status = 'Current'
        """
    
    db = wrds.Connection(wrds_username=wrds_username)
    fisd_ratings_current = db.raw_sql(sql_query, date_cols=["rating_date"])
    db.close()
    
    return fisd_ratings_current


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


def process_ratings_to_monthly(ratings_df, rating_type='SPR'):
    """
    Convert ratings history to monthly panel data.
    
    For each bond-month, assigns the most recent rating as of that month-end.
    
    Parameters
    ----------
    ratings_df : pd.DataFrame
        DataFrame from pull_mergent_fisd_ratings
    rating_type : str
        Rating type to filter ('SPR', 'MR', or 'FR')
    
    Returns
    -------
    pd.DataFrame
        Monthly panel with columns: complete_cusip, month_end, rating, rating_numeric
    """
    # Filter to specific rating type
    df = ratings_df[ratings_df['rating_type'] == rating_type].copy()
    
    # Add month-end date
    df['month_end'] = df['rating_date'] + MonthEnd(0)
    
    # Sort by CUSIP and date
    df = df.sort_values(['complete_cusip', 'rating_date'])
    
    # For each month, keep the last rating observation
    df = df.drop_duplicates(['complete_cusip', 'month_end'], keep='last')
    
    # Add numeric rating
    if rating_type == 'SPR':
        df['rating_numeric'] = df['rating'].apply(get_sp_rating_numeric)
    elif rating_type == 'MR':
        df['rating_numeric'] = df['rating'].apply(get_moodys_rating_numeric)
    
    return df[['complete_cusip', 'month_end', 'rating', 'rating_numeric', 'investment_grade']]


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


def load_mergent_fisd_ratings_current(data_dir=DATA_DIR):
    """Load saved Mergent FISD current ratings data."""
    path = Path(data_dir) / "Mergent_FISD_ratings_current.parquet"
    fisd_ratings_current = pd.read_parquet(path)
    return fisd_ratings_current


def _demo():
    """Demonstrate loading the saved data."""
    fisd_issue = load_mergent_fisd_issue(data_dir=DATA_DIR)
    fisd_ratings = load_mergent_fisd_ratings(data_dir=DATA_DIR)
    fisd_ratings_current = load_mergent_fisd_ratings_current(data_dir=DATA_DIR)
   
    
    # Show example of processing ratings to monthly
    if len(fisd_ratings) > 0:
        monthly_sp = process_ratings_to_monthly(fisd_ratings, rating_type='SPR')
    # is this necessary?


if __name__ == "__main__":
    # Pull and save Mergent FISD issue data
    fisd_issue = pull_mergent_fisd_issue(wrds_username=WRDS_USERNAME)
    fisd_issue.to_parquet(DATA_DIR / "Mergent_FISD_issue.parquet")
    
    # Pull and save Mergent FISD ratings history
    print("\nPulling Mergent FISD ratings history...")
    fisd_ratings = pull_mergent_fisd_ratings(wrds_username=WRDS_USERNAME)
    fisd_ratings.to_parquet(DATA_DIR / "Mergent_FISD_ratings.parquet")
    
    # Pull and save current ratings
    fisd_ratings_current = pull_mergent_fisd_ratings_current(wrds_username=WRDS_USERNAME)
    fisd_ratings_current.to_parquet(DATA_DIR / "Mergent_FISD_ratings_current.parquet")
    