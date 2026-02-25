"""
Replicate Table 1 from Bai, Collin-Dufresne (2019).

Summary statistics of CDS-bond basis across four crisis phases and 
different bond categories (rating, financial vs non-financial).

Input: basis.parquet
Output: 
    - _output/table1_replication.tex
    - _output/table1_replication.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

from settings import config

DATA_DIR = Path(config("DATA_DIR"))
OUTPUT_DIR = Path("_output")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():
    """Load basis data."""
    basis_path = DATA_DIR / "basis.parquet"
    df = pd.read_parquet(basis_path)
    
    print(f"Loaded {len(df):,} observations from :{df['date'].min()} to {df['date'].max()}")    
    return df


def add_crisis_phases(df):
    """Add crisis phase indicators."""
    df = df.copy()
    
    df['phase'] = 'Unknown'
    df.loc[df['date'] < '2007-07-01', 'phase'] = 'Before Crisis'
    df.loc[(df['date'] >= '2007-07-01') & (df['date'] < '2008-09-01'), 'phase'] = 'Crisis I'
    df.loc[(df['date'] >= '2008-09-01') & (df['date'] < '2009-10-01'), 'phase'] = 'Crisis II'
    df.loc[df['date'] >= '2009-10-01', 'phase'] = 'Post-crisis'
    df.loc[df['date'] >= '2015-01-01', 'phase'] = 'Extended'
    
    return df


def classify_rating(row):
    """Classify bonds into rating buckets matching the paper."""
    # Use S&P rating if available, otherwise Moody's
    rating = row['sp_rating'] if pd.notna(row['sp_rating']) else row['moodys_rating']
    
    if pd.isna(rating):
        return 'Unrated'
    
    rating = str(rating).upper()
    
    # AAA/AA bucket
    if rating.startswith('AAA') or rating.startswith('AA'):
        return 'AAA/AA'
    # A bucket
    elif rating.startswith('A') and not rating.startswith('AA'):
        return 'A'
    # BBB bucket
    elif rating.startswith('BBB') or rating.startswith('BAA'):
        return 'BBB'
    # BB bucket
    elif rating.startswith('BB') or rating.startswith('BA'):
        return 'BB'
    # B bucket (but not BB or BBB)
    elif rating.startswith('B') and not rating.startswith('BB') and not rating.startswith('BA'):
        return 'B'
    # CCC and below
    elif rating.startswith('CCC') or rating.startswith('CC') or rating.startswith('C'):
        return 'CCC'
    else:
        return 'Unrated'


def classify_financial(row):
    """
    Classify bonds as Financial (F) or Non-Financial (NF).
    
    Note: This requires SIC codes. If not available in data, 
    we'll need to add this information.
    """
    # TODO: Add SIC code logic when available
    # Financial firms typically have SIC codes 6000-6999
    # For now, return None
    return None


def calculate_daily_statistics(df, group_col=None):
    """
    Calculate cross-sectional statistics for each day, then time-series average.
    
    Per the paper: "We calculate the cross-sectional mean, standard deviation, 
    the 10th and the 90th percentile value of the bases across all bonds each day, 
    and report the time-series average of these statistics."
    """
    if group_col:
        # Group by date and category
        daily_stats = df.groupby(['date', group_col])['basis_bps'].agg([
            ('mean', 'mean'),
            ('sd', 'std'),
            ('p10', lambda x: x.quantile(0.10)),
            ('p90', lambda x: x.quantile(0.90))
        ]).reset_index()
        
        # Then take time-series average for each category
        result = daily_stats.groupby(group_col)[['mean', 'sd', 'p10', 'p90']].mean()
    else:
        # Just by date (for ALL category)
        daily_stats = df.groupby('date')['basis_bps'].agg([
            ('mean', 'mean'),
            ('sd', 'std'),
            ('p10', lambda x: x.quantile(0.10)),
            ('p90', lambda x: x.quantile(0.90))
        ])
        
        # Time-series average
        result = daily_stats.mean().to_frame().T
        result.index = ['ALL']
    
    return result


def create_table1(basis_df):
    """
    Create Table 1 following the paper's exact methodology.
    
    For each phase and category:
    1. Calculate daily cross-sectional statistics (mean, SD, P10, P90)
    2. Take time-series average of these daily statistics
    """  
    # Add classifications
    basis_df['rating_bucket'] = basis_df.apply(classify_rating, axis=1)
    basis_df['is_investment_grade'] = basis_df['rating_class'].str.contains('IG', na=False)
    
    # Define phases
    phases = ['Before Crisis', 'Crisis I', 'Crisis II', 'Post-crisis']
    
    # Categories to analyze
    categories = {
        'ALL': basis_df,
        'IG': basis_df[basis_df['is_investment_grade'] == True],
        'HY': basis_df[basis_df['is_investment_grade'] == False],
        # F and NF would require SIC codes - skip for now
        # 'F': basis_df[basis_df['is_financial'] == True],
        # 'NF': basis_df[basis_df['is_financial'] == False],
        'AAA/AA': basis_df[basis_df['rating_bucket'] == 'AAA/AA'],
        'A': basis_df[basis_df['rating_bucket'] == 'A'],
        'BBB': basis_df[basis_df['rating_bucket'] == 'BBB'],
        'BB': basis_df[basis_df['rating_bucket'] == 'BB'],
        'B': basis_df[basis_df['rating_bucket'] == 'B'],
        'CCC': basis_df[basis_df['rating_bucket'] == 'CCC']
    }
    # Build results table
    results = []
    
    for cat_name, cat_df in categories.items():
        row = {'Category': cat_name}
        
        for phase in phases:
            # Filter to this phase
            phase_df = cat_df[cat_df['phase'] == phase]
            
            if len(phase_df) > 0:
                # Calculate daily cross-sectional statistics
                daily_stats = phase_df.groupby('date')['basis_bps'].agg([
                    ('mean', 'mean'),
                    ('sd', 'std'),
                    ('p10', lambda x: x.quantile(0.10)),
                    ('p90', lambda x: x.quantile(0.90))
                ])
                
                # Time-series average of daily statistics
                ts_avg = daily_stats.mean()
                
                row[f'{phase}_Mean'] = int(round(ts_avg['mean']))
                row[f'{phase}_SD'] = int(round(ts_avg['sd']))
                row[f'{phase}_P10'] = int(round(ts_avg['p10']))
                row[f'{phase}_P90'] = int(round(ts_avg['p90']))
            else:
                row[f'{phase}_Mean'] = None
                row[f'{phase}_SD'] = None
                row[f'{phase}_P10'] = None
                row[f'{phase}_P90'] = None
        
        results.append(row)
    
    # Create DataFrame
    table1 = pd.DataFrame(results)
    
    # Reorder columns to match paper format
    col_order = ['Category']
    for phase in phases:
        col_order.extend([f'{phase}_Mean', f'{phase}_SD', f'{phase}_P10', f'{phase}_P90'])
    
    table1 = table1[col_order]
    
    return table1


def export_to_latex(table1, filename="table1_replication.tex"):
    """Export Table 1 to LaTeX format matching the paper's style."""
    
    # Get date range for Extended period
    # (will be shown in column header)
    
    # Create multi-level column headers for LaTeX
    latex_str = r"""\begin{table}[htbp]
\centering
\caption{Summary statistics of discrepancies in CDS and cash bond spreads}
\label{tab:table1}
\small
\begin{tabular}{l rrrr rrrr rrrr rrrr rrrr}
\hline\hline
& \multicolumn{4}{c}{Before Crisis} & \multicolumn{4}{c}{Crisis I} & \multicolumn{4}{c}{Crisis II} & \multicolumn{4}{c}{Post-crisis} & \multicolumn{4}{c}{Extended} \\
\cline{2-5} \cline{6-9} \cline{10-13} \cline{14-17} \cline{18-21}
& \multicolumn{4}{c}{July 2006--June 2007} & \multicolumn{4}{c}{July 2007--Aug. 2008} & \multicolumn{4}{c}{Sept. 2008--Sept. 2009} & \multicolumn{4}{c}{Oct. 2009--Dec. 2014} & \multicolumn{4}{c}{Jan. 2015--Present} \\
\cline{2-5} \cline{6-9} \cline{10-13} \cline{14-17} \cline{18-21}
& Mean & SD & P10 & P90 & Mean & SD & P10 & P90 & Mean & SD & P10 & P90 & Mean & SD & P10 & P90 & Mean & SD & P10 & P90 \\
\hline
"""
    
    # Add data rows
    for _, row in table1.iterrows():
        cat = row['Category']
        latex_str += f"{cat}"
        
        for phase in ['Before Crisis', 'Crisis I', 'Crisis II', 'Post-crisis', 'Extended']:
            mean = row[f'{phase}_Mean']
            sd = row[f'{phase}_SD']
            p10 = row[f'{phase}_P10']
            p90 = row[f'{phase}_P90']
            
            # Format as integers or -- for missing
            mean_str = f"{mean:d}" if pd.notna(mean) else "--"
            sd_str = f"{sd:d}" if pd.notna(sd) else "--"
            p10_str = f"{p10:d}" if pd.notna(p10) else "--"
            p90_str = f"{p90:d}" if pd.notna(p90) else "--"
            
            latex_str += f" & {mean_str} & {sd_str} & {p10_str} & {p90_str}"
        
        latex_str += " \\\\\n"
    
    # Close table
    latex_str += r"""\hline\hline
\end{tabular}
\begin{flushleft}
\footnotesize
\textit{Notes:} This table provides the descriptive statistics for the average CDS-bond basis across five periods. Phase 1 is the period prior to the subprime credit crisis, ``Before Crisis'' (July 2006--June 2007), Phase 2 is the period between the subprime credit crisis and the bankruptcy of Lehman Brothers, ``Crisis I'' (July 2007--August 2008), Phase 3 is the period after Lehman Brothers' failure, ``Crisis II'' (September 2008--September 2009), Phase 4 is the period after the financial crisis, ``Post-crisis'' (October 2009--December 2014), and Phase 5 is the extended period, ``Extended'' (January 2015--Present). The basis is calculated as the difference between the CDS spread and the par equivalent corporate bond spread using the methodology in the Appendix. The summary statistics are reported for all bonds (ALL), investment-grade bonds (IG), high-yield bonds (HY), as well as across rating categories: AAA/AA, A, BBB, BB, B, and CCC. We calculate the cross-sectional mean, standard deviation, the 10th and the 90th percentile value of the bases across all bonds each day, and report the time-series average of these statistics. All entries are in basis points.
\end{flushleft}
\end{table}
"""
    
    # Save
    output_path = OUTPUT_DIR / filename
    with open(output_path, 'w') as f:
        f.write(latex_str)
    
    print(f"Saved LaTeX table to {output_path}")


def print_comparison_with_paper(table1):
    """Compare our results with the paper's published Table 1."""
    print("\n" + "="*80)
    print("COMPARISON WITH PAPER")
    print("="*80)
    
    # Paper's results
    paper = {
        'ALL': {'Before Crisis': (-10, 59, -57, 45), 'Crisis I': (-118, 192, -273, 14), 
                'Crisis II': (-324, 369, -667, -55), 'Post-crisis': (-137, 152, -268, -32)},
        'IG': {'Before Crisis': (-17, 30, -51, 17), 'Crisis I': (-83, 108, -150, -10),
               'Crisis II': (-243, 256, -451, -48), 'Post-crisis': (-101, 71, -173, -32)},
        'HY': {'Before Crisis': (12, 104, -107, 142), 'Crisis I': (-180, 265, -486, 57),
               'Crisis II': (-560, 504, -1248, -114), 'Post-crisis': (-237, 242, -477, -35)},
    }
    
    for cat in ['ALL', 'IG', 'HY']:
        print(f"\n{cat}:")
        for phase in ['Before Crisis', 'Crisis I', 'Crisis II', 'Post-crisis']:
            our_mean = table1[table1['Category'] == cat][f'{phase}_Mean'].values[0]
            paper_vals = paper[cat][phase]
            
            diff = our_mean - paper_vals[0] if pd.notna(our_mean) else None
            
            print(f"  {phase:15s}: Our Mean={our_mean:6.0f}  " +
                  f"Paper Mean={paper_vals[0]:6d}  Diff={diff:6.0f}" if diff else "  Missing")


if __name__ == "__main__":
    print("="*80)
    print("REPLICATING TABLE 1")
    print("="*80)
    
    # Load data
    basis = load_data()
    
    # Add crisis phases if not present
    if 'phase' not in basis.columns:
        basis = add_crisis_phases(basis)
    
    # Create Table 1
    table1 = create_table1(basis)
    
    # Display
    print("\nTable 1:")
    print(table1.to_string(index=False))
    
    # Export to LaTeX
    export_to_latex(table1)
    
    # Also save as CSV
    table1.to_csv(OUTPUT_DIR / "table1_replication.csv", index=False)
    print(f"Saved CSV to {OUTPUT_DIR / 'table1_replication.csv'}")
    
    # Compare with paper
    print_comparison_with_paper(table1)

