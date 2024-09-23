## **Pedigree data preprocessing and family content exploration**

This Python module is designed for cleaning and preparing two pedigree datasets for downstream analysis. The pedigree data comes from the open resource PedigreeQuery, while the genotypes were provided by Plusvital.

### Input data

The raw data are located in the `data/ `folder and consist of two files: `raw_pedigree_part1.xlsx` and `raw_pedigree_part2.csv`, representing **Pedigree #1**  and **Pedigree #2**, respectively.

**Pedigree #1**

This is an `.xlsx` file containing individuals found in an open resource pedigree. It includes three sheets:

* **pedIDmatch**

| Equinome ID | Horse Name         | horse_id |
| :---------- | :----------------- | -------: |
| 82          | A Goodlookin Broad |       62 |
| 82_2        | A Goodlookin Broad |       62 |
| CM012       | Sadlers Wells      |       69 |
| CM006       | Fairy King         |       98 |
| CM015       | Turtle Island      |      106 |

* **PedNew**

|     id | status | name          | sire_id | dam_id |  YOB | sex | colour | COB |
| -----: | -----: | :------------ | ------: | -----: | ---: | --: | :----- | :-- |
|      7 |      0 | battle joined |       3 |      6 | 1959 |   1 | b.     | USA |
| 177841 |      0 | armed venus   |       3 | 452020 | 1958 |   2 | b.     | USA |
| 448331 |      0 | gentility     |       3 | 448330 | 1961 |   2 | b.     | USA |
|     15 |      0 | ack ack       |       7 |     14 | 1966 |   1 | b.     | USA |
| 383725 |      0 | jungle war    |       7 | 383724 | 1964 |   2 | b.     | USA |

* **GenotypeIDs**

| id                  |  batchID | equinomeID | SNPChip | Year of Birth | Country Reported | sex    |
| :------------------ | -------: | :--------- | :------ | ------------: | :--------------- | :----- |
| 20160112_JSB001_409 | 20160112 | JSB001_409 | SNP670  |          1971 | Ireland          | Female |
| 20141029_CM108      | 20141029 | CM108      | SNP70   |          1973 | Ireland          | Female |
| 20100101_CM002      | 20100101 | CM002      | SNP50   |          1974 | Ireland          | Male   |
| 20100101_CM104      | 20100101 | CM104      | SNP50   |          1975 | Ireland          | Female |
| 20141029_CM110      | 20141029 | CM110      | SNP70   |          1976 | Ireland          | Female |

**Pedigree #2**

This is a `.csv` file containing genotyped animals that were not found in PedigreeQuery.

| id              |  batchID | equinomeID | SNPChip | Year of Birth | sex    | Country Reported | Horse Name      | Sire          | Dam           | Month of Birth | Country of Birth |
| :-------------- | -------: | :--------- | :------ | ------------: | :----- | :--------------- | :-------------- | :------------ | :------------ | :------------- | :--------------- |
| 20100101_103    | 20100101 | 103        | SNP50   |          2003 | Male   | New Zealand      | Condesire       | Traditionally | Fine Feather  | September      | New Zealand      |
| 20100101_GB5    | 20100101 | GB5        | SNP50   |          1999 | Female | Ireland          | Susan Glen      | Sacrament     | SanvacGlen    | May            | Ireland          |
| 20100101_GF01   | 20100101 | GF01       | SNP50   |          2000 | Male   | Ireland          | Rossmore Castle | WitnessBox    | LatinQuarter  | June           | Ireland          |
| 20100101_GF03   | 20100101 | GF03       | SNP50   |          2003 | Male   | Ireland          | Radiator Rooney | Elnadim       | QueenofTheMay | April          | Ireland          |
| 20100101_JSB049 | 20100101 | JSB049     | SNP50   |          2004 | Female | Ireland          | Ambereen        | Lils Boy      | Aeraiocht     | February       | Ireland          |

### Output data

The preprocessing produces two output files in the `results/` folder:

`bedids2exclude.txt` **—** a file containing bed_ids of genotypes that were excluded from the analysis, formatted for PLINK QC.

| 20141029_WKS001_177 20141029_WKS001_177 |
| -------------------------------------- |
| 20180601_BTY001_002 20180601_BTY001_002 |
| 20180601_BTY001_003 20180601_BTY001_003 |
| 20150528_SHS001_262 20150528_SHS001_262 |
| 20180111_DRK001_063 20180111_DRK001_063 |
| 20180111_RSY001_047 20180111_RSY001_047 |

`cleaned_pedigree.csv` — the cleaned and combined pedigree file.

| horse_id | status | horse_name    | sire_id | dam_id |  YOB | MOB | sex | colour | COB | equinome_id | bed_id | batch | snp_chip | country_reported | genotyped |
| -------: | -----: | :------------ | ------: | -----: | ---: | --: | --: | :----- | :-- | ----------: | -----: | ----: | -------: | ---------------: | :-------- |
|        7 |      0 | battle joined |       3 |      6 | 1959 | nan |   1 | b.     | USA |         nan |    nan |   nan |      nan |              nan | False     |
|   177841 |      0 | armed venus   |       3 | 452020 | 1958 | nan |   2 | b.     | USA |         nan |    nan |   nan |      nan |              nan | False     |
|   448331 |      0 | gentility     |       3 | 448330 | 1961 | nan |   2 | b.     | USA |         nan |    nan |   nan |      nan |              nan | False     |
|       15 |      0 | ack ack       |       7 |     14 | 1966 | nan |   1 | b.     | USA |         nan |    nan |   nan |      nan |              nan | False     |
|   383725 |      0 | jungle war    |       7 | 383724 | 1964 | nan |   2 | b.     | USA |         nan |    nan |   nan |      nan |              nan | False     |

### **Requirements**

* python => 3.10.10
* R => 4.3.2

## Synopsis

**Preprocessing steps:**

1) Pedigree #1 undergoes some QC. This includes clearing the colour column (where some values are digits) and checking for multiple sires or dams per individual. Sex checks are performed to ensure no inconsistencies (e.g., dams listed as sires). Records that violate the rule "parent must be older than the child" are removed.
2) Genotype records from both files are checked against the provided `.fam` files. Individuals are then filtered based on SNPChip density, selecting the most recent data when duplicates by EquinomeID exist.
3) Duplications in pedIDmatch are resolved by removing entries listed in `problems/pedid_dup_diff_names.csv `from both pedIDmatch and the GenotypeIDs dataframes. Duplicates based on horse_id are prioritized by chip information, as was done previously for EquinomeID duplicates.
4) All three dataframes from Pedigree #1 are merged, and the columns are tidied to allow concatenation with Pedigree #2.
5) Pedigree #2 is modified to allow concatenation with Pedigree #1 (since it contains extra columns).
6) Pedigree #1 and Pedigree #2 are concatenated into a single file,` cleaned_pedigree.csv`.
7) The file `bedids2exclude.txt` file, containing all bed_ids excluded from the analysis. This file is used in PLINK QC analysis.

## Running preprocessing

```bash
pip install -r requirements.txt

python main.py
```
