# Dataframe: `P1:bond_prices` - 

Bond prices/yields used to proxy PECDS and match to CDS.


## DataFrame Glimpse

```
Rows: 3475149
Columns: 12
$ date           <datetime[ns]> 2006-07-31 00:00:00
$ issue_id                <f64> 5.0
$ cusip                   <str> '00077TAA2'
$ company_symbol          <str> 'ABN'
$ bond_type               <str> 'CDEB'
$ conv                    <f64> 0.0
$ coupon                  <f64> 7.75
$ maturity       <datetime[ns]> 2023-05-15 00:00:00
$ tmt                     <f64> 17.033333333333335
$ price_eom               <f64> 122.712
$ yield                   <f64> 0.05636203487156202
$ rating_class            <str> '0.IG'


```

## Dataframe Manifest

| Dataframe Name                 |                                                    |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [bond_prices](../dataframes/P1/bond_prices.md)                                       |
| Data Sources                   | WRDS Bond Returns                                        |
| Data Providers                 | WRDS                                      |
| Links to Providers             |                              |
| Topic Tags                     |                                           |
| Type of Data Access            |                                   |
| How is data pulled?            | Pulled via WRDS from Bond Returns (monthly)                                                    |
| Data available up to (min)     | N/A (large file)                                                             |
| Data available up to (max)     | N/A (large file)                                                             |
| Dataframe Path                 | /Users/kebo/Downloads/MS FinMath/Courses/Full Stack/p13_Bai_Collin-Dufresne_2019/_data/bond_prices.parquet                                                   |


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
| Date of Last Code Update        | 2026-03-10 14:03:57           |
| OS Compatibility                |  |
| Linked Dataframes               |  [P1:bond_prices](../dataframes/P1/bond_prices.md)<br>  [P1:cds](../dataframes/P1/cds.md)<br>  [P1:ratings](../dataframes/P1/ratings.md)<br>  [P1:matched_bond_cds](../dataframes/P1/matched_bond_cds.md)<br>  [P1:pecds](../dataframes/P1/pecds.md)<br>  [P1:basis](../dataframes/P1/basis.md)<br>  |


