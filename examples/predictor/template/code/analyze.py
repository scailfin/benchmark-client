"""Analytics code for the predictor examples. Reads a text file (as produced by
the predictor code) and outputs the average distance of the predicted values
from the expected values and the number of exact predictions.
"""

from __future__ import absolute_import, division, print_function

import argparse
import errno
import os
import json
import sys


GROUND_TRUTH = [5, 2, 6, 7, 6]


def main(inputfile, outputfile):
    """Expects an input file with five rows, each containig an integer value.
    Outputs JSON object that contains the average distance of the predicted
    value from the expected value and the total number of exact predictions.
    """
    # Count number of lines, characters, and keep track of the longest line
    exact_match_count = 0
    total_diff = 0
    with open(inputfile, 'r') as f:
        index = 0
        for line in f:
            if index > len(GROUND_TRUTH):
                break
            diff = abs(int(line.strip()) - GROUND_TRUTH[index])
            if diff == 0:
                exact_match_count += 1
            else:
                total_diff += diff
            index += 1
    # Create results object
    results = {
        'avg_diff': total_diff / len(GROUND_TRUTH),
        'exact_match': exact_match_count
    }
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
        json.dump(results, f)


if __name__ == '__main__':
    args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputfile", required=True)
    parser.add_argument("-o", "--outputfile", required=True)

    parsed_args = parser.parse_args(args)

    main(inputfile=parsed_args.inputfile, outputfile=parsed_args.outputfile)
