import csv
import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim
from os import path

DB_ROW_DEFAULTS = {
    'name': ['AAAAAAAAAA'], 
    'species': [''],
    'shadow_azimuth': [0.0],
    'sun_altitude': [0.0],
    'cam_altitude': [0.0],
}

class DatasetError(Exception):
    """Exception raised for errors in the dataset structure."""

    def __init__(self, message):
        self.message = message

def dataset(outdir='output', image_size=1024, img_channels=3, cols=DB_ROW_DEFAULTS):
    if not outdir.endswith('/'):
        outdir += '/'
    filepath = path.join(outdir, 'pprd.csv')

    # check database structure
    with open(filepath, 'r') as csv_read:
        fields = csv.DictReader(csv_read).fieldnames
        for f, c in zip(fields, cols.keys()):
            if f != c:
                raise DatasetError('Columns "{}" and "{}" do not match'.format(f, c))

    def expand_row(row):
        # read image for parsed row

        name = row.get('name')
        filename =  tf.string_join([
            outdir,
            'img_',
            name,
            '_{}.png'.format(image_size),
        ])

        image_string = tf.read_file(filename)
        image_decoded = tf.image.decode_image(image_string, channels=img_channels)
        image_decoded.set_shape([image_size, image_size, img_channels])

        return {'img': image_decoded, **row}

    def apply_line(line):
        # parse a row

        items = tf.decode_csv(line, record_defaults=list(cols.values()))
        pairs = zip(cols.keys(), items)
        return expand_row(dict(pairs))

    ds = tf.data.TextLineDataset(filepath)
    ds = ds.skip(1)
    ds = ds.map(apply_line)
    return ds

# ds = dataset()
# ds = ds.map(lambda row: (row.get('img'), row.get('species')))
# ds = ds.shuffle(buffer_size=1000)
# ds = ds.repeat()
# ds = ds.batch(4)

# ds_iterator = ds.make_one_shot_iterator()
# next_batch = ds_iterator.get_next()

# with tf.Session() as sess:
#     img, species = sess.run(next_batch)