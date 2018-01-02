from math import radians, degrees
from random import choice, uniform
import time

# number of trees to generate and render
TOTAL_COUNT = 1
# number of workers (blender instances)
WORKER_COUNT = 1

# where to save rendered images
IMG_FILENAME = 'output/img_{name:}_{resx:}.png'
# image sizes
IMG_SIZES = [(1024, 1024), (32, 32)]
# image vertical FOV
IMG_FOV = 60

# where to save dataset metadata (image labels, etc.)
DB_FILENAME = 'output/pprd.csv'
# append or replace existing metadata
DB_APPEND = True
# csv fieldnamess
DB_FIELDNAMES = ['name', 'species', 'shadow_azimuth', 'sun_altitude', 'cam_altitude']

# where to save temporary worker metadata
WORKER_OUT = '/tmp/_pprd_sub{}.csv'
# command to launch blender
BLENDER_EXE = 'blender'
# seed prefix
BASE_SEED = b'\4'
# .blend file to build off of
BASE_BLEND = 'base.blend'

# choose a species name
def species():
    TREE_SET = [
        'balsam_fir',
        'black_tupelo',
        'dim_red_test',
        'fan_palm',
        'palm',
        'silver_birch',
        # 'spiral',
        # 'weeping_willow_o',
        'acer',
        'bamboo',
        # 'branch_struct',
        'douglas_fir',
        'hill_cherry',
        'quaking_aspen',
        'small_pine',
        'apple',
        'black_oak',
        # 'cambridge_oak',
        'european_larch',
        'lombardy_poplar',
        'sassafras',
        # 'sphere_tree',
        'weeping_willow'
    ]
    return choice(TREE_SET)

# choose the sun direction = (azimuth, altitude)
def sun_direction():
    return (
        uniform(0, radians(360)),
        uniform(radians(15), radians(90)),
    )

# choose the sky color = (R, G, B)
def sky_color():
    return (0.3, 0.3, 0.3)

# choose the sun color = (R, G, B)
def sun_color():
    return (3, 3, 3)

# choose the camera direction = (azimuth, altitude)
def cam_direction():
    return (
        uniform(0, radians(360)),
        uniform(radians(15), radians(60)),
    )