import os
import sys
import subprocess, shlex
from multiprocessing import Pool
import pandas as pd

km_classification = sys.argv[1]
genomes_folder = sys.argv[2]

ref_genomes = ["Streptococcus_mutans_ATCC_700610.fa", "Streptococcus_agalactiae_ATCC_BAA_611.fa",
               "Staphylococcus_epidermidis_ATCC_12228.fa", "Staphylococcus_aureus_subsp_aureus_ATCC_BAA_1556.fa",
               "Schaalia_odontolytica_ATCC_17982.fa", "Rhodobacter_sphaeroides_ATCC_17029.fa",
               "Pseudomonas_aeruginosa_ATCC_9027.fa", "Porphyromonas_gingivalis_ATCC_33277.fa",
               "Phocaeicola_vulgatus_ATCC_8482.fa", "Neisseria_meningitidis_ATCC_BAA_335.fa",
               "Lactobacillus_gasseri_ATCC_33323.fa", "Helicobacter_pylori_ATCC_700392.fa",
               "Escherichia_coli_ATCC_700926.fa", "Enterococcus_faecalis_ATCC_47077.fa",
               "Deinococcus_radiodurans_ATCC_BAA_816.fa", "Cutibacterium_acnes_ATCC_11828.fa",
               "Clostridium_beijerinckii_ATCC_35702.fa", "Bifidobacterium_adolescentis_ATCC_15703.fa",
               "Bacillus_pacificus_ATCC_10987.fa", "Acinetobacter_baumannii_ATCC_17978.fa"]

df = pd.read_csv(km_classification, header=0, index_col=0, sep=",")
print(df.shape)
ref_list = []
for ref in ref_genomes:
    tosearch = ref.split("_")[:2]
    if tosearch[1] == "pacificus":
        tosearch[1] = "cereus"
    if tosearch[0] == "Rhodobacter":
        tosearch[0] = "Cereibacter"
    matched_bin = [g for g, c in zip(df["bin"].to_list(), df["organism_name"].to_list()) if
                   all([c.find(tosearch[0]) > -1, c.find(tosearch[1]) > -1, g.find("SRR11606871") == -1])]
    ref_list_name = f"{ref.split('.')[0]}_genomes.lst"
    matched_bin.append(ref)
    with open(ref_list_name, "w") as f:
        f.write("\n".join(map(lambda x: os.path.join(genomes_folder,x), set(matched_bin))))
    ref_list.append(ref_list_name)


def smash_exec(ref_list):
    cmd = shlex.split(f"mash sketch -p 20 -k 21 -s 15000 -l {ref_list} -o {ref_list.replace('.lst', '.sketch')}")
    p = subprocess.Popen(cmd)
    p.wait()
    cmd = shlex.split(f"mash dist -p 20 {ref_list.replace('.lst', '.sketch')}.msh {ref_list.replace('.lst', '.sketch')}.msh")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    with open(ref_list.replace('.lst', '.dist'), "w") as f:
        f.write(p.stdout.read().decode())


with Pool(processes=5) as pool:
    future = pool.map(smash_exec, ref_list)

