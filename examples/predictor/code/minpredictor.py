"""Analytics code for the adopted hello workd Demo. Reads a text file (as
produced by the helloworld.py code) and outputs the average number of characters
per line and the number of characters in the line with the most characters.
"""

from __future__ import absolute_import, division, print_function

import argparse
import errno
import os
import json
import sys


def main(inputfile, outputfile):
    """Write greeting for every name in a given input file to the output file.
    The optional waiting period delays the output between each input name.

    """
    result = list()
    with open(inputfile, 'r') as f:
        for line in f:
            values = [int(v) for v in line.strip().split(',')]
            result.append(min(values) + 1)
    # Write analytics results. Ensure that output directory exists:
    # influenced by http://stackoverflow.com/a/12517490
    dir_name = os.path.dirname(outputfile)
    if dir_name != '':
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name)
            except OSError as exc:  # guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
    with open(outputfile, "w") as f:
        for val in result:
            f.write(str(val) + '\n')


if __name__ == '__main__':
    args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputfile", required=True)
    parser.add_argument("-o", "--outputfile", required=True)

    parsed_args = parser.parse_args(args)

    main(inputfile=parsed_args.inputfile, outputfile=parsed_args.outputfile)
