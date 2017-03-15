#!/usr/bin/env python

import luigi
import os


class TouchFile(luigi.Task):
    infile = luigi.Parameter()

    def run(self):
        o = self.output().path
        os.system('touch {}'.format(o))

    def output(self):
        return luigi.file.LocalTarget(self.infile[:-4] + '.out')


class TouchAllFiles(luigi.WrapperTask):
    directory = luigi.Parameter()

    def requires(self):
        for f in os.listdir(self.directory):
            if f.endswith('.inp'):
                yield TouchFile(os.path.join(self.directory, f))

