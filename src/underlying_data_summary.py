# src/underlying_data_summary.py
"""
Creates summary table and figure for the underlying data to provide background in final report.

Outputs:
    - _output/sample_summary_table.tex
    - _output/underlying_spreads.png
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from settings import config

DATA_DIR = Path(config("DATA_DIR"))
OUTPUT_DIR = Path(config("OUTPUT_DIR"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    df = pd.read_parquet(DATA_DIR / "basis.parquet").copy()
    df["date"] = pd.to_datetime(df["date"])
    return df


def make_summary_table(df):
    vars_to_keep = ["cds_spread", "pecds", "basis_bps", "yield"]
    rows = []

    labels = {
        "cds_spread": "CDS spread",
        "pecds": "PECDS",
        "basis_bps": "Basis (bps)",
        "yield": "Bond yield",
    }

    for var in vars_to_keep:
        x = df[var].dropna()
        rows.append(
            {
                "Variable": labels[var],
                "Mean": x.mean(),
                "SD": x.std(),
                "P10": x.quantile(0.10),
                "Median": x.median(),
                "P90": x.quantile(0.90),
                "N": x.shape[0],
            }
        )

    out = pd.DataFrame(rows)

    tex = out.to_latex(
        index=False,
        float_format="%.2f",
        escape=False,
    )

    (OUTPUT_DIR / "sample_summary_table.tex").write_text(tex)


def make_underlying_figure(df):
    daily = (
        df.groupby("date", as_index=False)[["cds_spread", "pecds"]]
        .mean()
        .sort_values("date")
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(daily["date"], daily["cds_spread"], label="Average CDS spread")
    ax.plot(daily["date"], daily["pecds"], label="Average PECDS")
    ax.set_xlabel("Date")
    ax.set_ylabel("Spread")
    ax.set_title("Average Daily CDS Spread and PECDS")
    ax.legend()
    fig.tight_layout()

    fig.savefig(OUTPUT_DIR / "underlying_spreads.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    df = load_data()
    make_summary_table(df)
    make_underlying_figure(df)