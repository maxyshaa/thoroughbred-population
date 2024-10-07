import os
import pandas as pd
from preprocessing.load_data import read_pedigree_sheets, get_pedigree_csv, read_fam
from preprocessing.filter_geno import filter_by_fam, filter_by_chip, update_idmatch
from preprocessing.clean_data import clear_colour, fix_logic
from preprocessing.match_n_merge import merge_1stdataframes, clear_ped_additional, modifying_countries, concat_peds
from preprocessing.utils import save_file, clear_string_val


geno_path = "/home/kseniia/projects/data/raw_data/"
results_path = "/home/kseniia/projects/github/pedigree_analysis/results"

country_unific_dict = {"australia": "AUS",
                       "aus": "AUS",
                       "argentina": "ARG",
                       "arg": "ARG",
                       "brazil": "BRZ",
                       "brz": "BRZ",
                       "canada": "CAN",
                       "can": "CAN",
                       "great britain": "GB",
                       "germany":"GER",
                       "united kingdown": "GB",
                       "gb": "GB",
                       "ireland": "IRL",
                       "IRELAND": "IRL",
                       "irl": "IRL",
                       "ire":"IRL",
                       "ity":"ITY",
                       "New Zealand": "NZ",
                       "new zealand": "NZ",
                       "nz": "NZ",
                       "South Africa": "SAF",
                       "south africa": "SAF",
                       "saf": "SAF",
                       "France": "FR",
                       "france": "FR",
                       "fr": "FR",
                       "Germany": "GER",
                       "ger": "GER",
                       "Japan": "JAP",
                       "japan": "JAP",
                       "jan": "JAP",
                       "Uruguay": "URU",
                       "uruguay": "URU",
                       "uru": "URU",
                       "United Arab Emirates": "UAE",
                       "united arab emirates": "UAE",
                       "uae": "UAE",
                       "usa": "USA"}

col_order = ["horse_id", "status", "horse_name", "sire_id", 
         "dam_id", "YOB", "MOB", "sex", "colour", "COB",
         "equinome_id", "bed_id", "batch", "snp_chip", 
         "country_reported", "genotyped"]

if os.path.exists(os.path.join(results_path, "bedids2exclude.txt")):
    os.remove(os.path.join(results_path, "bedids2exclude.txt"))
    print("bedid2exclude has been removed")

def main() -> None:

    # initializing a list to hold removed bed_ids
    removed_bedids = []

    ### Step 1: Load all data
    # 1st part of pedigree
    pedid_match, ped_df, geno_id = read_pedigree_sheets(
        os.path.join("data/raw_pedigree_part1.xlsx")
        )
    # 2nd part of pedigree
    ped_addit = get_pedigree_csv(
        os.path.join("data/raw_pedigree_part2.csv")
        )
    # plink fam files
    fam_11k_ids = read_fam(os.path.join(geno_path, "TB_11K.fam"))
    fam_6k_ids = read_fam(os.path.join(geno_path, "TB_6K.fam"))
    bed_ids = fam_11k_ids.union(fam_6k_ids)

    # umbigous individuals
    # sameid_diff_names = pd.read_csv("problems/pedid_dup_diff_names.csv")["Equinome ID"]
    # Already removed from raw_dataset after review

    ### Step 2: Clean 1st pedigree DataFrame
    ped_cleaned = fix_logic(clear_colour(init_file=ped_df, col_name="colour"))
    print("----------Cleaning of 1st pedigree has finished----------")

    ### Step 3: Clean genotype information and remove duplicates based on SNPchip
    geno_id_chip_filtered = filter_by_chip(
        filter_by_fam(geno_id, "id", bed_ids), 
        snp_col="SNPChip", batch_col="batchID", equinomeid="equinomeID", bedid="id", 
        removed_bedids=removed_bedids)
    print("----------Filtering on presence in fam and prioritizing on chip info of genotypes has finished; geno_id has updated for 1st pedigree----------")

    ped_addit_chip_filtered = filter_by_chip(
        filter_by_fam(ped_addit, "id", bed_ids), 
        snp_col="SNPChip", batch_col="batchID", equinomeid="equinomeID", bedid="id", 
        removed_bedids=removed_bedids)
    print("----------Filtering on presence in fam and prioritizing on chip info of genotypes has finished; geno_id has updated for 2nd pedigree----------")

    # Step 4: Update pedid_match with the cleaned geno_id
    pedid_match_chip_filtered = update_idmatch(pedid_match=pedid_match, 
                                               new_geno=geno_id_chip_filtered)
    print("----------pedid_match has updated: no extra SNPchips----------")

    ### Step 5: Handle duplicated horse_id entries with different EquinomeID [only for the first ped_df]

    # I have 1011 rows that are the same horse_id but they have different EquinomeID
    # 111 of them have different names too
    # what I did here was manually: I captured those from pedid match df rows assigned to a single horse_id but having different names
    # I checked manually if those Equinome ID are present in quick run king on raw TB_11K.bed --duplicate, removed same horses from the df
    # So I don't want to include those genotypes if I don't know what horse is that, I have file saved in problems, it needs to be resolved
    # for now I am removing them before we prioritized by chip diff equinome IDs

    # pedid_match_chip_filtered = pedid_match_chip_filtered[~pedid_match_chip_filtered["Equinome ID"].isin(sameid_diff_names)]
    # geno_id_chip_filtered = geno_id_chip_filtered[~geno_id_chip_filtered["equinomeID"].isin(sameid_diff_names)]
    # print("----------Wrong assigned equinomeIDs were removed from pedid_match and geno_id_nodup----------")

    # finding duplicates by horse_id and getting their equinome id
    duplicated_horse_ids = pedid_match_chip_filtered[pedid_match_chip_filtered["horse_id"].duplicated(keep=False)]
    dup_merged = duplicated_horse_ids.merge(geno_id_chip_filtered, left_on="Equinome ID", 
                                            right_on="equinomeID", how="left")
    
    # filtering those equinome id by chip priority
    no_eqdup = filter_by_chip(dup_merged, "SNPChip", "batchID", "horse_id", "id", removed_bedids)
    removed_ids = dup_merged[~dup_merged["Equinome ID"].isin(no_eqdup["Equinome ID"])]["Equinome ID"].tolist()
    
    # update new_geno
    geno_id_nodup = geno_id_chip_filtered[~geno_id_chip_filtered["equinomeID"].isin(removed_ids)]
    print("----------geno_id has updated: no extra equinomeID per horse----------")

    # update pedid_match
    pedid_match_nodup = update_idmatch(pedid_match=pedid_match_chip_filtered, new_geno=geno_id_nodup)
    print("----------pedid_match has updated: no extra equinomeID per horse----------")

    # Step 6: Modifying columns and prepare pedigres
    ped_1stmerged = merge_1stdataframes(ped_df=ped_cleaned, 
                                         pedid_match=pedid_match_nodup, 
                                         geno_id=geno_id_nodup)
    ped_addit_prep = clear_ped_additional(ped_addit_chip_filtered)
    
    ped_1stmerged, ped_addit_prep = modifying_countries(ped_1stmerged, ped_addit_prep,
                                       country_unific_dict)
    
    # Step 7: Concatenating 2 datasets
    final_pedigree = concat_peds(ped_1stmerged, ped_addit_prep, col_order)
  
    # saving results
    save_file(final_pedigree, "results/", "cleaned_pedigree.csv")

    # Write all removed bedids to a file
    with open("results/bedids2exclude.txt", 'w') as f:
        for bedid in removed_bedids:
            f.write(f"{bedid} {bedid}\n")

if __name__ == "__main__":
    main()