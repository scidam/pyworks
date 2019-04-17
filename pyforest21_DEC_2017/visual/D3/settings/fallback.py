'''
File of visualization parameters for 3D plotting

It is part of `pyforest` -- a framework for trees growth modeling.

This is file of fallback parameters. It is used when no species was defined.
'''

# This special constant used by data autodiscovery function
__species__ = 'none'
__checked__ = False
__checkedby__ = 'Noname'


# ------------ Common parameters of 3D models ---------------
# Simple 3d scene plotting, everything is given in meters

GROUND_BOX_HEIGHT = 0.4
GROUND_BOX_COLOR = [1.0, 0.3333333333333333, 0.4980392156862745]

# -----------------------------------------------------------


# --------------- Tree geometry properties ------------------

TREE_RANDOM_SLOPE = 0.2
TREE_STEM_CROWN_CENTER = 0.8  # total length of tree stem as percentage of tree height
TREE_CROWN_START_POSITION = 0.5
TREE_CROWN_MIN_RADIUS = 1
TREE_CROWN_STEM_FACTOR = 1.4
TREE_CROWN_SHAPE = 'sphere'  # 'cone', 'sphere', 'cylinder'
TREE_CROWN_COLOR = [0.1, 0.9, 0.1] 
TREE_STEM_COLOR =  [0.4, 0.4, 0.4]

TREE_STEM_RESOLUTION = 10  # the number of facets to represent tree stem
TREE_CROWN_RESOLUTION = 20  # the number of facets to represent tree crown (as sphere, e.g.)

# -----------------------------------------------------------