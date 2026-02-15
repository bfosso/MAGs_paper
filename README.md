Benchmarking short and Long Read Sequencing Technologies for Metagenomic Profiling of Microbiomes
=====

Content:
- [Introduction](#introduction)
- [Environment Settings and Data download](#environment-settings-and-data-download-)
- [Mapping on ATCC reference genomes and coverage and sequencing depth estimation](#mapping-on-atcc-reference-genomes-and-coverage-and-sequencing-depth-estimation)
- []()


# Introduction
Grazia Visci 1†, Elisabetta Notario 2†, Giuseppe Defazio 1†, Mariano Francesco Caratozzolo 2, Bruno Fosso 1*, Marinella 
Marzano 2*, Graziano Pesole 1,2,3

1) Department of Biosciences, Biotechnology and Environment, University of Bari Aldo Moro, 70125 Bari, Italy.
2) Institute of Biomembranes, Bioenergetics and Molecular Biotechnologies, Consiglio Nazionale delle Ricerche, 70126 
3) Bari, Italy.
3) Consorzio Interuniversitario Biotecnologie, 34148 Trieste, Italy.

† These authors contributed equally to this work.<br/>
\* Correspondence: bruno.fosso@uniba.it (BF); m.marzano@ibiom.cnr.it (MM)

-------
Currently, the manuscript is available as _pre-print_ at DOI: [https://doi.org/10.21203/rs.3.rs-7581938/v1](https://doi.org/10.21203/rs.3.rs-7581938/v1).  

-------
This repository collects bioinformatics approaches for benchmarking sequencing technologies in microbiome data assembly 
used for this manuscript.

# Environment Settings and Data download 
### 1) Create the conda environment required to reproduce data analysis
To properly installa and configure the required virtual environments (VEs) you need to install the **CONDA** manager.  
You can find the most appropriate info for you system [here](https://docs.conda.io/projects/conda/en/latest/index.html).  
In the `VE_yaml` folder are available the different emplyed VEs. To generate it on you system, please use the following 
line:  
```
conda env create -f environment.yml
```
Please change `environment.yml` with the specific yaml file you want to use.  

### 2) Download data from ENA database
All raw sequencing data are available in under the bioproject [PRJEB89875](https://www.ebi.ac.uk/ena/browser/view/PRJEB89875).  
In **Table 1** are shown the available files.  

| Sequencing Technology |    Platform    |     Data Accession Numner    |   Layout   |
|:---------------------:|:--------------:|:----------------------------:|:----------:|
|     **Illumina**      | _Novaseq 6000_ |          ERR15084348         | Paired End |
|     **Nanopore**      |   _GridION_    |          ERR15084349         | Single End |
|      **PacBio**       |       _Sequel IIe System_       | ERR15084350   | Single End |

## Raw data trimming, mapping on reference genomes, assembly and binning
### 1 Illumina data analysis and assembly
#### Prepare the working directory for Illumina data:  
```
mkdir -p Illumina_data && cd Illumina_data

# Put the downloaded Illumina data in this folder
# mv /DOWNLOAD/PATH/ERR15084348_*.fastq.gz .
```
#### Data quality evaluation with _*FastQC* (v0.11.9) evaluation of reads_
#### _Trimmomatic (v0.11.9)_
```
conda activate assembly

sample=ERR15084348
forward=ERR15084348_1.fastq.gz
reverse=ERR15084348_2.fastq.gz

trimmomatic PE \
-phred33 \
$forward \
$reverse \
${sample}_forward_paired.fq.gz \
${sample}_forward_unpaired.fq.gz \
${sample}_reverse_paired.fq.gz \
${sample}_reverse_unpaired.fq.gz \
-summary ${sample}_trimmomatic.summary.log \
ILLUMINACLIP:${CONDA_PREFIX}/envs/assembly/share/trimmomatic-0.39-2/adapters/NexteraPE-PE.fa:3:30:10 \
LEADING:3 \
TRAILING:3 \
SLIDINGWINDOW:4:15 \
MINLEN:50 
```

#### Seqkit application
```
seqkit stats -j10 -t -a ERR15084348_1.fastq.gz ${sample}_forward_unpaired.fq.gz
```

#### _Activate metawrap environment and prepare data_
```
conda activate metawrap-env 

# metawrap requires uncompressed files
gzip -d *fastq.gz
forward_trimmed_data=${pwd}/${sample}_forward_paired.fq.gz 
reverse_trimmed_data=${pwd}/${sample}_reverse_paired.fq.gz
```
#### _Assembly with megaHIT (v1.2.9)_
```
mkdir -p megahit_data && cd megahit_data

metawrap assembly \
    -1  $forward_trimmed_data \
    -2 $reverse_trimmed_data \
    -m 50 \
    -t 50 \
    --megahit \
    -o megahit_assembly
    
cd ..
```
#### _Assembly with metaSPAdes (v3.15.5)_
```
mkdir -p metaspades_data && cd metaspades_data
mkdir -p TMP
```
Prepare the `dataset.yml` file as follow:  
```
- "left reads":
  - "PATH_to_forward_reads"
  "orientation": "fr"
  "right reads":
  - "PATH_to_reverese_reads"
  "type": "paired-end"
```
Apply SPAdes:  
```
spades.py --meta \
    -o metaspades_assembly_result \
    -k 21,29,39,59,79,99,119 \
    -t 35  --dataset dataset.yml \
    -m 500 \
    --phred-offset 33 \
    --tmp-dir ${pwd}/TMP
    
cd ..
```

### 2 Nanopore data analysis and assembly
#### Prepare the working dir for Nanopore data:  
```
mkdir -p nanopore_data && cd nanopore_data

# Put the downloaded Nanopore data in this folder
# mv /DOWNLOAD/PATH/ERR15084349.fastq.gz .
```
#### _pycoQC evaluation of reads_<br/>
#### _Porechop abi (v0.5.0) for adapters trimming_
```
conda activate NANOPORE

porechop_abi --ab_initio --format fastq.gz -i ERR15084349.fastq.gz -o ERR15084349_trimmed.fastq.gz
```
#### Seqkit application
```
seqkit stats -j10 -t -a ERR15084349.fastq.gz ERR15084349_trimmed.fastq.gz
```


#### _Assembly with metaFlye (v2.9.2-b1786)_
```
mkdir -p flye_nanopore && cd flye_nanopore 

flye --nano-raw ERR15084349_trimmed.fastq.gz \
 -o assembly \
 -t 50 \
 -i 5 --meta
 
 cd ..
```
#### _Assembly with metaMDBG (v1.0)_
```
mkdir -p metamdbg_nanopore && cd metamdbg_nanopore 

metaMDBG asm --out-dir ./assembly/ \
     --in-ont ERR15084349_trimmed.fastq.gz \
     --threads 50

cd ..
```

### 3 PacBio data analysis and assembly
#### Prepare the working dir for PacBio data:  
```
mkdir -p pacbio_data && cd pacbio_data

# Put the downloaded Nanopore data in this folder
# mv /DOWNLOAD/PATH/ERR15084350.fastq.gz .
```
#### _FastQC (v0.11.9) evaluation of reads_<br/>
#### _Cutadapt (v4.5) for adapter trimming_
```
cutadapt --overlap 35 -e 0.1 \
        --discard -j 5 --revcomp \
        -b file:pacbio_adapter.fa \
        -o ERR15084350.trimmed_hifi.fastq \
        ERR15084350.fastq.gz
```

#### Seqkit application
```
seqkit stats -j10 -t -a ERR15084350.fastq.gz ERR15084350.trimmed_hifi.fastq
```

#### _metaFlye (v2.9.2-b1786)_
```
conda activate NANOPORE

mkdir -p flye_pacbio && cd flye_pacbio

flye --pacbio-hifi ../RR15084350.trimmed_hifi.fastq \
 -o assembly \
 -t 50 \
 -i 5 --meta
 
 cd ..
```
#### metaMDBG (v1.0)
```
conda activate NANOPORE

mkdir -p metamdbg_pacbio && cd metamdbg_pacbio 

metaMDBG asm --out-dir ./assembly/ \
    --in-hifi ../ERR15084350.trimmed_hifi.fastq \
    --threads 50
    
cd ..
```

## Mapping on ATCC reference genomes and coverage and sequencing depth estimation
Sequencing data were mapped on the 20 prokaryotic strain reference genomes by using _minimap2_ (v2.26-r1175).  
First **ATCC reference genome** should be downloaded from [ATCC Genome Portal](https://genomes.atcc.org).
```
mkdir -p ATCC_Mock_20_Strain_ref && cd ATCC_Mock_20_Strain_ref

#download here fasta file

cat *fasta > genomes.fa
```

### _Illumina_ 
```
cd Illumina_data
conda activate NANOPORE

minimap2 -ax sr -o raw_reads_mapping.sam \
   -L -t 30 ../ATCC_Mock_20_Strain_ref/genomes.fa \
   ERR15084348_forward_paired.fastq \
   ERR15084348_reverse_paired.fastq
conda deactivate

conda activate RNASEQ

samtools view -@ 15 -bS ../mock_MAGs/Illumina/raw_reads_mapping.sam -o ../mock_MAGs/Illumina/raw_reads_mapping.bam
samtools sort -@ 15 ../mock_MAGs/Illumina/raw_reads_mapping.bam  -o ../mock_MAGs/Illumina/raw_reads_mapping.sorted.bam
samtools index ../mock_MAGs/Illumina/raw_reads_mapping.sorted.bam

samtools coverage --ff 1284 \
    -o Illumina_cov.tsv \
    -d 0 raw_reads_mapping.sorted.bam
```

### Nanopore 
```
cd nanopore_data

conda activate NANOPORE

minimap2 -ax map-ont -o trimmed_reads_mapping.sam \
    -L -t 30 ../ATCC_Mock_20_Strain_ref/genomes.fa \
    ERR15084349_trimmed.fastq.gz

conda activate RNASEQ
samtools view -@ 15 -bS trimmed_reads_mapping.sam -o trimmed_reads_mapping.bam
samtools sort -@ 15 trimmed_reads_mapping.bam -o trimmed_reads_mapping.sorted.bam
samtools index trimmed_reads_mapping.sorted.bam

samtools coverage --ff 1284 \
    -o nanopore_Mar24_R10_cov.tsv \
    -d 0 trimmed_reads_mapping.sorted.bam
```

### PacBio
```
cd pacbio_data

conda activate NANOPORE

minimap2 -ax map-hifi -o genome_check.sam -L -t 5 \
    -H ../ATCC_Mock_20_Strain_ref/genomes.fa \
     ERR15084350.trimmed_hifi.fastq

conda activate RNASEQ
samtools view -@ 15 -bS genome_check.sam -o /genome_check.bam
samtools sort -@ 15 genome_check.bam  -o genome_check.sorted.bam
samtools index genome_check.sorted.bam

samtools coverage --ff 1284 \
    -o PacBio_Jul24_cov.tsv \
    -d 0 genome_check.sorted.bam
```

## Assembly evaluation, binning and bin refinement

### Illumina
#### metaQUAST (v5.2.0) 
```
cd Illumina_data
conda activate NANOPORE

metaquast -o megahit_data/metaquast_Illumina_megahit_assembly -t 30 \
    -l "Mock 20 Strain Illumina megahit Assembly" \
    -1 ERR15084348_forward_paired.fastq \
    -2 ERR15084348_reverse_paired.fastq \
    -r ../mock_MAGs/ATCC_Mock_20_Strain_ref/Acinetobacter_baumannii_ATCC_17978.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Deinococcus_radiodurans_ATCC_BAA_816.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Neisseria_meningitidis_ATCC_BAA_335.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Schaalia_odontolytica_ATCC_17982.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Bacillus_pacificus_ATCC_10987.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Enterococcus_faecalis_ATCC_47077.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Phocaeicola_vulgatus_ATCC_8482.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Staphylococcus_aureus_subsp_aureus_ATCC_BAA_1556.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Bifidobacterium_adolescentis_ATCC_15703.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Escherichia_coli_ATCC_700926.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Porphyromonas_gingivalis_ATCC_33277.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Staphylococcus_epidermidis_ATCC_12228.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Clostridium_beijerinckii_ATCC_35702.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Helicobacter_pylori_ATCC_700392.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Pseudomonas_aeruginosa_ATCC_9027.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Streptococcus_agalactiae_ATCC_BAA_611.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Cutibacterium_acnes_ATCC_11828.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Lactobacillus_gasseri_ATCC_33323.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Rhodobacter_sphaeroides_ATCC_17029.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Streptococcus_mutans_ATCC_700610.fasta \
    --rna-finding megahit_data/megahit_assembly/final_assembly.fasta
    
metaquast -o metaspades_data/metaquast_Illumina_metaspades_assembly -t 30 \
    -l "Mock 20 Strain Illumina megahit Assembly" \
    -1 ERR15084348_forward_paired.fastq \
    -2 ERR15084348_reverse_paired.fastq \
    -r ../mock_MAGs/ATCC_Mock_20_Strain_ref/Acinetobacter_baumannii_ATCC_17978.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Deinococcus_radiodurans_ATCC_BAA_816.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Neisseria_meningitidis_ATCC_BAA_335.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Schaalia_odontolytica_ATCC_17982.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Bacillus_pacificus_ATCC_10987.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Enterococcus_faecalis_ATCC_47077.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Phocaeicola_vulgatus_ATCC_8482.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Staphylococcus_aureus_subsp_aureus_ATCC_BAA_1556.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Bifidobacterium_adolescentis_ATCC_15703.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Escherichia_coli_ATCC_700926.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Porphyromonas_gingivalis_ATCC_33277.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Staphylococcus_epidermidis_ATCC_12228.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Clostridium_beijerinckii_ATCC_35702.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Helicobacter_pylori_ATCC_700392.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Pseudomonas_aeruginosa_ATCC_9027.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Streptococcus_agalactiae_ATCC_BAA_611.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Cutibacterium_acnes_ATCC_11828.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Lactobacillus_gasseri_ATCC_33323.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Rhodobacter_sphaeroides_ATCC_17029.fasta,../mock_MAGs/ATCC_Mock_20_Strain_ref/Streptococcus_mutans_ATCC_700610.fasta \
    --rna-finding metaspades_data/metaspades_assembly_result/contigs.fasta
```

#### Binning & Refinement
metaWRAP: metaBAT2 (v2.12.1), MaxBin2 (2.2.4), CONCOT (v1.0.0)
```
cd megahit_data

metawrap binning -o INITIAL_BINNING -t 96 \
    -a megahit_assembly/final_assembly.fasta \
    -t 50 \
    -m 50 \
    -o INITIAL_BINNING \
    --universal \
    --run-checkm $single \
    --metabat2 \
    --maxbin2 \
    --concoct ../ERR15084348_forward_paired.fastq ../ERR15084348_reverse_paired.fastq
    
metawrap bin_refinement -o BIN_REFINEMENT_c90_x5 \
    -t 96 \
    -A INITIAL_BINNING/metabat2_bins/ \
    -B INITIAL_BINNING/maxbin2_bins/ \
    -C INITIAL_BINNING/concoct_bins/ \
    -c 90 \
    -x 5
    
cd ../metaspades_data

metawrap binning -o INITIAL_BINNING -t 96 \
    -a metaspades_assembly_result/contigs.fasta \
    -t 50 \
    -m 50 \
    -o INITIAL_BINNING \
    --universal \
    --run-checkm $single \
    --metabat2 \
    --maxbin2 \
    --concoct ../ERR15084348_forward_paired.fastq ../ERR15084348_reverse_paired.fastq
    
metawrap bin_refinement -o BIN_REFINEMENT_c90_x5 \
    -t 96 \
    -A INITIAL_BINNING/metabat2_bins/ \
    -B INITIAL_BINNING/maxbin2_bins/ \
    -C INITIAL_BINNING/concoct_bins/ \
    -c 90 \
    -x 5
```


## 4) MAGs comparison to reference genomes
a) MASH (v2.3)
```
mash sketch -k 21 -s 15000
```

b) GTDB-tk (v2.1.1)
```
gtdbtk classify_wf --genome_dir ./refined \
                   --out_dir ./gtdbtk_refined \
                   --cpus 10 \
                   -x gz
```

c) kMetaShot (v2.0)

```
kMetaShot_classifier_NV.py -b ./refined \
                           -r kMetaShot_reference.h5 \
                           -p 10 \
                           -o kMetaShot_refined
```

## 5) MAGs Dereplication
dRep (v3.5.0)
```
dRep dereplicate --ignoreGenomeQuality --genomeInfo
```

## 6) MAGs Genes Annotation
Bakta (v1.4.0)
```
bakta --min-contig-length 200 --db ./reference/bakta_db/db --output ./annotation_on_drep --prefix annotation_on_drep --threads 10 ./dereplicated_genomes
```

## 7) MAGs quantification

Sequencing data were mapped MAGs. 

a) minimap2 (v2.26-r1175)
_Illumina_ 
```
minimap2 -ax sr
```
_Nanopore_
```
minimap2 -ax map-ont -L
```
_PacBio_ 
```
minimap2 -ax map-hifi -L
```
b) samtools (v1.3.1)<br/>
```
# SAM to BAM conversion
samtools view

# BAM sorting
samtools sort

# Filter for properly paired alignments and secondary elimination
samtools view -ff 1284 

# Coverage computation without any limit
samtools coverage -d 0
```


