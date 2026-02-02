# Dataframe: `P1:ff_factors` - 

Fama–French factor returns used as benchmark market measures.


## DataFrame Glimpse

```
Rows: 1193
Columns: 9
$ date   <datetime[ns]> 2025-11-30 00:00:00
$ mktrf           <f64> -0.0013
$ smb             <f64> 0.0038
$ hml             <f64> 0.0376
$ rf              <f64> 0.003
$ year            <f64> 2025.0
$ month           <f64> 11.0
$ umd             <f64> -0.018
$ dateff          <str> null


```

## Dataframe Manifest

| Dataframe Name                 |                                                    |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [ff_factors](../dataframes/P1/ff_factors.md)                                       |
| Data Sources                   | Fama–French Factors                                        |
| Data Providers                 | WRDS                                      |
| Links to Providers             |                              |
| Topic Tags                     |                                           |
| Type of Data Access            |                                   |
| How is data pulled?            | Pulled from WRDS ff.factors_monthly table                                                    |
| Data available up to (min)     | 2024-12-31 00:00:00                                                             |
| Data available up to (max)     | 2025-11-30 00:00:00                                                             |
| Dataframe Path                 | /Users/kebo/Downloads/p13_Bai_Collin-Dufresne_2019/_data/FF_FACTORS.parquet                                                   |


**Linked Charts:**


- [P1:ff_market](../../charts/P1.ff_market.md)



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


