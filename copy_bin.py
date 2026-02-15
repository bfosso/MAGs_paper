import os

folder_list = {"PacBio_flye":"../../pacbio_data/flye_pacbio/BIN_REFINEMENT_c20_x50/metawrap_20_50_bins",
               "PacBio_metaMDBG": "../../pacbio_data/metamdbg_pacbio/BIN_REFINEMENT_c20_x50/metawrap_20_50_bins",
               "Nanopore_flye": "../../nanopore_data/flye_nanopore/BIN_REFINEMENT_c20_x50/metawrap_20_50_bins",
               "Nanopore_metaMDBG": "../../nanopore_data/metamdbg_nanopore/BIN_REFINEMENT_c20_x50/metawrap_20_50_bins",
               "Ill_megahit":"../../Illumina_data/megahit_data/BIN_REFINEMENT_c20_x50/metawrap_20_50_bins",
               "Ill_metaSPAdes":"../../Illumina_data/metaspades_data/BIN_REFINEMENT_c20_x50/metawrap_20_50_bins"}

for dataset,folder in folder_list.items():
    for fasta in os.listdir(folder):
        if fasta.endswith(".fa"):
            _fasta = f"{dataset}_{fasta}"
            os.system(f"cp {os.path.join(folder,fasta)} {_fasta}")