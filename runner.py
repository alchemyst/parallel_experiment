#!/usr/bin/env python

import sys
import os

infile = sys.argv[1]
stem = infile[:-4]
outfile = stem + ".out"

os.system('touch {}'.format(outfile))
