# Embarassingly parallel task execution

This is an experiment in generating queues for long-running tasks.

The job consists of touching a corresponding .out file for a large number of .inp files in `data`, simulating calling some simulation code on input files.

The Python file which actually does this work is called `runner.py`:

    import sys
    import os

    infile = sys.argv[1]
    stem = infile[:-4]
    outfile = stem + ".out"

    os.system('touch {}'.format(outfile))


## Baseline: bash for loop

    for i in data/*.inp; do python runner.py $i; done
    
    394.14s user 126.83s system 93% cpu 9:14.31 total
    
## Baseline: GNU parallel

GNU parallel makes this really easy. Simply

    parallel --progress --bar python runner.py ::: data/*.inp
    
This will automatically run a good number of processes in parallel


## Old school: Parallel make

First we create a Makefile:

    targets := $(addsuffix .out,$(basename $(wildcard data/*)))
    
    all: $(targets)
    
    data/%.out: data/%.inp
        python runner.py $@
    
    clean:
        -rm $(targets)
    
    .PHONY: clean

This defines all the targets and how to remove them once they're done. We can run 4 jobs at a time with

    make -j4  # 649.35s user 181.82s system 313% cpu 4:25.31 total

The big benefit, though, is that it knows not to run the job twice, so running that same command again exits immediately.


## First attempt: Celery

Conda environment:

    conda create -n multiprocessing python=3.5

    source activate multiprocessing


Install rabbitmq, the default broker for celery

On mac:

    brew install rabbitmq-server

On Ubuntu:
    
    aptitude install rabbitmq-server

Note, on Ubuntu this installs as a service, so you don't have to run it in the later process

Install celery

    pip install celery

Install flower, a browser-based monitor
    
    pip install flower

On Ubuntu, you will also need to enable the management plugins:

    sudo rabbitmq-plugins enable rabbitmq_management

Now, start rabbitmq - for some reason this doesn't respect C-z, so start in separate terminal (4 terminals in all, activating the environment each time)

    rabbitmq-server

Note that this for some reason doesn't like to be backgrounded, so add it to a different terminal.

Check tasks.py for how to define a task. enq.py will enqueue the tasks

Start a worker with

    celery -A tasks worker

Enqueue the tasks with

    python celery_enq.py *.inp

Now, sit back and watch the system eat through the tasks.

## ISSUES

It seems like not all the tasks finish successfully. This is probably due to contention for the disk.

Based on times between first and last .out file, total 9999 files took 6 minutes to complete.

Doing the same thing with gnu parallel:

    parallel --progress --bar touch {/.}.out ::: *.inp

Takes 2 minutes.

So quite a bit of overhead, although if the tasks are longer running that's obviously going to go down.

To make things fair, I suppose we have to compare with actually starting Python over and over:

    parallel --progress --bar python runner.py {/.}.out ::: *.inp

Takes 12 minutes. Wow. Celery is looking a lot better now!

## Next up: RQ.

    pip install rq

The mechanics of the job queue is easier to understand. You still have to place the function which will be called in a separate file. I think this is for the serialisation to work (each worker process will import the module where the function is defined).

For us this is in `rq_tasks.py`.

This works through redis, so you have to have redis installed 

    brew install redis
    
and start it
    
    redis-server

We also need a similar program to enqueue the tasks, this time it is `rq_enq.py`.

    python rq_enq.py data/*.inp

Will enqueue all the tasks, and

    rq worker

will start consuming them. This seems conceptually similar to celery at this point, but it is clear that celery has a significant edge in the number of options that you can specify for the queue, like for instance allowing concurrent workers and so on, also imposing rate limits. The default behaviour here is for one task to be done at a time. So you could probably run four (say) of them in parallel.

RQ's version of flower is rq-dashboard. It's not as flashy with graphics and stuff, but it is perfectly functional.

    pip install rq-dashboard

It is also useful to run `rq info --interval 1` to get an updated progress bar of the various queues you've set up.

When running 4 workers in parallel, 

    rq woker & rq worker & rq worker & rq worker

we get 9 minutes on the task.

# Jug



# Luigi

Luigi is in anaconda, so just

    conda install luigi
    
Now, start the luigi daemon:

    luigid
    
Luigi appears to run from a different folder than the one where you launch it, so the module you build must be in PYTHONPATH

    PYTHONPATH=. luigi --module luigi_run TouchAllFiles --directory data --workers=4
    
