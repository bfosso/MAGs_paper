# Benchmarking short and Long Read Sequencing Technologies for Metagenomic Profiling of Microbiomes

Grazia Visci 1†, Elisabetta Notario 2†, Giuseppe Defazio 1†, Mariano Francesco Caratozzolo 2, Bruno Fosso 1*, Marinella Marzano 2*, Graziano Pesole 1,2,3

1) Department of Biosciences, Biotechnology and Environment, University of Bari Aldo Moro, 70125 Bari, Italy.
2) Institute of Biomembranes, Bioenergetics and Molecular Biotechnologies, Consiglio Nazionale delle Ricerche, 70126 Bari, Italy.
3) Consorzio Interuniversitario Biotecnologie, 34148 Trieste, Italy.

† These authors contributed equally to this work.<br/>
\* Correspondence: bruno.fosso@uniba.it (BF); m.marzano@ibiom.cnr.it (MM)

DOI: https://doi.org/10.21203/rs.3.rs-7581938/v1

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

## 2) Assembly evaluation, binning and bin refinement

a) metaQUAST (v5.2.0) 
```
metaquast.py contigs_1 contigs_2 ... -r reference_1,reference_2,reference_3
```
b) Seqkit (v2.8.2)
```,
seqkit stats -j10 -t -a
```




