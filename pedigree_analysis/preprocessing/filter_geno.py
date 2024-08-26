
def extract_ped_additional(init_file: pd.DataFrame) -> pd.DataFrame:
    """This function changes the format of the additional dataset of pedigree mixed with genotypes \
        to be able to concatenate with the base one for downstream analysis.
    Args:
        init_file: dataframe to be cleared
    Returns:
        df: returns dataframe
    """
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


def concat_peds(fileone: pd.DataFrame, filetwo: pd.DataFrame) -> pd.DataFrame:
    """"""
    return

# I need to extract columns related only to pedigree thing, \
# make columns the same, add info if it's full pedigree or not, if it has genotype or not,\
#  drop duplicates from the additional pedigree
# so the output would be cleaned, combined ped file
# after some other cleaning we can add an additional column that would say \
# what genotype we took for the analysis (like corresponding id_bed or equinome id)