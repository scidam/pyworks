from unittest import TestCase

import numpy as np
from pyforest.utils.randomizer import place_spatially


class TestPlaceSpatially(TestCase):
    def setUp(self):
        self.data = place_spatially(probgrid=np.array([[0, 1],
                                                      [0, 0]],
                                                      dtype=np.float),
                                    size=100)
        prob = np.zeros((10, 10))
        prob[0, 0] = 1.0
        prob[9, 9] = 1.0
        self.datacomplex = place_spatially(bbox=[(0, 5), (2, 12)],
                                           probgrid=prob, size=100)

    def test_place_spatially(self):
        self.assertGreater(sum(self.data[0] >= 0.5), 60)
        self.assertGreater(sum(self.data[1] <= 0.5), 60)

    def test_complex_spatially_placement(self):
        self.assertGreater(sum((self.datacomplex[0] < 0.5) *
                               (self.datacomplex[0] > 0)), 30)
        self.assertGreater(sum((self.datacomplex[1] < 3) *
                               (self.datacomplex[1] > 2)), 30)
        self.assertEqual(sum((self.datacomplex[1] > 4) *
                             (self.datacomplex[1] < 6)), 0)
        self.assertGreater(sum((self.datacomplex[0] > 4.5) *
                               (self.datacomplex[0] < 5)), 30)
        
