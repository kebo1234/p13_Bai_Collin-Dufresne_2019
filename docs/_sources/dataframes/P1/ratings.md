# Dataframe: `P1:ratings` - 

Bond ratings data used to tag IG vs HY.


## DataFrame Glimpse

```
Rows: 4388968
Columns: 7
$ issue_id                   <f64> 1221179.0
$ rating_type                <str> 'SPR'
$ rating_date       <datetime[ns]> 2025-01-27 00:00:00
$ rating                     <str> 'NR'
$ rating_status              <str> null
$ investment_grade           <str> null
$ __index_level_0__          <i64> 388967


```

## Dataframe Manifest

| Dataframe Name                 |                                                    |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [ratings](../dataframes/P1/ratings.md)                                       |
| Data Sources                   | Mergent FISD Ratings                                        |
| Data Providers                 | WRDS / LSEG Mergent                                      |
| Links to Providers             |                              |
| Topic Tags                     |                                           |
| Type of Data Access            |                                   |
| How is data pulled?            | Pulled from Mergent FISD ratings table                                                    |
| Data available up to (min)     | 2025-07-10 00:00:00                                                             |
| Data available up to (max)     | 2091-06-14 00:00:00                                                             |
| Dataframe Path                 | /Users/kebo/Downloads/MS FinMath/Courses/Full Stack/p13_Bai_Collin-Dufresne_2019/_data/Mergent_FISD_ratings.parquet                                                   |


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
| Date of Last Code Update        | 2026-03-10 15:27:21           |
| OS Compatibility                |  |
| Linked Dataframes               |  [P1:bond_prices](../dataframes/P1/bond_prices.md)<br>  [P1:cds](../dataframes/P1/cds.md)<br>  [P1:ratings](../dataframes/P1/ratings.md)<br>  [P1:matched_bond_cds](../dataframes/P1/matched_bond_cds.md)<br>  [P1:pecds](../dataframes/P1/pecds.md)<br>  [P1:basis](../dataframes/P1/basis.md)<br>  |


