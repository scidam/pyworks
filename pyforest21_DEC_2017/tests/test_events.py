
from unittest import TestCase

from pyforest.core import Model
from pyforest.events.random import CreateRandomSimpleTrees
from pyforest.objects.trees import Tree


class TestCreateRandomSimpleTrees(TestCase):

    def setUp(self):
        self.model = Model()
        rnd_trees = CreateRandomSimpleTrees(treenum=100,
                                            species=list(map(str, range(10))),
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 15],
                                            dbhs=[10, 100]
                                            )
        self.model.insert_event(rnd_trees)
        self.model.events[0].activate()

    def test_trees_created(self):
        self.assertEqual(len(self.model.objects), 100)

    def test_trees_really(self):
        for item in self.model.objects:
            self.assertIsInstance(item, Tree)

    def test_trees_positions(self):
        '''All trees generated should be inside bbox'''

        for item in self.model.objects:
            self.assertTrue(0 <= item.x <= 10)
            self.assertTrue(0 <= item.y <= 10)

    def test_trees_parameters(self):
        for item in self.model.objects:
            self.assertTrue(int(item.species) <= 10)
            self.assertEqual(item.ddh, 0)
            self.assertGreaterEqual(item.dbh, 10)

