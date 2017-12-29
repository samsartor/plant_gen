import bpy
import mathutils
import sys
import os
from mathutils import Vector, Matrix
from imp import reload
from random import uniform, randint, choice
from math import pi, sin, cos, radians, degrees, sqrt

sys.path.append('./tree-gen/')
import ch_trees.parametric.gen as tree_gen
TREE_SET = [
    "balsam_fir",
    "black_tupelo",
    "dim_red_test",
    "fan_palm",
    "palm",
    "silver_birch",
    # "spiral",
    # "weeping_willow_o",
    "acer",
    "bamboo",
    # "branch_struct",
    "douglas_fir",
    "hill_cherry",
    "quaking_aspen",
    "small_pine",
    "apple",
    "black_oak",
    # "cambridge_oak",
    "european_larch",
    "lombardy_poplar",
    "sassafras",
    # "sphere_tree",
    "weeping_willow"
]

def reset_blend():
    # bpy.ops.wm.read_factory_settings()

    for scene in bpy.data.scenes:
        for obj in scene.objects:
            scene.objects.unlink(obj)

    # only worry about data in the startup scene
    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.lamps,
            bpy.data.cameras,
            ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data)

def create_tree(ty, seed):
    mod = __import__('ch_trees.parametric.tree_params.' + ty, fromlist=[''])
    reload(mod)
    tree_gen.construct(mod.params, seed=seed)
    tree = bpy.context.scene.objects.active
    return tree

def look(location, yaw, pitch, roll):
    return Matrix.Translation(location)\
    * (Matrix.Rotation(yaw - 3 * pi / 2, 3, 'Z')\
    * Matrix.Rotation(pi / 2 - pitch, 3, 'X')\
    * Matrix.Rotation(roll, 3, 'Z')).to_4x4()

def create_sun(yaw, pitch, color=(1,1,1), name="sun"):
    sun = bpy.data.lamps.new(name, type="SUN")
    sun_ob = bpy.data.objects.new(name, sun)
    sun_ob.matrix_world = look((0, 0, 0), yaw, pitch, 0).to_4x4()
    sun.color = color
    bpy.context.scene.objects.link(sun_ob)
    return sun_ob

def create_camera(location, yaw, pitch, roll, name="cam"):
    cam = bpy.data.cameras.new(name)
    cam_ob = bpy.data.objects.new(name, cam)
    cam_ob.matrix_world = look(location, yaw, pitch, roll).to_4x4()
    bpy.context.scene.objects.link(cam_ob)
    return cam_ob

def create_floor(radius, name="floor"):
    bpy.ops.mesh.primitive_circle_add(
        vertices=32,
        radius=radius,
        fill_type='TRIFAN',
        location=(0, 0, 0))
    return bpy.context.object

def reset(*argv):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in argv:
        obj.select = True
        bpy.ops.object.delete() 

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

def render(camera, resolution_x, resolution_y, filepath=None):
    scene = bpy.context.scene
    scene.camera = camera
    sets = scene.render
    sets.resolution_x = resolution_x
    sets.resolution_y = resolution_y
    sets.resolution_percentage = 100
    sets.filepath = filepath or sets.filepath
    bpy.ops.render.render(write_still = bool(filepath))
    
# setup env
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

#ensure_dir("output/blend")
#ensure_dir("output/img")
ensure_dir("output/many")
scene = bpy.context.scene

#for tree_ty in TREE_SET[14:]:
for index in range(0, 200):
    tree_ty = choice(TREE_SET)

    reset_blend()
    scene.render.engine = "CYCLES"
    scene.world.horizon_color = (0.2, 0.2, 0.2)

    tree = create_tree(tree_ty, randint(0, 999999999))
    sun = create_sun(
        uniform(0, pi * 2),
        uniform(pi / 4, 2 * pi / 6),
        color=(2, 2, 2))

    (rad, center) = bound_data(all_corners(tree))

    yaw = uniform(0, pi * 2)
    pitch = uniform(pi / 6, pi / 3)
    cam = create_camera((
        rad * cos(pitch) * cos(yaw) + center[0], 
        rad * cos(pitch) * sin(yaw) + center[1],
        rad * sin(pitch) + center[2]),
        yaw, pitch, 0)

    floor = create_floor(rad * 100)

    #render(cam, 512, 512, filepath="output/img/{}".format(tree_ty))
    #bpy.ops.wm.save_as_mainfile(filepath="output/blend/{}.blend".format(tree_ty))
    render(cam, 1024, 1024, filepath="output/many/{}".format(index))

    reset(tree, sun, cam, floor)