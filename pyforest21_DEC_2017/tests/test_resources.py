
import datetime
from unittest import TestCase



from pyforest.resources.light.solar import (get_altitude,
                                            get_azimuth)
from pyforest.resources.light.utils import (point_in_triangle,
                                            poly3d_intersection)

from pyforest.events.random import CreateRandomSimpleTrees
from pyforest.objects.trees import Tree

from pyforest.core import Model
from pyforest.resources.light import (SimpleSolarIrradianceMixin,
                                      SolarDirectIrradiance,
                                      get_intersection_length,
                                      SolarDirectMonsiSaekiIrradiance,
                                      SolarDirectMonsiSaekiAdoptedIrradiance)

from scipy.spatial import ConvexHull as CH
import numpy as np


class TestSolarSubmodule(TestCase):

    def setUp(self):
        self.cube = [[0, 0, 0], [0, 0, 1], [0, 1, 0],
                     [1, 0, 0], [0, 1, 1], [1, 0, 1],
                     [1, 1, 0], [1, 1, 1]]

    def test_get_altitute(self):
        '''
        Based on data from `pysolar` project
        '''
        value = get_altitude(42.364908, -71.112828,
                             datetime.datetime(2007, 2, 18, 20, 13, 1, 130320))
        self.assertLess(abs(value - 19), 1)

    def test_get_azimuth(self):
        value = get_azimuth(42.364908,
                            -71.112828,
                            datetime.datetime(2007, 2, 18, 20, 18, 0, 0))
        self.assertLess(abs(value + 52), 1)

    def test_point_within_triangle(self):
        triangle = [[0, 0], [1, 0], [0.5, 8]]
        res = point_in_triangle(triangle[1], triangle[2], [0.5, 2])
        self.assertTrue(res)

    def test_point_outside_triangle(self):
        triangle = [[0, 0], [1, 0], [0.5, 8]]
        res = point_in_triangle(triangle[1], triangle[2], [1.5, 2])
        self.assertFalse(res)

    def test_point_on_vertex_triangle(self):
        triangle = [[0, 0], [1, 0], [0.5, 8]]
        res = point_in_triangle(triangle[1], triangle[2], [0.5, 8])
        self.assertTrue(res)

    def test_point_on_edge_triangle(self):
        triangle = [[0, 0], [1, 0], [0.5, 8]]
        res = point_in_triangle(triangle[1], triangle[2], [0.5, 0])
        self.assertTrue(res)

    def test_compute_3d_intersection(self):
        point = [-1, -1, -1]
        direction = [1, 1, 1]
        res = poly3d_intersection(self.cube, point, direction)
        np.testing.assert_almost_equal(res[0], np.array([0.0, 0.0, 0.0]))
        np.testing.assert_almost_equal(res[1], np.array([1.0, 1.0, 1.0]))

    def test_compute_3dedge_intersection(self):
        point = [0.5, 0, -0.5]
        direction = [0, 0, 1]
        res = poly3d_intersection(self.cube, point, direction)
        np.testing.assert_almost_equal(res[0], np.array([0.5, 0.0, 0.0]))
        np.testing.assert_almost_equal(res[1], np.array([0.5, 0.0, 1.0]))

    def test_slightly_complex_intersection(self):
        point = [0, 0, -0.5]
        direction = [1, 1, 1]
        res = poly3d_intersection(self.cube, point, direction)
        np.testing.assert_almost_equal(res[0],
                                       np.array([0.5, 0.5, 0.0]))
        np.testing.assert_almost_equal(res[1],
                                       np.array([1.0, 1.0, 0.5]))

    def test_slightly_complex_nointersection(self):
        point = [0, 0, -0.5]
        direction = [-1, -1, -1]
        res = poly3d_intersection(self.cube, point, direction)
        self.assertEqual(len(res), 0)

    def test_compute_3dedge_nointersection(self):
        point = [0.5, 0, -0.5]
        direction = [0, 0, -1]
        res = poly3d_intersection(self.cube, point, direction)
        self.assertEqual(len(res), 0)


class TestSimpleSolarIrradiance(TestCase):

    def setUp(self):
        self.model = Model()
        self.model.data = {'orientation': {'xaxis': 3.0 * np.pi / 2.0}}
        self.model.insert_resource(SimpleSolarIrradianceMixin())
        self.res = self.model.resources[0]

    def test_get_direction_default(self):
        direction = self.res._get_direction()
        np.testing.assert_almost_equal(self.res.sundirection, direction)

    def test_get_direction_sun_from_north(self):
        res = SimpleSolarIrradianceMixin(sundirection=np.array([0,
                                                           -1.0 / np.sqrt(2),
                                                           -1 / np.sqrt(2)]))
        self.model.insert_resource(res)
        direction = self.model.resources[-1]._get_direction()
        np.testing.assert_almost_equal(direction, np.array(res.sundirection))

    def test_get_direction_sun_from_east(self):
        res = SimpleSolarIrradianceMixin(sundirection=np.array([-1.0, 0.0, 0.0]))
        self.model.insert_resource(res)
        direction = self.model.resources[-1]._get_direction()
        np.testing.assert_almost_equal(direction, np.array(res.sundirection))

    def test_get_direction_modified_orientation(self):
        self.model.data = {'orientation': {'xaxis': np.pi}}
        direction = self.res._get_direction()
        np.testing.assert_almost_equal(direction, np.array([-1.0 / np.sqrt(2.0),
                                                            0,
                                                            -1.0 / np.sqrt(2.0)]))


class TestAuxilaryLightFunction(TestCase):

    def setUp(self):
        self.cube = [[0, 0, 0], [0, 0, 1], [0, 1, 0],
                     [1, 0, 0], [0, 1, 1], [1, 0, 1],
                     [1, 1, 0], [1, 1, 1]
                     ]
        self.qhull = CH(self.cube, incremental=True)

    def test_get_intersection_length(self):
        direction = [0, 0, 1]
        point = [0.5, 0.5, -2]
        res = get_intersection_length(point, direction, self.qhull)
        self.assertAlmostEqual(res, 1.0)

    def test_get_intersection_length_point_inside(self):
        direction = [0, 0, 1]
        point = [0.5, 0.5, 0.5]
        res = get_intersection_length(point, direction, self.qhull)
        self.assertAlmostEqual(res, 0.5)


# class TestSolarDirectIrradiance(TestCase):
#     def setUp(self):
#         self.model = Model(bbox=[(0, 30), (0, 30)])
#         self.model.data = {'orientation': {'xaxis': 3.0 * np.pi / 2.0}}
#         self.model.insert_resource(SolarDirectIrradiance(stepx=4,
#                                                          stepy=4,
#                                                          stepz=4))
#         monsisaeki = SolarDirectMonsiSaekiIrradiance(stepx=4,
#                                                      stepy=4,
#                                                      stepz=4)
#         monsisaekiadopted = SolarDirectMonsiSaekiAdoptedIrradiance(stepx=4,
#                                                                    stepy=4,
#                                                                    stepz=4)
#         self.model.insert_resource(monsisaeki)
#         self.model.insert_resource(monsisaekiadopted)
# 
#         # 5 x 5 cube crown
#         crown = 5 * np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0],
#                               [1, 0, 0], [0, 1, 1], [1, 0, 1],
#                               [1, 1, 0], [1, 1, 1]]
#                              )
#         tree = Tree(10, 10, stage='adult', species='Quercus Mongolica',
#                     height=10, dbh=20)
#         tree.add_crown(crown)
#         self.model.objects.append(tree)
#         self.simple_direct_irr = self.model.resources[0]
#         self.monsisaeki = self.model.resources[1]
#         self.monsisaeki_adopted = self.model.resources[2]
# 
#     def test_SimpleSolarIrradiance(self):
#         self.simple_direct_irr._pre_computations()
#         self.assertAlmostEqual(np.sum(self.simple_direct_irr.values), 0.0)
#         self.simple_direct_irr.update()
#         self.assertGreater(np.sum(self.simple_direct_irr.values), 100.0)
# 
#     def test_MonsiSaekiIrradiance(self):
#         self.monsisaeki.update()
#         self.assertGreater(np.sum(self.monsisaeki.values), 100.0)
# 
#     def test_MonsiSaekiIrradianceAdopted(self):
#         self.monsisaeki_adopted.update()
#         self.assertGreater(np.sum(self.monsisaeki_adopted.values), 100.0)
# 
#     def test_SimpleSoarIrradianceForest(self):
#         rnd_trees = CreateRandomSimpleTrees(treenum=100,
#                                             species=map(lambda x: str(x),
#                                                         range(10)),
#                                             bbox=[(0, 30), (0, 30)],
#                                             heights=[0, 15],
#                                             dbhs=[10, 20],
#                                             stage='sapling'
#                                             )
#         self.model.insert_event(rnd_trees)
#         self.model.events[0].activate()
#         for tree in self.model.objects:
#             crown = float(np.random.randint(5, 12)) * np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0],
#                               [1, 0, 0], [0, 1, 1], [1, 0, 1],
#                               [1, 1, 0], [1, 1, 1]]
#                              )
#             tree.add_crown(crown)
#         self.simple_direct_irr.update()  
#         self.assertGreater(np.sum(self.simple_direct_irr.values), 100.0)

            