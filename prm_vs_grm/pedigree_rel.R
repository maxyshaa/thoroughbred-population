library(pedsuite)
library(dplyr)

# Read pedigree data from CSV file
ped_df = read.csv("/home/kseniia/projects/phd_thrg/merged_tables/merged_ped_no_dupl.csv", na.strings = c("", NA)) # this all that have id bed
ped_df = ped_df[!is.na(ped_df$id_bed), ]

# Indeed, I have some duplicates in my table... I need to fix that in my code before
# Identify and remove duplicates
# tab = table(ped_df$id)
# dup_ids = names(tab[tab > 1])
# dup_dups = NULL
# for (i in dup_ids) dup_dups = c(dup_dups, which(ped_df$id == i)[-1])
# ped_df = ped_df[-dup_dups,]

ped_df <- ped_df %>%
  group_by(id) %>%
  arrange(desc(batchID)) %>%
  slice_head(n = 1) %>%
  ungroup()

# Replace NA in sex to 0
ped_df$sex[is.na(ped_df$sex)] = 0
ped_df$sex[is.na(ped_df$sire_id)] = 0
ped_df$sex[is.na(ped_df$dam_id)] = 0

# Add unobserved parents as founders
missing.sires = unique(ped_df$sire_id[!(ped_df$sire_id %in% ped_df$id)])
missing.dams = unique(ped_df$dam_id[!(ped_df$dam_id %in% ped_df$id)])
tmp1 = matrix(NA, length(missing.sires), ncol(ped_df))
tmp2 = matrix(NA, length(missing.dams), ncol(ped_df))
tmp1[, c(1, 4, 5, 7)] = cbind(missing.sires, 0, 0, 1)
tmp2[, c(1, 4, 5, 7)] = cbind(missing.dams, 0, 0, 2)
colnames(tmp1) = colnames(tmp2) = colnames(ped_df)
ped_founders = rbind(ped_df, tmp1, tmp2)
ped_founders = ped_founders[!is.na(ped_founders$id),]

# Calculate pedigree relationship matrix (PRM)
x = ped(ped_founders$id, ped_founders$dam_id, ped_founders$sire_id, ped_founders$sex)
PRM = kinship(x)
# Write PRM to a text file
write.table(PRM, file = "prm.txt")
# R --max-ppsize=1000000 -f