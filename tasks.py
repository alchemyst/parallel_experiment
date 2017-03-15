#!/usr/bin/env python

from celery import Celery
import logging

app = Celery('tasks', broker='amqp://guest@localhost')

@app.task
def process(filename):
    import os
    logging.info('Queing task {}'.format(filename))
    os.system('python runner.py {}'.format(filename))
