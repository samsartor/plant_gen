#!/usr/bin/env python3

from subprocess import Popen, DEVNULL
from hashlib import sha256
import time
import csv
import os
import config as cfg

per_worker = cfg.TOTAL_COUNT // cfg.WORKER_COUNT

def create_worker(index):
    global per_worker, BLENDER_EXE, BASE_SEED, WORKER_OUT, IMG_FILENAME

    start = per_worker * index

    args = [cfg.BLENDER_EXE, cfg.BASE_BLEND, '-b', '-P', 'worker.py']

    print('RUN WORKER {}'.format(index))
    return Popen(args, env={
        'START_INDEX': str(start),
        'END_INDEX': str(start + per_worker),
        'WORKER_OUT': cfg.WORKER_OUT.format(index),
    }, stdout=DEVNULL, stdin=DEVNULL)

print('CREATING {} WORKERS'.format(cfg.WORKER_COUNT))
workers = [(ind, create_worker(ind)) for ind in range(cfg.WORKER_COUNT)]

is_appending = cfg.DB_APPEND and os.path.isfile(cfg.DB_FILENAME)
with open(cfg.DB_FILENAME, 'a' if cfg.DB_APPEND else 'w') as csv_file:
    csv_out = csv.DictWriter(csv_file, fieldnames=cfg.DB_FIELDNAMES)
    if not is_appending:
        csv_out.writeheader()

    for index, worker in workers:
        worker.wait()
        print('WORKER {} RETURNED'.format(index))

        sub_filename = cfg.WORKER_OUT.format(index)
        with open(sub_filename) as sub_file:
            csv_out.writerows(csv.DictReader(sub_file))
        os.remove(sub_filename)
        print('WORKER {} DONE'.format(index))

print('ALL WORKERS DONE')