# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 01. Data Tour: Bai, Collin-Dufresne (2019) Replication
#
# This notebook gives a brief tour of the cleaned data and the main analysis steps
# used in the replication of Figure 1 and Table 1.

# %%
from pathlib import Path
import pandas as pd
import plotly.express as px
from settings import config

DATA_DIR = Path(config("DATA_DIR"))

# %%
matched = pd.read_parquet(DATA_DIR / "matched_bond_cds.parquet")
pecds = pd.read_parquet(DATA_DIR / "pecds.parquet")
basis = pd.read_parquet(DATA_DIR / "basis.parquet")

for df in [matched, pecds, basis]:
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

# %% [markdown]
# ## 1. Overview of cleaned data

# %%
print("Matched bond-CDS data:")
print(matched.shape)
print(matched.head())

# %%
print("PECDS data:")
print(pecds.shape)
print(pecds.head())

# %%
print("Basis data:")
print(basis.shape)
print(basis.head())

# %% [markdown]
# ## 2. Sample coverage

# %%
print("Matched sample date range:", matched["date"].min(), "to", matched["date"].max())
print("Basis sample date range:", basis["date"].min(), "to", basis["date"].max())

if "ticker" in matched.columns:
    print("Unique CDS tickers:", matched["ticker"].nunique())

if "issue_id" in matched.columns:
    print("Unique bond issues:", matched["issue_id"].nunique())

# %% [markdown]
# ## 3. Construction of PECDS
#
# In this simplified replication, PECDS is proxied by the bond yield:
#
# `pecds = yield`

# %%
pecds[["date", "yield", "pecds"]].head()

# %% [markdown]
# ## 4. Construction of the CDS-bond basis
#
# The economic definition of the basis is:
#
# `basis = cds_spread - pecds`
#
# In the analysis scripts, the basis is then converted to basis points for reporting:
#
# `basis_bps = 10000 * basis`
#
# Figure 1 and Table 1 both use `basis_bps`.

# %%
basis[["date", "cds_spread", "pecds", "basis", "basis_bps"]].head()

# %% [markdown]
# ## 5. Simple time-series summary
#
# The final analysis is reported in basis points, so the summary plots below use `basis_bps`.

# %%
avg_basis = basis.groupby("date", as_index=False)["basis_bps"].mean()
avg_basis.head()

# %%
fig = px.line(
    avg_basis,
    x="date",
    y="basis_bps",
    title="Average CDS-Bond Basis (bps) Over Time"
)
fig

# %% [markdown]
# ## 6. IG vs HY comparison

# %%
if "rating_class" in basis.columns:
    ig_hy = basis.groupby(["date", "rating_class"], as_index=False)["basis_bps"].median()
    fig = px.line(
        ig_hy,
        x="date",
        y="basis_bps",
        color="rating_class",
        title="Median CDS-Bond Basis (bps) by Rating Class"
    )
    fig

# %% [markdown]
# ## 7. Final outputs
#
# The scripts `replicate_figure1.py` and `replicate_table1.py` generate the final
# paper-style outputs used in the report:
#
# - Figure 1: basis dispersion over time for IG and HY bonds, using `basis_bps`
# - Table 1: summary statistics across crisis phases and rating categories, using `basis_bps`