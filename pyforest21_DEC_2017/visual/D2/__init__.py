'''
Tools for 2D visualization of model states
'''

try:
    import matplotlib.pyplot as plt
except ImportError:
    pass

import os

from pyforest.objects.data import ObjectDataStorage

import numpy as np


class AbstractScene2D(object):
    pass

# class AbstractAxes2D(plt.Axes):
#     pass
# 
# class Axes2D(AbstractAxes2D):
#     pass


class Scene2D(AbstractScene2D):

    def __init__(self, *args, **kwargs):
        super(Scene2D, self).__init__(*args, **kwargs)
        self.figure = plt.figure()
        self.axes = self.figure.add_subplot(111)
        self.axes.set_aspect('equal')
        self._rotmat = None
        self._trans = None
        cpath = os.path.dirname(os.path.abspath(__file__))
        self._params = ObjectDataStorage()
        self._params.autodiscover(path=os.path.join(cpath, '../settings'))
        self._viewport = ((0, 1), (0, 1))

    def _get_projection(self, model):
        x_orient = model.data.get('orientation', dict()).get('xaxis', 0)
        phi = 3.0*np.pi/2.0 - x_orient
        l_x = model.bbox[0][1] - model.bbox[0][0]
        l_y = model.bbox[1][1] - model.bbox[1][0]
        bbox_proj = [[0.0, 0.0],
                     [l_x * np.cos(phi), l_x*np.sin(phi)],
                     [l_y * np.cos(x_orient), -l_y * np.sin(x_orient)],
                     ]
        bbox_proj = np.array(bbox_proj)
        bbox_proj = np.vstack((bbox_proj, bbox_proj[1] + bbox_proj[2]))
        xmin, ymin = np.min(bbox_proj, axis=0)
        xmax, ymax = np.max(bbox_proj, axis=0)
        self._viewport = ((xmin, xmax), (ymin, ymax))
        xc = 0.5 * (xmin + xmax)
        yc = 0.5 * (ymin + ymax)
        rotmat = np.array([[np.cos(phi), -np.sin(phi)],
                           [np.sin(phi), np.cos(phi)]])
        self._rotmat = rotmat
        self._trans = np.array([xc, yc])

    def _project(self, model, x, y):
        if self._rotmat is None or self._trans is None:
            self._get_projection(model)
        r = np.array([[x], [y]])
        rr = np.dot(self._rotmat, r)
        return rr[0, 0] + self._trans[0], rr[1, 0] + self._trans[1]

    def _project_vectors(self, model, x, y):
        if self._rotmat is None or self._trans is None:
            self._get_projection(model)
        res = np.vstack((x, y))
        res = np.dot(self._rotmat, res).T
        return res[:, 0] + self._trans[0], res[:, 1] + self._trans[1]

    def add_plants(self, model, species='all'):
        '''Appends trees or shrubs of specified species to the visual plot

        :param model: a model instance where objects will be searched;
        :param species: a list of species names to be plotted; default is 'all',
                        i.e. all species (trees and shrubs) are plotted.
        :type model: pyforest.core.Model
        '''

        if species == 'all':
            selection = model.objects
        elif isinstance(species, list):
            selection = model.objects.select_by_species(species)
        elif isinstance(species, str):
            selection = model.objects.select_by_species([species])
        else:
            selection = []
        for obj in selection:
            cf, ce, m, s = self.get_obj_cms(obj, model)
            x, y = self._project(model, obj.x, obj.y)
            self.axes.plot(x, y, marker=m, markersize=s, mec=ce, mfc=cf)

    def add_seeds(self, model, species='all'):
        '''Add seeds of specified plant species to the visual plot
        '''

        if species == 'all':
            selection = model.seeds.keys()
        elif isinstance(species, list):
            selection = species
        elif isinstance(species, str):
            selection = [species]
        else:
            selection = []
        for key in selection:
            for age in np.unique(model.seeds[key][-1]):
                c, m, s = self.get_seed_cms(species, age)
                _x, _y = model.seeds[key][0], model.seeds[key][1]
                _x = _x[model.seeds[key][-1] == age]
                _y = _y[model.seeds[key][-1] == age]
                x, y = self._project_vectors(model, _x, _y)
                self.axes.scatter(x, y, s=s, c=c, marker=m)

    def plot_model(self, model):
        '''Add all objects in the model to visual plot'''

        self.add_plants(model)
        self.add_seeds(model)

    def get_obj_cms(self, obj, model):
        '''Just a fake function for now'''
        if obj.species:
            species = obj.species
        else:
            species = 'none'
        minm, maxm = self._params.get_minmax_data(species,
                                                  'MIN_MARKER_SIZE')
        _data = np.array([i.dbh for i in model.objects])
        mind = min(_data[_data > 0])
        maxd = max(_data)
        part = (obj.dbh - mind) / float(maxd - mind)
        size = minm + part * (maxm - minm)
        if size < minm:
            size = minm
        elif size > maxm:
            size = maxm
        if obj.type == 'shrub':
            marker = self._params.get_parameter(species, 'SHRUB_MARKER')
        else:
            marker = self._params.get_parameter(species, 'TREE_MARKER')
        fcolor = self._params.get_parameter(species, 'FILL_COLOR')
        ecolor = self._params.get_parameter(species, 'EDGE_COLOR')
        return (fcolor, ecolor, marker, size)

    @staticmethod
    def get_seed_cms(species, age):
        '''Just a fake function for now'''
        import random
        m = random.choice(['o',
                           'x',
                           's',
                           'd',
                           '^'])
        s = random.randint(1, 20)
        c = random.choice(['r', 'g', 'b', 'c', 'm'])
        return c, m, s

    def show(self):
        _, maxm = self._params.get_minmax_data('none',
                                               'MIN_MARKER_SIZE')
        rval = np.sqrt(maxm / np.pi)
        vx_min = self._viewport[0][0] - rval
        vx_max= self._viewport[0][1] + rval
        vy_min = self._viewport[1][0] - rval
        vy_max= self._viewport[1][1] + rval
        self.axes.set_xlim([vx_min, vx_max])
        self.axes.set_ylim([vy_min, vy_max])
        plt.show()
