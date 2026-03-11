# Dataframe: `P1:matched_bond_cds` - 

Matched panel used to compute PECDS and basis.


## DataFrame Glimpse

```
Rows: 16727368
Columns: 24
$ date           <datetime[ns]> 2006-07-03 00:00:00
$ ticker                  <str> 'T'
$ redcode                 <str> '001AEC'
$ tenor                   <str> '5Y'
$ currency                <str> 'USD'
$ docclause               <str> 'XR14'
$ cds_spread              <f64> 0.00234669375
$ year_month              <str> '2006-07'
$ bond_date      <datetime[ns]> 2006-07-31 00:00:00
$ issue_id                <f64> 21454.0
$ cusip                   <str> '879240AN9'
$ company_symbol          <str> 'T'
$ bond_type               <str> 'CDEB'
$ conv                    <f64> 0.0
$ coupon                  <f64> 9.8
$ maturity       <datetime[ns]> 2012-02-01 00:00:00
$ tmt                     <f64> 5.586111111111111
$ price_eom               <f64> 116.589
$ yield                   <f64> 0.06204082935158779
$ rating_class            <str> '0.IG'
$ sp_rating               <str> 'NR'
$ sp_ig                   <str> null
$ moodys_rating           <str> 'NR'
$ moodys_ig               <str> null


```

## Dataframe Manifest

| Dataframe Name                 |                                                    |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [matched_bond_cds](../dataframes/P1/matched_bond_cds.md)                                       |
| Data Sources                   | Constructed: bond–CDS matched panel                                        |
| Data Providers                 | Internal                                      |
| Links to Providers             |                              |
| Topic Tags                     |                                           |
| Type of Data Access            |                                   |
| How is data pulled?            | Built by src/filter_data.py by matching bond monthly to CDS daily by ticker and month                                                    |
| Data available up to (min)     | N/A (large file)                                                             |
| Data available up to (max)     | N/A (large file)                                                             |
| Dataframe Path                 | /Users/kebo/Downloads/MS FinMath/Courses/Full Stack/p13_Bai_Collin-Dufresne_2019/_data/matched_bond_cds.parquet                                                   |


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
| Date of Last Code Update        | 2026-03-11 13:30:24           |
| OS Compatibility                |  |
| Linked Dataframes               |  [P1:bond_prices](../dataframes/P1/bond_prices.md)<br>  [P1:cds](../dataframes/P1/cds.md)<br>  [P1:ratings](../dataframes/P1/ratings.md)<br>  [P1:matched_bond_cds](../dataframes/P1/matched_bond_cds.md)<br>  [P1:pecds](../dataframes/P1/pecds.md)<br>  [P1:basis](../dataframes/P1/basis.md)<br>  |


