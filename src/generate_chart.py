from pathlib import Path
import pandas as pd
import plotly.express as px
from settings import config

DATA_DIR = Path(config("DATA_DIR"))
OUTPUT_DIR = Path(config("OUTPUT_DIR"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def save_chart(df, x, y, title, outpath):
    fig = px.line(df, x=x, y=y, title=title)
    fig.write_html(outpath, include_plotlyjs="cdn")

# Compustat
df = pd.read_parquet(DATA_DIR / "Compustat.parquet")
df = df[["datadate", "at"]].dropna()
df["year"] = pd.to_datetime(df["datadate"]).dt.year
df = df.groupby("year", as_index=False)["at"].mean()
save_chart(df, x="year", y="at", title="Compustat: Average Assets by Year", outpath=OUTPUT_DIR / "Compustat.html",)

# CRSP–Compustat link table
df = pd.read_parquet(DATA_DIR / "CRSP_Comp_Link_Table.parquet")
df = df[["linkdt"]].dropna()
df["year"] = pd.to_datetime(df["linkdt"]).dt.year
df = df.groupby("year", as_index=False).size()
save_chart(df, x="year", y="size", title="CRSP–Compustat Links Over Time", outpath=OUTPUT_DIR / "CRSP_Comp_Link_Table.html",)

# CRSP MSF index inputs
df = pd.read_parquet(DATA_DIR / "CRSP_MSF_INDEX_INPUTS.parquet")
df = df[["date", "ret"]].dropna()
df["date"] = pd.to_datetime(df["date"])
df = df.groupby("date", as_index=False)["ret"].mean()
save_chart(df, x="date", y="ret", title="CRSP MSF: Average Monthly Return", outpath=OUTPUT_DIR / "CRSP_MSF_Index_Inputs.html",)

# CRSP MSIX (index returns)
df = pd.read_parquet(DATA_DIR / "CRSP_MSIX.parquet")
df = df[["caldt", "vwretd"]].dropna()
df["caldt"] = pd.to_datetime(df["caldt"])
save_chart(df, x="caldt", y="vwretd", title="CRSP MSIX: Value-Weighted Index Return", outpath=OUTPUT_DIR / "CRSP_MSIX.html",)

# CRSP stock CIZ
df = pd.read_parquet(DATA_DIR / "CRSP_stock_ciz.parquet")
df = df[["jdate", "mthret"]].dropna()
df = df.groupby("jdate", as_index=False)["mthret"].mean()
save_chart(df, x="jdate", y="mthret", title="CRSP Stock CIZ: Average Monthly Return", outpath=OUTPUT_DIR / "CRSP_stock_ciz.html",)

# FF factors
df = pd.read_parquet(DATA_DIR / "FF_FACTORS.parquet")
df = df[["date", "mktrf"]].dropna()
df["date"] = pd.to_datetime(df["date"])
save_chart(df, x="date", y="mktrf", title="Fama–French: Market Excess Return (MKTRF)", outpath=OUTPUT_DIR / "FF_Factors.html",)