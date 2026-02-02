# Dataframe: `P1:crsp_msf` - 

Monthly CRSP stock-level data used to compute returns and market equity.


## DataFrame Glimpse

```
Rows: 532309
Columns: 24
$ date              <datetime[ns]> 2014-11-28 00:00:00
$ permno                     <i64> 93436
$ permco                     <i64> 53453
$ shrcd                      <i64> 11
$ exchcd                     <i64> 3
$ comnam                     <str> 'TESLA MOTORS INC'
$ shrcls                     <str> null
$ ret                        <f64> 0.011667
$ retx                       <f64> 0.011667
$ dlret                      <f64> null
$ dlretx                     <f64> null
$ dlstcd                     <i64> null
$ prc                        <f64> 244.52
$ altprc                     <f64> 244.52
$ vol                        <f64> 1077170.0
$ shrout                     <f64> 125382000.0
$ cfacshr                    <f64> 15.0
$ cfacpr                     <f64> 15.0
$ naics                      <str> '336111'
$ siccd                      <i64> 9999
$ adj_shrout                 <f64> 1880730000.0
$ adj_prc                    <f64> 16.301333333333336
$ market_cap                 <f64> 30658406640.000004
$ __index_level_0__          <i64> 32308


```

## Dataframe Manifest

| Dataframe Name                 |                                                    |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [crsp_msf](../dataframes/P1/crsp_msf.md)                                       |
| Data Sources                   | CRSP Monthly Stock File                                        |
| Data Providers                 | WRDS                                      |
| Links to Providers             |                              |
| Topic Tags                     |                                           |
| Type of Data Access            |                                   |
| How is data pulled?            | Pulled from CRSP MSF v2 and processed                                                    |
| Data available up to (min)     | 2014-10-31 00:00:00                                                             |
| Data available up to (max)     | 2014-11-28 00:00:00                                                             |
| Dataframe Path                 | /Users/kebo/Downloads/p13_Bai_Collin-Dufresne_2019/_data/CRSP_MSF_INDEX_INPUTS.parquet                                                   |


**Linked Charts:**


- [P1:crsp_msf_returns](../../charts/P1.crsp_msf_returns.md)



## Pipeline Manifest

| Pipeline Name                   | p13_Bai_Collin-Dufresne_2019                       |
|---------------------------------|--------------------------------------------------------|
| Pipeline ID                     | [P1](../index.md)              |
| Lead Pipeline Developer         | Nicholas Kebo & Lucie Martin             |
| Contributors                    | Nicholas Kebo & Lucie Martin           |
| Git Repo URL                    |                         |
| Pipeline Web Page               | <a href="file:///Users/kebo/Downloads/p13_Bai_Collin-Dufresne_2019/docs/index.html">Pipeline Web Page      |
| Date of Last Code Update        | 2026-02-02 13:35:01           |
| OS Compatibility                |  |
| Linked Dataframes               |  [P1:compustat](../dataframes/P1/compustat.md)<br>  [P1:crsp_comp_link](../dataframes/P1/crsp_comp_link.md)<br>  [P1:crsp_msf](../dataframes/P1/crsp_msf.md)<br>  [P1:crsp_msix](../dataframes/P1/crsp_msix.md)<br>  [P1:crsp_stock_ciz](../dataframes/P1/crsp_stock_ciz.md)<br>  [P1:ff_factors](../dataframes/P1/ff_factors.md)<br>  |


