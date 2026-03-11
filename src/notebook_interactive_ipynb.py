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
# # Bai, Collin-Dufresne (2019) Replication
#
# ## Summary
#
# Bai and Collin-Dufresne (2019) study the CDS-bond basis, defined as the difference
# between the market CDS spread and the bond-implied CDS spread. Their results show
# that the basis became sharply negative and more volatile during the global financial crisis,
# especially for high-yield bonds. In this project, we replicate their Figure 1 and Table 1
# using WRDS bond return data, Markit CDS data, and Mergent FISD ratings.
#
#
# This notebook gives a guided tour of the cleaned datasets and the main analysis steps
# used in the pipeline. The underlying scripts (not including pull scripts) are:
#
# - `filter_data.py`: filters the bond and CDS universe and builds the matched panel
# - `calc_PECDS.py`: constructs the PECDS proxy
# - `calc_basis.py`: computes the CDS-bond basis and converts it to basis points
# - `replicate_figure1.py`: generates the figure outputs
# - `replicate_table1.py`: generates the summary table output

# %%

from pathlib import Path
import pandas as pd
import plotly.express as px
from settings import config
from IPython.display import Image, display

DATA_DIR = Path(config("DATA_DIR"))
OUTPUT_DIR = Path(config("OUTPUT_DIR"))

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
# In this simplified replication, PECDS is proxied by bond yield - Treasury yield (procy for risk-free rate):
#
# `pecds = Bond yield - Treasury yield`,
#
# where Treasury yields are mapped to bond yields based on duration -> TTM.

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
# paper-style outputs used in the report.

# %% [markdown]
# ### Figure 1: Replication Period (July 2006 - December 2014)
#
# This figure replicates Figure 1 from the original paper, showing the median CDS-bond
# basis and 10th/90th percentiles for investment-grade and high-yield bonds during the
# paper's sample period.

# %%
display(Image(filename=OUTPUT_DIR / "replication_figure1.png"))

# %% [markdown]
# ### Figure 1: Extension Period (January 2015 - Present)
#
# This figure extends the analysis beyond the paper's sample period to show how the
# CDS-bond basis has evolved in recent years.

# %%
display(Image(filename=OUTPUT_DIR / "extension_figure1.png"))

# %% [markdown]
# ### Table 1: Replication Period
#
# Summary statistics for the CDS-bond basis across rating categories and crisis phases,
# matching the paper's methodology. All values in basis points.

# %%
table1_replication = pd.read_csv(OUTPUT_DIR / "table1_replication.csv")
table1_replication

# %% [markdown]
# ### Table 1: Extension Period
#
# Summary statistics for the extended period (January 2015 - Present).

# %%
table1_extension = pd.read_csv(OUTPUT_DIR / "table1_extension.csv")
table1_extension