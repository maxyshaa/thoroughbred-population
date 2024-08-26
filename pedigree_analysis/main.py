from preprocessing.load_data import read_pedigree_sheets, get_pedigree_csv, read_fam
from preprocessing.clean_data import clear_colour, fix_logic
from preprocessing.utils import save_file
import os


def main():
    # loading all data
    pedid_match, ped_df, geno_id = read_pedigree_sheets(
        os.path.join("data/raw_pedigree_part1.xlsx")
        )
    ped_addit = get_pedigree_csv(
        os.path.join("data/raw_pedigree_part2.csv")
    )
    # fam_11k_ids = read_fam(os.path.join(geno_path, "TB_11K.fam"))
    # fam_6k_ids = read_fam(os.path.join(geno_path, "TB_6K.fam"))
    # bed_ids = fam_11k_ids.union(fam_6k_ids)

    # cleaning ped_df
    ped_cleaned = fix_logic(clear_colour(init_file=ped_df, col_name="colour"))

    # 

    # saving results
    save_file(ped_cleaned, "results/", "cleaned_first_ped.csv")
    # save_file(bed_ids, res_path, "bedid_list.csv")

if __name__ == "__main__":
    main()