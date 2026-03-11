# Dataframe: `P1:basis` - 

Basis = CDS spread − PECDS proxy; used for Table 1 and Figure 1.


## DataFrame Glimpse

```
Rows: 770841
Columns: 32
$ date                      <datetime[ns]> 2022-03-31 00:00:00
$ ticker                             <str> 'NSC'
$ redcode                            <str> '6BADC8'
$ tenor                              <str> '5Y'
$ currency                           <str> 'USD'
$ docclause                          <str> 'XR14'
$ cds_spread                         <f64> 0.00277103
$ year_month                         <str> '2022-03'
$ bond_date                 <datetime[ns]> 2022-03-31 00:00:00
$ issue_id                           <f64> 572541.0
$ cusip                              <str> '655844BJ6'
$ company_symbol                     <str> 'NSC'
$ bond_type                          <str> 'CDEB'
$ conv                               <f64> 0.0
$ coupon                             <f64> 3.0
$ maturity                  <datetime[ns]> 2022-04-01 00:00:00
$ tmt                                <f64> 0.002777777777777778
$ price_eom                          <f64> 100.003
$ yield                              <f64> 0.03383129252989459
$ rating_class                       <str> '0.IG'
$ sp_rating                          <str> 'NR'
$ sp_ig                              <str> null
$ moodys_rating                      <str> 'NR'
$ moodys_ig                          <str> null
$ matched_treasury_no                <f64> 207809.0
$ matched_treasury_id                <str> '20220405.400000'
$ matched_treasury_yield             <f64> 3.472252363386e-06
$ matched_treasury_duration          <f64> 5.0
$ match_dist                         <f64> 4.997222222222222
$ pecds                              <f64> 0.03382782027753121
$ basis                              <f64> -0.031056790277531207
$ basis_bps                          <f64> -310.56790277531206


```

## Dataframe Manifest

| Dataframe Name                 |                                                    |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [basis](../dataframes/P1/basis.md)                                       |
| Data Sources                   | Constructed: CDS–bond basis                                        |
| Data Providers                 | Internal                                      |
| Links to Providers             |                              |
| Topic Tags                     |                                           |
| Type of Data Access            |                                   |
| How is data pulled?            | Built by src/calc_basis.py                                                    |
| Data available up to (min)     | 2021-09-30 00:00:00                                                             |
| Data available up to (max)     | 2022-03-31 00:00:00                                                             |
| Dataframe Path                 | /Users/kebo/Downloads/MS FinMath/Courses/Full Stack/p13_Bai_Collin-Dufresne_2019/_data/basis.parquet                                                   |


**Linked Charts:**


- [P1:figure1_replication](../../charts/P1.figure1_replication.md)

- [P1:figure1_extension](../../charts/P1.figure1_extension.md)



## Pipeline Manifest

| Pipeline Name                   | p13_Bai_Collin-Dufresne_2019                       |
|---------------------------------|--------------------------------------------------------|
| Pipeline ID                     | [P1](../index.md)              |
| Lead Pipeline Developer         | Nicholas Kebo & Lucie Martin             |
| Contributors                    | Nicholas Kebo & Lucie Martin           |
| Git Repo URL                    |                         |
| Pipeline Web Page               | <a href="file:///Users/kebo/Downloads/MS FinMath/Courses/Full Stack/p13_Bai_Collin-Dufresne_2019/docs/index.html">Pipeline Web Page      |
| Date of Last Code Update        | 2026-03-11 10:39:46           |
| OS Compatibility                |  |
| Linked Dataframes               |  [P1:bond_prices](../dataframes/P1/bond_prices.md)<br>  [P1:cds](../dataframes/P1/cds.md)<br>  [P1:ratings](../dataframes/P1/ratings.md)<br>  [P1:matched_bond_cds](../dataframes/P1/matched_bond_cds.md)<br>  [P1:pecds](../dataframes/P1/pecds.md)<br>  [P1:basis](../dataframes/P1/basis.md)<br>  |


