import sys
import tasks

for infile in sys.argv[1:]:
    tasks.process.delay(infile)
