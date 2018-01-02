import bpy
from mathutils import Vector, Matrix
from math import pi, sin, cos, tan, sqrt, radians, degrees, fmod

from os import getenv
from zlib import adler32
import csv
import random
import sys
from imp import reload
import hashlib
from base64 import b32encode

sys.path.append('./')
sys.path.append('./tree-gen/')
import config as cfg
import ch_trees.parametric.gen as tree_gen

def reset_blend():
    for scene in bpy.data.scenes:
        for obj in scene.objects:
            scene.objects.unlink(obj)

    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.lamps,
            bpy.data.cameras,
            ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data)

def bound_data(vertices):
    def ch(vertices, i):
        vs = [c[i] for c in vertices]
        v_min = min(vs)
        v_max = max(vs)
        return (v_max - v_min, (v_min + v_max) / 2)

    data = [ch(vertices, i) for i in [0, 1, 2]]
    return (sqrt(sum(d[0] * d[0] for d in data)), tuple(d[1] for d in data))

def all_corners(obj):
    corners = [v for v in obj.bound_box]
    for c in obj.children:
        corners += all_corners(c)
    return corners

def look(location, azimuth, altitude, roll):
    return Matrix.Translation(location)\
    * (Matrix.Rotation(azimuth - 3 * pi / 2, 3, 'Z')\
    * Matrix.Rotation(pi / 2 - altitude, 3, 'X')\
    * Matrix.Rotation(roll, 3, 'Z')).to_4x4()

def create_camera(location, azimuth, altitude, roll, name="cam"):
    cam = bpy.data.cameras.new(name)
    cam.angle_y = radians(cfg.IMG_FOV)
    cam_ob = bpy.data.objects.new(name, cam)
    cam_ob.matrix_world = look(location, azimuth, altitude, roll).to_4x4()
    bpy.context.scene.objects.link(cam_ob)
    return cam_ob

def create_sun(azimuth, altitude, color=(1,1,1), name="sun"):
    sun = bpy.data.lamps.new(name, type="SUN")
    sun_ob = bpy.data.objects.new(name, sun)
    sun_ob.matrix_world = look((0, 0, 0), azimuth, altitude, 0).to_4x4()
    sun.color = color
    bpy.context.scene.objects.link(sun_ob)
    return sun_ob

def create_floor(radius, name="floor"):
    bpy.ops.mesh.primitive_circle_add(
        vertices=32,
        radius=radius,
        fill_type='TRIFAN',
        location=(0, 0, 0))
    return bpy.context.object

def create_tree(species, seed):
    mod = __import__('ch_trees.parametric.tree_params.' + species, fromlist=[''])
    reload(mod)
    tree_gen.construct(mod.params, seed=seed)
    tree = bpy.context.scene.objects.active
    return tree

def render(camera, resolution_x, resolution_y, filepath=None):
    scene = bpy.context.scene
    scene.camera = camera
    sets = scene.render
    sets.resolution_x = resolution_x
    sets.resolution_y = resolution_y
    sets.resolution_percentage = 100
    sets.filepath = filepath or sets.filepath
    bpy.ops.render.render(write_still = bool(filepath))

def gen_scene(name, tree_seed):
    reset_blend()

    species = cfg.species()
    sun_azimuth, sun_altitude = cfg.sun_direction()
    cam_azimuth, cam_altitude = cfg.cam_direction()

    scene = bpy.context.scene
    scene.world.horizon_color = cfg.sky_color()

    sun = create_sun(sun_azimuth, sun_altitude, color=cfg.sun_color())
    tree = create_tree(species, tree_seed)
    floor = create_floor(50)

    diag, cam_center = bound_data(all_corners(tree))
    cam_center = (0, 0, cam_center[2])
    cam_dist = diag / tan(radians(cfg.IMG_FOV))

    camera = create_camera((
        cam_dist * cos(cam_altitude) * cos(cam_azimuth) + cam_center[0], 
        cam_dist * cos(cam_altitude) * sin(cam_azimuth) + cam_center[1],
        cam_dist * sin(cam_altitude) + cam_center[2]), cam_azimuth, cam_altitude, 0)

    for resx, resy in cfg.IMG_SIZES:
        filepath = cfg.IMG_FILENAME.format(name=name, resx=resx, resy=resy)
        render(camera, resx, resy, filepath=filepath)

    return {
        'name': name,
        # 'scene': '{:08x}'.format(scene_seed),
        # 'tree': '{:08x}'.format(tree_seed),
        'species': species,
        'shadow_azimuth': degrees(sun_azimuth + radians(180) - cam_azimuth) % 360,
        'sun_altitude': degrees(sun_altitude),
        'cam_altitude': degrees(cam_altitude),
    }

def seed_hash(data):
    return hashlib.md5(data).digest()

def name_hash(data):
    return b32encode(seed_hash(data)).decode('utf-8')[:10]

SAVE_FILE  = getenv('WORKER_OUT')
INDS = range(int(getenv('START_INDEX')), int(getenv('END_INDEX')))
with open(SAVE_FILE, 'w') as csv_file:
    csv_out = csv.DictWriter(csv_file, fieldnames=cfg.DB_FIELDNAMES)
    csv_out.writeheader()

    for index in INDS:
        try:
            ind_bytes = index.to_bytes(8, byteorder='big')
            name = name_hash(cfg.BASE_SEED + ind_bytes)
            scene_seed = seed_hash(cfg.BASE_SEED + ind_bytes + b'scene')
            tree_seed = seed_hash(cfg.BASE_SEED + ind_bytes + b'tree')

            random.seed(scene_seed)
            csv_out.writerow(gen_scene(name, tree_seed))
        except Exception:
            pass
