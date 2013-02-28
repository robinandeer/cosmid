#!/usr/bin/env python

from __future__ import print_function
import argparse
from genie.fetcher import Fetcher


def main(args):

    fetcher = Fetcher(args.email, project=args.project, force=args.force)

    if args.ensembl:
        # Get Ensembl fasta reference
        fetcher.ensembl(args.ensembl_assembly)

    if args.ccds:
        # Get the NCBI files
        fetcher.ncbi(args.ccds_release)

    if args.gatk:
        # Get all the GATK curated files
        fetcher.gatk(args.gatk_codes, version=args.gatk_version, assembly=args.gatk_assembly)

    if args.ucsc:
        # Get the RefSeq FASTA file from UCSC
        fetcher.ucsc(args.ucsc_assembly)

    if args.convert:
        # Map between to genetic elements (BED files)
        fetcher.converter(args.from_path, args.to_path, cut=args.post_cut)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Your email address
    parser.add_argument('-email', '--email', type=str, required=True)
    parser.add_argument('-p', '--project', type=str, default="b2010080")

    # Ensembl options
    parser.add_argument('-e', '--ensembl', action='store_true', default=False)
    parser.add_argument('-ea', '--ensembl_assembly', type=str, default="latest")

    # NCBI CCDS options
    parser.add_argument('-c', '--ccds', action='store_true', default=False)
    parser.add_argument('-cr', '--ccds_release', type=str, default="latest")

    # UCSC options
    parser.add_argument('-u', '--ucsc', action='store_true', default=False)
    parser.add_argument('-ua', '--ucsc_assembly', type=str, default="hg19")

    # GATK options
    parser.add_argument('-g', '--gatk', action='store_true', default=False)
    parser.add_argument('-gv', '--gatk_version', type=str, default="latest")
    # Input the actual file names since the request will be from a script that
    # already knows which file it's looking for.
    parser.add_argument('-gf', '--gatk_codes', type=str, nargs="+")
    parser.add_argument('-ga', '--gatk_assembly', type=str, default="hg19")

    # Converter
    parser.add_argument('-convert', '--convert', action='store_true')
    parser.add_argument('-cfrom', '--from_path', type=str)
    parser.add_argument('-cto', '--to_path', type=str)
    parser.add_argument('-ccut', '--post_cut', type=str, default=False)

    # Option to force overwrite existing files
    parser.add_argument('-f', '--force', action='store_true', default=False)

    args = parser.parse_args()
    main(args)

# # Bash
# for chrm in "chr1" "chr2" "chr3" "chr4" "chr5" "chr6" "chr7" "chr8" "chr9" "chr10" "chr11" "chr12" "chr13" "chr14" "chr15" "chr16" "chr17" "chr18" "chr19" "chr20" "chr21" "chr22" "chrX" "chrY"
# do
#   gzip -d "$chrm.fa.gz"
# done

# cat chr*.fa > Homo_sapiens.GRCh37.dna.concat.fa
