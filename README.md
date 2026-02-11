# Benchmarking short and Long Read Sequencing Technologies for Metagenomic Profiling of Microbiomes

Grazia Visci 1†, Elisabetta Notario 2†, Giuseppe Defazio 1†, Mariano Francesco Caratozzolo 2, Bruno Fosso 1*, Marinella Marzano 2*, Graziano Pesole 1,2,3

1) Department of Biosciences, Biotechnology and Environment, University of Bari Aldo Moro, 70125 Bari, Italy.
2) Institute of Biomembranes, Bioenergetics and Molecular Biotechnologies, Consiglio Nazionale delle Ricerche, 70126 Bari, Italy.
3) Consorzio Interuniversitario Biotecnologie, 34148 Trieste, Italy.

† These authors contributed equally to this work.<br/>
\* Correspondence: bruno.fosso@uniba.it (BF); m.marzano@ibiom.cnr.it (MM)

-------
Currently the manuscript is available as _pre-print_ at DOI: [https://doi.org/10.21203/rs.3.rs-7581938/v1](https://doi.org/10.21203/rs.3.rs-7581938/v1).  

-------
This repository collects bioinformatics approaches for benchmarking sequencing technologies in microbiome data assembly used for this manuscript.

## 1) Raw data trimming, assembly and, mapping on reference genomes
### 1.1 Illumina data analysis and assembly

a) _FastQC (v0.11.9) evaluation of reads_<br/>
b) _Trimmomatic (v0.11.9)_
```
trimmomatic PE ILLUMINACLIP LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:50 
```
c) _Assembly with megaHIT (v1.2.9)_
```
megahit --k-list 21, 29, 39, 59, 79, 99, 119, 141 --k-step 10 --min_count 2
```
d) _Assembly with metaSPAdes (v3.15.5)_
```
spades.py --meta -k 21,29,39,59,79,99,119 -m 500 --phred-offset 33
```

### 1.2 Nanopore data analysis and assembly

a) _pycoQC evaluation of reads_<br/>
b) _Porechop abi (v0.5.0) for adapters trimming_
```
porechop_abi --ab_initio --format fastq.gz -i input_reads.fastq.gz -o output_reads.fastq.gz
```
c) _Assembly with metaFlye (v2.9.2-b1786)_
```
flye --nano-raw –meta -i 5
```
d) _Assembly with metaMDBG (v1.0)_
```
metaMDBG asm –in-ont
```

### 1.3 PacBio data analysis and assembly

a) _FastQC (v0.11.9) evaluation of reads_<br/>
b) _Cutadapt (v4.5) for adapter trimming_
```
cutadapt --overlap 35 -e 0.1 --discard -j 5 --revcomp
```
c) _metaFlye (v2.9.2-b1786)_
```
flye --pacbio-hifi --meta -i 5
```
d) metaMDBG (v1.0)
```
metaMDBG asm –in-hifi
```
## 2) Mapping on reference genomes and reference coverage
Sequencing data were mapped on the 20 prokaryotic strain reference genomes. 

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

## 3) Assembly evaluation, binning and bin refinement

a) metaQUAST (v5.2.0) 
```
metaquast.py contigs_1 contigs_2 ... -r reference_1,reference_2,reference_3
```
b) Seqkit (v2.8.2)
```
seqkit stats -j10 -t -a
```
c) metaWRAP: metaBAT2 (v2.12.1), MaxBin2 (2.2.4), CONCOT (v1.0.0)
```
# Binning
metawrap binning --universal --metabat2 --maxbin2 --concoct \
-a contigs.fasta \
-o not_refined \
samples_1.fastq \
samples_2.fastq

# refinement
metawrap \
bin_refinement -c 50 -x 10 \
-o refined \
-A not_refined/metabat2_bins \
-B not_refined/maxbin2_bins \
-C not_refined/concoct_bins
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



