# Dataframe: `P1:cds` - 

Daily CDS spreads (5Y) used to compute CDS–bond basis.


## DataFrame Glimpse

```
Rows: 50222100
Columns: 7
$ date       <datetime[ns]> 2006-01-02 00:00:00
$ ticker              <str> 'T'
$ redcode             <str> '001AEC'
$ tenor               <str> '10Y'
$ currency            <str> 'USD'
$ docclause           <str> 'XR14'
$ cds_spread          <f64> 0.006852199737396506


```

## Dataframe Manifest

| Dataframe Name                 |                                                    |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [cds](../dataframes/P1/cds.md)                                       |
| Data Sources                   | Markit CDS                                        |
| Data Providers                 | WRDS                                      |
| Links to Providers             |                              |
| Topic Tags                     |                                           |
| Type of Data Access            |                                   |
| How is data pulled?            | Pulled via WRDS Markit CDS table                                                    |
| Data available up to (min)     | N/A (large file)                                                             |
| Data available up to (max)     | N/A (large file)                                                             |
| Dataframe Path                 | /Users/kebo/Downloads/MS FinMath/Courses/Full Stack/p13_Bai_Collin-Dufresne_2019/_data/CDS.parquet                                                   |


**Linked Charts:**

- None


## Pipeline Manifest

| Pipeline Name                   | p13_Bai_Collin-Dufresne_2019                       |
|---------------------------------|--------------------------------------------------------|
| Pipeline ID                     | [P1](../index.md)              |
| Lead Pipeline Developer         | Nicholas Kebo & Lucie Martin             |
| Contributors                    | Nicholas Kebo & Lucie Martin           |
| Git Repo URL                    |                         |
| Pipeline Web Page               | <a href="file:///Users/kebo/Downloads/MS FinMath/Courses/Full Stack/p13_Bai_Collin-Dufresne_2019/docs/index.html">Pipeline Web Page      |
| Date of Last Code Update        | 2026-03-10 14:08:47           |
| OS Compatibility                |  |
| Linked Dataframes               |  [P1:bond_prices](../dataframes/P1/bond_prices.md)<br>  [P1:cds](../dataframes/P1/cds.md)<br>  [P1:ratings](../dataframes/P1/ratings.md)<br>  [P1:matched_bond_cds](../dataframes/P1/matched_bond_cds.md)<br>  [P1:pecds](../dataframes/P1/pecds.md)<br>  [P1:basis](../dataframes/P1/basis.md)<br>  |


