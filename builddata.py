#!/usr/bin/env python

import pathlib

base = pathlib.Path('data')
if not base.exists():
    base.mkdir()

for i in range(9999):
    infile = base / pathlib.Path("{:04}.inp".format(i))
    infile.touch()
