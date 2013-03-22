#!/usr/bin/env python

from __future__ import print_function
import argparse
from genie.fetcher import Fetcher


def main(args):

    fetcher = Fetcher("unknown")

    fetcher.reorganize(args.main_path, args.order, misc_path=args.misc_path, out_path=args.out_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Reorganize columns in one or two files
    parser.add_argument('-main', '--main_path', type=str, required=True)
    parser.add_argument('-misc', '--misc_path', type=str, default=None)
    parser.add_argument('-o', '--order', type=int, nargs="+")
    parser.add_argument('-out', '--out_path', type=str, default=None)

    args = parser.parse_args()
    main(args)
