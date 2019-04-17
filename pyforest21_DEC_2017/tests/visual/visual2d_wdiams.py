'''
Plots a few trees with different diameters

'''

from pyforest.objects.trees import Tree
from pyforest.core import Model
from pyforest.visual.D2 import Scene2D


m = Model(bbox=[(0, 10), (0, 40)])


t1 = Tree (1, 1, dbh=35, stage='adult')
t2 = Tree (12, 2, dbh=15, stage='sapling')
t3 = Tree (3, 13, ddh=1, dbh=0, stage='seedling')

m.objects += [
              t1, t2, t3
              ]


d2 = Scene2D()
d2.plot_model(m)
d2.show()
