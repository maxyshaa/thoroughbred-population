"""
This python script is designed to generate a suitable csv file with merged pedigree & genotype information for 
given individuals and concatenate all provided datasets. The script cleans and processes pedigree information,
merges data provided from Plusvital, filters duplicates.

Inputs:
- raw_pedigree_part1.xlsx: An excel file containing multiple sheets with pedigree data provided by Plusvital.
- raw_pedigree_part2.csv: A csv file with additional pedigree data provided by Plusvital.
- TB_11K.fam: A PLINK .fam file for 11K SNP data as a part of plink files provided by Plusvital.
- TB_6K.fam: A PLINK .fam file for 6K SNP data as a part of plink files provided by Plusvital.

Outputs:
- merged_ped.csv: A csv file with merged and cleaned pedigree data.
- merged_ped_no_dupl.csv: A csv file with merged pedigree data, duplicates removed.
- dupl_bedids.txt: A text file with duplicate bed ids to remove them from genotype analysis.
"""

import pandas as pd
import numpy as np

################################## Inputs ##################################
# read an initial file of pedigree
sheet_to_df_map = pd.read_excel("raw_pedigree_part1.xlsx", 
                                sheet_name=None, 
                                dtype=str,
                                na_values=[" ", "", "None"]) # just to unify missing values

# the names of the sheets are:
# PedIDMatch (matching suffixes of genome id written in plink files with ped id), 
# PedNew (pedigree phenotypes info), 
# GenotypeIDs (info about genotypes)

pedid_match = sheet_to_df_map["PedIDMatch"]
ped_df = sheet_to_df_map["PedNew"]
geno_id = sheet_to_df_map["GenotypeIDs"]

# read a pedigree with additional 6k data without info on pedigree
ped_addit = pd.read_csv("raw_pedigree_part2.csv", 
                        dtype=str, na_values=[" ", "", "None"], 
                        usecols=range(12)).query("id.notna().values") # to read only those rows that has an actual records


################################## Functions ##################################

# functions to process and clean the ped_df first

def clear_colour(init_file: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """This function corrects the colour variable in the ped_df that automatically inherited values from the websites"""
    incor_color = ~init_file[col_name].isna() & init_file[col_name].str.contains('\d', regex=True)
    init_file.loc[incor_color, col_name] = np.NAN
    print(f"The missing values in the {col_name} is {init_file[col_name].isna().sum()} out of {init_file.shape[0]}\
 and variables in the given columns are following:{init_file[col_name].unique()}")
    return init_file 

def fix_logic(init_file: pd.DataFrame) -> pd.DataFrame:
    """The function checks the pedigree df in terms of logical errors and removes incorrect information"""
    # checking if some indivs have multiple sires or dams
    multipar = init_file \
                .groupby(["id"], as_index=False) \
                .agg({"sire_id": pd.Series.nunique, "dam_id":pd.Series.nunique}) \
                .query("sire_id > 1 | dam_id > 1")
    
    if len(multipar) > 0:
        error_message = "DataFrame contains rows with multiple sire/dam of an inidividual"
        raise ValueError(error_message) # since we don't have this issue so I just raise the error here
    else:
        print("Multiple parents not detected")
    
    # checking if sex code matches with partnership; 1 codes a male
    sex_1dam = init_file.query("(sex=='1') and (id in dam_id)")
    sex_2sire = init_file.query("(sex=='2') and (id in sire_id)")

    if len(sex_1dam) or len(sex_2sire) > 0:
        error_message = "DataFrame contains rows with wrong sex assigned"
        raise ValueError(error_message)
    else:
        print("Sex conflict not detected")

    # checking if some individuals have parents younger than themselves
    slice_cols = ["id", "sire_id", "dam_id", "YOB"]
    wrongage_d = init_file[slice_cols] \
                    .merge(init_file[slice_cols], left_on="dam_id", right_on="id", suffixes=("_child", "_dam")) \
                    .query("YOB_child < YOB_dam")
    
    wrongage_s = init_file[slice_cols] \
                    .merge(init_file[slice_cols], left_on="sire_id", right_on="id", suffixes=("_child", "_sire")) \
                    .query("YOB_child < YOB_sire")
    
    if len(wrongage_d) > 0:
        wrong_ids = wrongage_d["id_child"].tolist()
        init_file.loc[init_file["id"].isin(wrong_ids), "dam_id"] = np.nan
        print(f"dam_id for individual {init_file.loc[init_file['id'].isin(wrong_ids), 'id'].to_string(index=False)} is removed")
    elif len(wrongage_s) > 0:
        wrong_ids = wrongage_s["id_child"].tolist()
        init_file.loc[init_file["id"].isin(wrong_ids), "sire_id"] = np.nan
        print(f"sire_id for individual {init_file.loc[init_file['id'].isin(wrong_ids),'id'].to_string(index=False)} is removed")
    else:
        print("Wrong parent-offspring relation based on age is not detected")
        pass
    
    return init_file

def read_fam_file(file_path:str) -> set:
    """
    Read a .fam file and extract a set of IDs
    """
    fam_df = pd.read_csv(file_path, delim_whitespace=True, header=None)
    ids = set(fam_df[1].unique())
    return ids

def filter_geno(init_file: pd.DataFrame, equinomeid:str, bedid:str) -> pd.DataFrame:
    """Filtering genotype records based on SNPChip priority and batchID"""
    snp_priority = {"SNP670":3, "SNP70_V2":2, "SNP70_PVL":2, "SNP70":2, "SNP50":1}
    init_file["SNPChip_prority"] = init_file["SNPChip"].map(snp_priority)
    df_sorted = init_file.sort_values(["SNPChip_prority", "batchID"], ascending=[False, False])
    # drop duplicates in 'equinomeID' column and keep the first occurrence (highest priority SNPChip and maximum batchID)
    df_filtered = df_sorted.drop_duplicates(subset=equinomeid, keep="first").drop(columns="SNPChip_prority")
    print(f"Duplicates were filtered, the shape of filtered dataframe is {df_filtered.shape[0]}")
    duplicates_removed = init_file[~init_file.index.isin(df_filtered.index)]
    exclusive_rows = duplicates_removed[duplicates_removed[bedid].notna()]
    exclusive_rows[[bedid, bedid]].to_csv("output/removed_bedids.txt", 
                                                index=False, sep=" ", header=None)
    print(f"Removed {exclusive_rows.shape[0]} rows")
    return df_filtered












def search_substring_in_dict(dictionary, substring):
    results = [key for key in dictionary if substring in key]
    return results

def filter_pedid_match(pedid_match: pd.DataFrame, fam_ids: set) -> pd.DataFrame:
    """
    Filter pedid_match to keep only equinomeIDs that are present in the bed file
    """
    filtered = pedid_match[pedid_match["Equinome ID"].isin(fam_ids)]
    return filtered


def merge_dataframes(ped_df: pd.DataFrame, pedid_match: pd.DataFrame, geno_id: pd.DataFrame, fam_ids: set) -> pd.DataFrame:
    """
    Merge ped_df, filtered pedid_match, and filtered geno_id into a single dataframe
    """
    pedid_match_filtered = filter_pedid_match(pedid_match, fam_ids)
    geno_id_filtered = filter_geno_id(geno_id)
    merged_df = ped_df \
        .merge(pedid_match_filtered, left_on="id", right_on="horse_id", how="left") \
        .drop(columns=["Horse Name", "horse_id"]) \
        .rename(columns={"Equinome ID": "equinomeID"})
    merged_df = merged_df.merge(geno_id_filtered, on="equinomeID", how="left") \
        .rename(columns={"id_x": "id", "id_y": "id_bed", "sex_x": "sex"}) \
        .drop(columns=["sex_y"])
    merged_df["ped_full"] = True
    
    return merged_df

def concat_peds(elevenK_df: pd.DataFrame, sixK_df: pd.DataFrame) -> pd.DataFrame:
    """Combine all pedigree datasets into one"""
    alltogether_pedigree = pd.concat([sixK_df[["id", "status", "name" ,"sire_id", "dam_id",
                                   "YOB", "sex", "COB", "equinomeID", "id_bed", 
                                   "batchID", "SNPChip", "Country Reported", "ped_full"]], elevenK_df])
    return alltogether_pedigree

def filter_duplicates(init_file: pd.DataFrame):
    """Filter duplicates based on SNPChip priority and batchID"""
    snp_priority = {"SNP670": 4, "SNP70_V2": 3, "SNP70_PVL": 2, "SNP50": 1}
    init_file["SNPChip_priority"] = init_file["SNPChip"].map(snp_priority)
    ped_sorted = init_file.sort_values(["SNPChip_priority", "batchID"], ascending=False)
    ped_filtered = ped_sorted.drop_duplicates(subset="equinomeID", keep="first").drop(columns="SNPChip_priority")
    print(f"Duplicates were filtered, the shape of filtered dataframe is {ped_filtered.shape}")
    duplicates_removed = init_file[~init_file.index.isin(ped_filtered.index)]
    exclusive_rows = duplicates_removed[duplicates_removed["id_bed"].notna()]
    exclusive_rows[["id_bed", "id_bed"]].to_csv("dupl_bedids.txt", index=False, sep=" ", header=None)
    return ped_filtered

# functions to reformat the ped_addit

def clear_ped_additional(init_file: pd.DataFrame) -> pd.DataFrame:
    """This function changes the format of the additional dataset of pedigree to be able to concatenate with the base one"""
    init_file["Horse Name"] = init_file["Horse Name"].str.lower()
    init_file["Sire"] = init_file["Sire"].str.lower()
    init_file["Dam"] = init_file["Dam"].str.lower()
    init_file["sex"] = init_file["sex"].replace(["Male", "Female"],["1", "2"])
    init_file["status"] = "9999"
    init_file["sire_id"] = None 
    init_file["dam_id"] = None
    init_file["id_bed"] = init_file["id"]
    init_file["ped_full"] = False
    init_file.rename(columns={"Horse Name":"name", "Year of Birth":"YOB",
                              "Country of Birth":"COB", "Sire":"sire_name", "Dam":"dam_name"}, inplace=True)
    init_file["YOB"] = init_file["YOB"].astype("float").astype("Int64")
    return init_file

# def merg_sheets(ped_df: pd.DataFrame, pedid_match=pedid_match, geno_id=geno_id) -> pd.DataFrame:
#     """This function merged all sheets after fixing errors and combine all id matching in one DataFrame"""
#     merged_table = ped_df \
#     .merge(pedid_match, left_on="id", right_on="horse_id", how="left") \
#     .drop(columns=["Horse Name", "horse_id"]) \
#     .rename(columns={"Equinome ID":"equinomeID"}) \
#     .merge(geno_id, on="equinomeID", how="outer") \
#     .rename(columns={"id_x":"id", "id_y":"id_bed", "sex_x":"sex"}) \
#     .drop(columns=["sex_y"])
#     merged_table["ped_full"] = True # to distinguish between this and 6K dataframe
#     return merged_table

# def concat_peds(elevenK_df: pd.DataFrame, sixK_df:pd.DataFrame) -> pd.DataFrame:
#     """It's a final step to combine all pedigree datasets into one."""
#     alltogether_pedigree = pd.concat([sixK_df[["id", "status", "name" ,"sire_id", "dam_id",
#                                    "YOB", "sex", "COB", "equinomeID", "id_bed", 
#                                    "batchID", "SNPChip", "Country Reported", "ped_full"]], elevenK_df])
#     return alltogether_pedigree

# def filter_duplicates(init_file: pd.DataFrame):
#     # define the order of priority for SNPChip values
#     snp_priority = {"SNP670":4, "SNP70_V2":3, "SNP70_PVL":2, "SNP50":1}
#     init_file["SNPChip_prority"] = init_file["SNPChip"].map(snp_priority)
#     # sort the DataFrame based on SNPChip and batchID in descending order
#     ped_sorted = init_file.sort_values(["SNPChip_prority", "batchID"], ascending=False)
#     # drop duplicates in 'equinomeID' column and keep the first occurrence (highest priority SNPChip and maximum batchID)
#     ped_filtered = ped_sorted.drop_duplicates(subset="equinomeID", keep="first").drop(columns="SNPChip_prority")
#     print(f"Duplicates were filtered, the shape of filtered dataframe is {ped_filtered.shape}")
#     duplicates_removed = init_file[~init_file.index.isin(ped_filtered.index)]
#     exclusive_rows = duplicates_removed[duplicates_removed["id_bed"].notna()]
#     exclusive_rows[["id_bed", "id_bed"]].to_csv("dupl_bedids.txt", index=False, sep=" ", header=None)
#     return ped_filtered

# if __name__ == "__main__":
#     print("Starting cleaning ped_df structure")
#     ped_fixed = fix_logic(clear_colour(init_file=ped_df, col_name="colour"))
#     print(f"The number of unique individuals in initial ped file is {ped_df.id.nunique()}")
#     print(f"The number of unique individuals in fixed ped file is {ped_fixed.id.nunique()}")
#     print("Starting working with the additional pedigree")
#     ped_addit_fixed = clear_ped_additional(init_file=ped_addit)
#     final_df = concat_peds(elevenK_df=merg_sheets(ped_df=ped_fixed), sixK_df=ped_addit_fixed)
#     final_df.to_csv("merged_ped.csv", sep=",", index=False)
#     # filter duplicates
#     ped_no_dupl = filter_duplicates(init_file=final_df)
#     ped_no_dupl.to_csv("merged_ped_no_dupl.csv", sep=",", index=False)

if __name__ == "__main__":
    print("Starting cleaning ped_df structure")
    ped_fixed = fix_logic(clear_colour(init_file=ped_df, col_name="colour"))
    print(f"The size of the dataframe before is {ped_df.shape[0]} and \
 the number of unique individuals in the initial ped file is {ped_df.id.nunique()}")
    print(f"The size of the dataframe after cleaning records is {ped_fixed.shape[0]} \
 and the number of unique individuals in the fixed ped file is {ped_fixed.id.nunique()}")

    print("Reading .fam files")
    fam_11k_ids = read_fam_file("/home/kseniia/projects/data/raw_data/TB_11K.fam")
    fam_6k_ids = read_fam_file("/home/kseniia/projects/data/raw_data/TB_6K.fam")
    bed_ids = fam_11k_ids.union(fam_6k_ids)

    print("Cleaning geno_id dataframe")
    geno_id_fixed = filter_geno(geno_id, "equinomeID", "id")

    print("Starting working with the additional pedigree")
    ped_addit_fixed = clear_ped_additional(init_file=ped_addit)


    
    print("Merging sheets")
    elevenK_df = merge_dataframes(ped_df=ped_fixed, pedid_match=pedid_match, geno_id=geno_id, fam_ids=bed_ids)
    final_df = concat_peds(elevenK_df=elevenK_df, sixK_df=ped_addit_fixed)
    final_df.to_csv("merged_ped.csv", sep=",", index=False)

    print("Filtering duplicates")
    ped_no_dupl = filter_duplicates(init_file=final_df)
    ped_no_dupl.to_csv("merged_ped_no_dupl.csv", sep=",", index=False)

    print("Process completed")


# I also found out if I check duplicates based on truio "name", "dam_id", "YOB" then I have 4K individuals that are not merged but their sire_id, dam_id and YOB are empty, however they might be the same founder. They are all founders, status=3.
# I will leave them how it is, I think it's that kinda of issue when you have to verify that using KING/other genetic tools 
