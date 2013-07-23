#!/usr/bin/env python

from __future__ import print_function
import argparse

import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
from genie.servers import NCBI, Ensembl, GATK, UCSC


def main(args):

    # Switch statement
    ftp = {
        "ensembl": Ensembl,
        "ncbi": NCBI,
        "gatk": GATK,
        "ucsc": UCSC
    }.get(args.server.lower())()

    # Which file to download and whether to force overwrites
    ftp.save(args.query).force(args.force)

    if args.destination is not None:
        ftp.to(args.destination)

    if args.file_name is not None:
        ftp.named(args.file_name)

    # Commit to download the file
    ftp.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-e", "--email", type=str,
                        help="Your email address (sometimes used as"
                             "username/password)")

    # Ensembl options
    parser.add_argument("-s", "--server", type=str, required=True)
    parser.add_argument("-q", "--query", type=str, required=True)

    # Options
    parser.add_argument("-d", "--destination", type=str, default=None)
    parser.add_argument("-n", "--file_name", type=str, default=None)

    # GATK specifics
    parser.add_argument("-v", "--gatk_version", type=float, default=None,
                        help="GATK version number. Currently either: 2.3, 2.4.")
    
    # GATK / UCSC
    parser.add_argument("-a", "--assembly", type=str, default=None,
                        help="Short hand for assembly: b37, hg19 etc.")

    # Option to force overwrite existing files
    parser.add_argument("-f", "--force", action='store_true', default=False)

    args = parser.parse_args()
    main(args)

# # Bash
# for chrm in "chr1" "chr2" "chr3" "chr4" "chr5" "chr6" "chr7" "chr8" "chr9" "chr10" "chr11" "chr12" "chr13" "chr14" "chr15" "chr16" "chr17" "chr18" "chr19" "chr20" "chr21" "chr22" "chrX" "chrY"
# do
#   gzip -d "$chrm.fa.gz"
# done

# cat chr*.fa > Homo_sapiens.GRCh37.dna.concat.fa
