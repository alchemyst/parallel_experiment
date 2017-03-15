#!/usr/bin/env python

from jug import TaskGenerator
import os
import glob

@TaskGenerator
def process(f):
    os.system('python runner.py {}'.format(f))

for f in glob.glob('data/*.inp'):
    process(f)
