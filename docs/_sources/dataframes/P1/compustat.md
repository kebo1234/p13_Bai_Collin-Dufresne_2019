# Dataframe: `P1:compustat` - 

Firm-level accounting fundamentals used to construct balance-sheet variables.


## DataFrame Glimpse

```
Rows: 585860
Columns: 18
$ gvkey                      <str> '369350'
$ datadate          <datetime[ns]> 2024-12-31 00:00:00
$ at                         <f64> 5715.961
$ sale                       <f64> 8227.629
$ cogs                       <f64> 5033.69
$ xsga                       <f64> 1886.339
$ xint                       <f64> 13.459
$ pstkl                      <f64> 0.0
$ txditc                     <f64> 308.523
$ pstkrv                     <f64> 0.0
$ seq                        <f64> 2876.098
$ pstk                       <f64> 0.0
$ ni                         <f64> 599.446
$ sich                       <i64> 2024
$ dp                         <f64> 321.982
$ ebit                       <f64> 985.618
$ year                       <i32> 2024
$ __index_level_0__          <i64> 85859


```

## Dataframe Manifest

| Dataframe Name                 |                                                    |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [compustat](../dataframes/P1/compustat.md)                                       |
| Data Sources                   | Compustat North America                                        |
| Data Providers                 | WRDS                                      |
| Links to Providers             |                              |
| Topic Tags                     |                                           |
| Type of Data Access            |                                   |
| How is data pulled?            | Pulled via WRDS SQL query from comp.funda                                                    |
| Data available up to (min)     | 2025-12-31 00:00:00                                                             |
| Data available up to (max)     | 2025-12-31 00:00:00                                                             |
| Dataframe Path                 | /Users/kebo/Downloads/p13_Bai_Collin-Dufresne_2019/_data/Compustat.parquet                                                   |


**Linked Charts:**


- [P1:compustat_assets](../../charts/P1.compustat_assets.md)



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


