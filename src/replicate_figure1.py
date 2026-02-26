# src/replicate_figure1.py
"""
Replicate Figure 1 from paper (pure replication + extension).
Plot of Basis (in bps) w/ median, 10th quantile, 90th quantile.
One plot for IG and HY bonds each.

Input:
    - basis.parquet

Output:
    - replication_figure1.png
    - extension_figure1.png
    - replication_figure1.html
    - extension_figure1.html
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from settings import config


DATA_DIR = Path(config('DATA_DIR'))
OUTPUT_DIR = Path(config('OUTPUT_DIR'))

START_DATE = pd.to_datetime(config('START_DATE'))
SAMPLE_END_DATE = pd.to_datetime(config('SAMPLE_END_DATE'))
END_DATE = pd.to_datetime(config('END_DATE'))


def compute_series(df):
    grouped = df.groupby('date')['basis']
    median = grouped.median()
    p10 = grouped.quantile(0.10)
    p90 = grouped.quantile(0.90)
    return median, p10, p90


def plot(df, end_date):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['date'] >= START_DATE) & (df['date'] <= end_date)]

    fig, axes = plt.subplots(2, 1, sharex=True)

    for ax, label, subset in [(axes[0], 'Investment Grade', df[df['rating_class'] == 0]),
                              (axes[1], 'High Yield', df[df['rating_class'] == 1]),]:
        median, p10, p90 = compute_series(subset)

        ax.plot(median.index, median.values)
        ax.plot(p10.index, p10.values, linestyle='--')
        ax.plot(p90.index, p90.values, linestyle='--')
        ax.set_title(label)
        ax.set_ylabel('Basis (bps)')

    axes[1].set_xlabel('Date')
    fig.tight_layout()
    return fig


def plot_html_px(df, end_date, outpath, title):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['date'] >= START_DATE) & (df['date'] <= end_date)]

    pieces = []
    for panel, rc in [('Investment Grade', 0), ('High Yield', 1)]:
        sub = df[df['rating_class'] == rc]
        grouped = sub.groupby('date')['basis']

        wide = pd.DataFrame({
            'date': grouped.median().index,
            'median': grouped.median().values,
            'p10': grouped.quantile(0.10).values,
            'p90': grouped.quantile(0.90).values,
        })

        long = wide.melt(id_vars='date', var_name='stat', value_name='basis')
        long['panel'] = panel
        pieces.append(long)

    plot_df = pd.concat(pieces, ignore_index=True)

    fig = px.line(
        plot_df,
        x='date',
        y='basis',
        color='stat',
        line_dash='stat',
        facet_row='panel',
        title=title,
    )

    fig.update_yaxes(title_text='Basis (bps)')
    fig.update_xaxes(title_text='Date')
    fig.write_html(outpath, include_plotlyjs='cdn')


if __name__ == '__main__':
    df = pd.read_parquet(DATA_DIR / 'basis.parquet')

    # PNGs
    replication_fig = plot(df, SAMPLE_END_DATE)
    replication_fig.savefig(OUTPUT_DIR / 'replication_figure1.png', dpi=200)
    plt.close(replication_fig)

    extension_fig = plot(df, END_DATE)
    extension_fig.savefig(OUTPUT_DIR / 'extension_figure1.png', dpi=200)
    plt.close(extension_fig)

    # HTMLs (for chartbook)
    plot_html_px(df, SAMPLE_END_DATE, OUTPUT_DIR / 'replication_figure1.html', 'Figure 1 (Replication Window)')
    plot_html_px(df, END_DATE, OUTPUT_DIR / 'extension_figure1.html', 'Figure 1 (Extended)')