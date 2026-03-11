# src/replicate_table1.py
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
OUTPUT_DIR = Path(config("OUTPUT_DIR"))
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
    
    # Ensure datetime
    df["date"] = pd.to_datetime(df["date"])

    df['phase'] = 'Unknown'
    df.loc[df['date'] < '2007-07-01', 'phase'] = 'Before Crisis'
    df.loc[(df['date'] >= '2007-07-01') & (df['date'] < '2008-09-01'), 'phase'] = 'Crisis I'
    df.loc[(df['date'] >= '2008-09-01') & (df['date'] < '2009-10-01'), 'phase'] = 'Crisis II'
    df.loc[(df['date'] >= '2009-10-01') & (df['date'] < '2015-01-01'), 'phase'] = 'Post-crisis'
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


def create_table1_replication(basis_df):
    """Create Table 1 for replication period only (matches paper exactly)"""
    basis_df['rating_bucket'] = basis_df.apply(classify_rating, axis=1)
    basis_df['is_investment_grade'] = basis_df['rating_class'].str.contains('IG', na=False)
    
    # Only replication phases (matching paper)
    phases = ['Before Crisis', 'Crisis I', 'Crisis II', 'Post-crisis']
    
    categories = {
        'ALL': basis_df,
        'IG': basis_df[basis_df['is_investment_grade'] == True],
        'HY': basis_df[basis_df['is_investment_grade'] == False],
        'AAA/AA': basis_df[basis_df['rating_bucket'] == 'AAA/AA'],
        'A': basis_df[basis_df['rating_bucket'] == 'A'],
        'BBB': basis_df[basis_df['rating_bucket'] == 'BBB'],
        'BB': basis_df[basis_df['rating_bucket'] == 'BB'],
        'B': basis_df[basis_df['rating_bucket'] == 'B'],
        'CCC': basis_df[basis_df['rating_bucket'] == 'CCC']
    }
    
    results = []
    for cat_name, cat_df in categories.items():
        row = {'Category': cat_name}
        
        for phase in phases:
            phase_df = cat_df[cat_df['phase'] == phase]
            
            if len(phase_df) > 0:
                daily_stats = phase_df.groupby('date')['basis_bps'].agg([
                    ('mean', 'mean'),
                    ('sd', 'std'),
                    ('p10', lambda x: x.quantile(0.10)),
                    ('p90', lambda x: x.quantile(0.90))
                ])
                
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
    
    table1 = pd.DataFrame(results)
    
    col_order = ['Category']
    for phase in phases:
        col_order.extend([f'{phase}_Mean', f'{phase}_SD', f'{phase}_P10', f'{phase}_P90'])
    
    return table1[col_order]


def create_table1_extension(basis_df):
    """Create extension table for 2015-present period"""
    basis_df['rating_bucket'] = basis_df.apply(classify_rating, axis=1)
    basis_df['is_investment_grade'] = basis_df['rating_class'].str.contains('IG', na=False)
    
    # Only extended phase
    phases = ['Extended']
    
    categories = {
        'ALL': basis_df,
        'IG': basis_df[basis_df['is_investment_grade'] == True],
        'HY': basis_df[basis_df['is_investment_grade'] == False],
        'AAA/AA': basis_df[basis_df['rating_bucket'] == 'AAA/AA'],
        'A': basis_df[basis_df['rating_bucket'] == 'A'],
        'BBB': basis_df[basis_df['rating_bucket'] == 'BBB'],
        'BB': basis_df[basis_df['rating_bucket'] == 'BB'],
        'B': basis_df[basis_df['rating_bucket'] == 'B'],
        'CCC': basis_df[basis_df['rating_bucket'] == 'CCC']
    }
    
    results = []
    for cat_name, cat_df in categories.items():
        row = {'Category': cat_name}
        
        phase_df = cat_df[cat_df['phase'] == 'Extended']
        
        if len(phase_df) > 0:
            daily_stats = phase_df.groupby('date')['basis_bps'].agg([
                ('mean', 'mean'),
                ('sd', 'std'),
                ('p10', lambda x: x.quantile(0.10)),
                ('p90', lambda x: x.quantile(0.90))
            ])
            
            ts_avg = daily_stats.mean()
            
            row['Mean'] = int(round(ts_avg['mean']))
            row['SD'] = int(round(ts_avg['sd']))
            row['P10'] = int(round(ts_avg['p10']))
            row['P90'] = int(round(ts_avg['p90']))
        else:
            row['Mean'] = None
            row['SD'] = None
            row['P10'] = None
            row['P90'] = None
        
        results.append(row)
    
    return pd.DataFrame(results)

def export_to_latex_replication(table1, filename="table1_replication.tex"):
    """Export Table 1 (replication period only) to LaTeX format"""
    
    latex_str = r"""\begin{table}[htbp]
\centering
\caption{Summary statistics of discrepancies in CDS and cash bond spreads (Replication Period)}
\label{tab:table1_replication}
\small
\begin{tabular}{l rrrr rrrr rrrr rrrr}
\hline\hline
& \multicolumn{4}{c}{Before Crisis} & \multicolumn{4}{c}{Crisis I} & \multicolumn{4}{c}{Crisis II} & \multicolumn{4}{c}{Post-crisis} \\
\cline{2-5} \cline{6-9} \cline{10-13} \cline{14-17}
& \multicolumn{4}{c}{July 2006--June 2007} & \multicolumn{4}{c}{July 2007--Aug. 2008} & \multicolumn{4}{c}{Sept. 2008--Sept. 2009} & \multicolumn{4}{c}{Oct. 2009--Dec. 2014} \\
\cline{2-5} \cline{6-9} \cline{10-13} \cline{14-17}
& Mean & SD & P10 & P90 & Mean & SD & P10 & P90 & Mean & SD & P10 & P90 & Mean & SD & P10 & P90 \\
\hline
"""
    
    # Add data rows
    for _, row in table1.iterrows():
        cat = row['Category']
        latex_str += f"{cat}"
        
        for phase in ['Before Crisis', 'Crisis I', 'Crisis II', 'Post-crisis']:
            mean = row[f'{phase}_Mean']
            sd = row[f'{phase}_SD']
            p10 = row[f'{phase}_P10']
            p90 = row[f'{phase}_P90']
            
            mean_str = f"{mean:d}" if pd.notna(mean) else "--"
            sd_str = f"{sd:d}" if pd.notna(sd) else "--"
            p10_str = f"{p10:d}" if pd.notna(p10) else "--"
            p90_str = f"{p90:d}" if pd.notna(p90) else "--"
            
            latex_str += f" & {mean_str} & {sd_str} & {p10_str} & {p90_str}"
        
        latex_str += " \\\\\n"
    
    latex_str += r"""\hline\hline
\end{tabular}
\begin{flushleft}
\footnotesize
\textit{Notes:} This table replicates Table 1 from Bai and Collin-Dufresne (2019), showing descriptive statistics for the average CDS-bond basis across four crisis phases. All entries are in basis points.
\end{flushleft}
\end{table}
"""
    
    output_path = OUTPUT_DIR / filename
    with open(output_path, 'w') as f:
        f.write(latex_str)
    print(f"Saved LaTeX table to {output_path}")


def export_to_latex_extension(table1, filename="table1_extension.tex"):
    """Export Table 1 extension (2015-present) to LaTeX format"""
    
    latex_str = r"""\begin{table}[htbp]
\centering
\caption{Summary statistics of discrepancies in CDS and cash bond spreads (Extended Period)}
\label{tab:table1_extension}
\small
\begin{tabular}{l rrrr}
\hline\hline
& \multicolumn{4}{c}{Extended Period} \\
\cline{2-5}
& \multicolumn{4}{c}{Jan. 2015--Present} \\
\cline{2-5}
& Mean & SD & P10 & P90 \\
\hline
"""
    
    # Add data rows
    for _, row in table1.iterrows():
        cat = row['Category']
        mean = row['Mean']
        sd = row['SD']
        p10 = row['P10']
        p90 = row['P90']
        
        mean_str = f"{mean:d}" if pd.notna(mean) else "--"
        sd_str = f"{sd:d}" if pd.notna(sd) else "--"
        p10_str = f"{p10:d}" if pd.notna(p10) else "--"
        p90_str = f"{p90:d}" if pd.notna(p90) else "--"
        
        latex_str += f"{cat} & {mean_str} & {sd_str} & {p10_str} & {p90_str} \\\\\n"
    
    latex_str += r"""\hline\hline
\end{tabular}
\begin{flushleft}
\footnotesize
\textit{Notes:} This table extends the analysis to the period January 2015 through present. All entries are in basis points.
\end{flushleft}
\end{table}
"""
    
    output_path = OUTPUT_DIR / filename
    with open(output_path, 'w') as f:
        f.write(latex_str)
    print(f"Saved LaTeX extension table to {output_path}")

if __name__ == "__main__":
    basis = load_data()
    
    if 'phase' not in basis.columns:
        basis = add_crisis_phases(basis)
    
    # Create both tables
    table1_replication = create_table1_replication(basis)
    table1_extension = create_table1_extension(basis)
    
    # Export both
    export_to_latex_replication(table1_replication)
    export_to_latex_extension(table1_extension)
    
    # Save CSVs
    table1_replication.to_csv(OUTPUT_DIR / "table1_replication.csv", index=False)
    table1_extension.to_csv(OUTPUT_DIR / "table1_extension.csv", index=False)


