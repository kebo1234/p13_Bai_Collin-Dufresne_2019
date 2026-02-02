# Dataframe: `P1:crsp_comp_link` - 

Link table connecting CRSP securities to Compustat firms.


## DataFrame Glimpse

```
Rows: 39192
Columns: 6
$ gvkey              <str> '356289'
$ permno             <f64> 25036.0
$ linktype           <str> 'LC'
$ linkprim           <str> 'P'
$ linkdt    <datetime[ns]> 2024-04-08 00:00:00
$ linkenddt <datetime[ns]> null


```

## Dataframe Manifest

| Dataframe Name                 |                                                    |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [crsp_comp_link](../dataframes/P1/crsp_comp_link.md)                                       |
| Data Sources                   | CRSP–Compustat Link Table                                        |
| Data Providers                 | WRDS                                      |
| Links to Providers             |                              |
| Topic Tags                     |                                           |
| Type of Data Access            |                                   |
| How is data pulled?            | Pulled from CRSP CCM linking table                                                    |
| Data available up to (min)     | 2024-12-01 00:00:00                                                             |
| Data available up to (max)     | 2024-12-31 00:00:00                                                             |
| Dataframe Path                 | /Users/kebo/Downloads/p13_Bai_Collin-Dufresne_2019/_data/CRSP_Comp_Link_Table.parquet                                                   |


**Linked Charts:**


- [P1:crsp_comp_links](../../charts/P1.crsp_comp_links.md)



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


