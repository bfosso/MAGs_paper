import os
import sys
import argparse
import argcomplete
import subprocess
import shlex


def be_parser():
    parser = argparse.ArgumentParser(
        description="parallely execute bakta",
        prefix_chars="-")
    parser.add_argument("-b", "--bin", type=str,
                        help="bin fasta", action="store",
                        required=True)
    parser.add_argument("-p", "--processors", type=str, help="Reference column",
                        action="store", required=True)
    argcomplete.autocomplete(parser)
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return parser.parse_args()


def sam_processing(samfile, cpu):
    bam = samfile.replace('.sam', '.bam')
    bam_sorted = bam.replace('.bam', '.sorted.bam')
    if not os.path.exists(bam):
        cmd = shlex.split(
            f"samtools view -@{cpu} -bS -o {bam} {samfile}")
        p = subprocess.Popen(cmd)
        p.wait()
        if p.returncode != 0:
            raise subprocess.CalledProcessError(p.returncode, cmd)
        else:
            os.system(f"rm {sam}")
    cmd = shlex.split(
        f"samtools sort -@{cpu} -o {bam_sorted} {bam}")
    p = subprocess.Popen(cmd)
    p.wait()
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmd)
    cmd = shlex.split(
        f"samtools index {bam_sorted}")
    p = subprocess.Popen(cmd)
    p.wait()
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmd)
    cmd = shlex.split(
        f"samtools coverage --ff 1284 -o {samfile.replace('.sam', '.coverage')}  -d 0 {bam_sorted}")
    p = subprocess.Popen(cmd)
    p.wait()


def illumina_mapping(bin_fasta, cpu):
    r1 = "/lustre/home/boss/mock_MAGs/MOCK_20_strain_data/Illumina_megahit/S_Mock_20_strain_S26_filtered_1.fastq"
    r2 = "/lustre/home/boss/mock_MAGs/MOCK_20_strain_data/Illumina_megahit/S_Mock_20_strain_S26_filtered_2.fastq"
    sam = os.path.basename(bin_fasta).replace('.fa', '.sam')
    if not os.path.exists(sam):
        cmd = shlex.split(f"minimap2 -a -t {cpu} -x sr {bin_fasta} {r1} {r2} -o {sam}")
        p = subprocess.Popen(cmd)
        p.wait()
        if p.returncode == 0:
            return sam
        else:
            return None
    elif os.stat(sam).st_size == 0:
        cmd = shlex.split(f"minimap2 -a -t {cpu} -x sr {bin_fasta} {r1} {r2}-o {sam}")
        p = subprocess.Popen(cmd)
        p.wait()
        if p.returncode == 0:
            return sam
        else:
            return None
    else:
        return sam

def pacbio_mapping(bin_fasta, cpu):
    r1 = "/lustre/home/boss/mock_MAGs/MOCK_20_strain_data/PacBio_Jul24/trimmed_hifi.fastq.gz"
    sam = os.path.basename(bin_fasta).replace('.fa', '.sam')
    if os.path.exists(f"/lustre/home/boss/mock_MAGs/MOCK_20_strain_data/genomes/bin_quantification/coverage_folder/{sam.replace('.sam','.coverage')}"):
        sys.exit(0)
    if not os.path.exists(sam):
        cmd = shlex.split(f"minimap2 -a -t {cpu} -x map-hifi {bin_fasta} {r1} -o {sam}")
        p = subprocess.Popen(cmd)
        p.wait()
        if p.returncode == 0:
            return sam
        else:
            return None
    elif os.stat(sam).st_size == 0:
        cmd = shlex.split(f"minimap2 -a -t {cpu} -x map-hifi {bin_fasta} {r1} -o {sam}")
        p = subprocess.Popen(cmd)
        p.wait()
        if p.returncode == 0:
            return sam
        else:
            return None
    else:
        return sam



def nanopore_mapping(bin_fasta, cpu):
    r1 = "/lustre/home/boss/mock_MAGs/MOCK_20_strain_data/nanopore_Mar24_R10/trimmed_nanopore_March24_raw_data.fastq.gz"
    sam = os.path.basename(bin_fasta).replace('.fa', '.sam')
    if not os.path.exists(sam):
        cmd = shlex.split(f"minimap2 -a -t {cpu} -x map-ont {bin_fasta} {r1} -o {sam}")
        p = subprocess.Popen(cmd)
        p.wait()
        if p.returncode == 0:
            return sam
        else:
            return None
    elif os.stat(sam).st_size == 0:
        cmd = shlex.split(f"minimap2 -a -t {cpu} -x map-ont {bin_fasta} {r1} -o {sam}")
        p = subprocess.Popen(cmd)
        p.wait()
        if p.returncode == 0:
            return sam
        else:
            return None
    else:
        return sam


if __name__ == '__main__':
    args = be_parser()
    mags, cpu = args.bin, args.processors
    tech = os.path.basename(mags).lower().split('_')[0]
    if tech == 'ill':
        sam = illumina_mapping(mags, cpu)
    elif tech == 'pacbio':
        sam = pacbio_mapping(mags, cpu)
    elif tech == 'nanopore':
        sam = nanopore_mapping(mags, cpu)
    else:
        sys.exit("Reference bin --> Not Processed")
    if sam:
        sam_processing(sam, cpu)
    else:
        raise Exception(f"{mags} was not analyzed")
