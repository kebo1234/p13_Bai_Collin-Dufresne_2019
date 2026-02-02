# Dataframe: `P1:crsp_stock_ciz` - 

CRSP stock data in CIZ format with monthly returns and prices.


## DataFrame Glimpse

```
Rows: 4780708
Columns: 17
$ permno                     <i64> 10000
$ permco                     <i64> 7952
$ mthcaldt          <datetime[ns]> 1986-01-31 00:00:00
$ issuertype                 <str> 'ACOR'
$ securitytype               <str> 'EQTY'
$ securitysubtype            <str> 'COM'
$ sharetype                  <str> 'NS'
$ usincflg                   <str> 'Y'
$ primaryexch                <str> 'Q'
$ conditionaltype            <str> 'RW'
$ tradingstatusflg           <str> 'A'
$ mthret                     <f64> 0.707317
$ mthretx                    <f64> 0.707317
$ shrout                     <i64> 3680
$ mthprc                     <f64> 4.375
$ jdate             <datetime[ns]> 1986-01-31 00:00:00
$ __index_level_0__          <i64> 0


```

## Dataframe Manifest

| Dataframe Name                 |                                                    |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [crsp_stock_ciz](../dataframes/P1/crsp_stock_ciz.md)                                       |
| Data Sources                   | CRSP Stock File (CIZ format)                                        |
| Data Providers                 | WRDS                                      |
| Links to Providers             |                              |
| Topic Tags                     |                                           |
| Type of Data Access            |                                   |
| How is data pulled?            | Pulled from CRSP msf_v2 using CIZ format                                                    |
| Data available up to (min)     | N/A (large file)                                                             |
| Data available up to (max)     | N/A (large file)                                                             |
| Dataframe Path                 | /Users/kebo/Downloads/p13_Bai_Collin-Dufresne_2019/_data/CRSP_stock_ciz.parquet                                                   |


**Linked Charts:**


- [P1:crsp_stock_returns](../../charts/P1.crsp_stock_returns.md)



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


