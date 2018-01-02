#!/usr/bin/env python3

import csv
import config as cfg
from PIL import Image
from os import path

in_size = (1024, 1024)
out_size = (101, 101)

with open(cfg.DB_FILENAME) as csv_file:
    csv_in = csv.DictReader(csv_file)
    for row in csv_in:
        name = row.get('name')
        filepath = cfg.IMG_FILENAME.format(
            name=name,
            resx=in_size[0],
            resy=in_size[1])
        filename, ext = path.splitext(filepath)
        im = Image.open(filepath)
        im = im.resize(out_size, resample=Image.BOX)
        im.save(cfg.IMG_FILENAME.format(
            name=name,
            resx=out_size[0],
            resy=out_size[1]))
        print("Resized image", filename)
