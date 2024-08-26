import pandas as pd
import numpy as np

# first 11K
sheet_to_df_map = pd.read_excel("raw_pedigree_part1.xlsx", 
                                sheet_name=None, 
                                dtype=str,
                                na_values=[" ", "", "None"]) 

pedid_match = sheet_to_df_map["PedIDMatch"]
ped_df = sheet_to_df_map["PedNew"]
geno_id = sheet_to_df_map["GenotypeIDs"]

# additional 5K
ped_addit = pd.read_csv("raw_pedigree_part2.csv", 
                        dtype=str, na_values=[" ", "", "None"], 
                        usecols=range(12)).query("id.notna().values")

# an actual genotypes
def read_fam_file(file_path:str) -> set:
    """
    Read a .fam file and extract a set of IDs
    """
    fam_df = pd.read_csv(file_path, delim_whitespace=True, header=None)
    ids = set(fam_df[1].unique())
    return ids

fam_11k_ids = read_fam_file("/home/kseniia/projects/data/raw_data/TB_11K.fam")
fam_6k_ids = read_fam_file("/home/kseniia/projects/data/raw_data/TB_6K.fam")
bed_ids = fam_11k_ids.union(fam_6k_ids)

if __name__ == "__main__":
