import sys
from redis import Redis
from rq import Queue

q = Queue(connection=Redis())

from rq_tasks import process

for infile in sys.argv[1:]:
    q.enqueue(process, infile)
