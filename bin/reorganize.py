#!/usr/bin/env python

from __future__ import print_function
import argparse
from genie.fetcher import Fetcher


def main(args):

    fetcher = Fetcher("unknown")

    if args.join:
        fetcher.join(args.main_path, args.misc_path, args.order, args.out_path,
                     idColumns=args.id_columns, sep=args.separator,
                     default=args.default)
    else:
        fetcher.reorganize(args.main_path, args.order,
                           misc_path=args.misc_path, out_path=args.out_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Reorganize columns in one or two files
    parser.add_argument('-main', '--main_path', type=str, required=True)
    parser.add_argument('-misc', '--misc_path', type=str, default=None)
    parser.add_argument('-o', '--order', type=int, nargs="+", required=True)
    parser.add_argument('-out', '--out_path', type=str, required=True)
    parser.add_argument('-id', '--id_columns', type=str, nargs="+",
                        default=[0, 1, 2])
    parser.add_argument('-sep', '--separator', type=str, default="\t")
    parser.add_argument('-def', '--default', default="")

    parser.add_argument("-j", --"join", action="store_true", default=False)

    args = parser.parse_args()
    main(args)
