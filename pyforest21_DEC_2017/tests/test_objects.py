from unittest import TestCase

from pyforest.objects.trees import Tree
import numpy as np

class TestBaseTreeObject(TestCase):
    def setUp(self):
        # mycrown is example of a tree component
        mycrown = {'par1': 0, 'par2': 12}

        self.tree = Tree(1, 1, name='mytree',
                         species='Mongolian Oak',
                         dbh=30,
                         height=26,
                         ddh=7)

    def test_tree(self):
        self.assertTrue(hasattr(self.tree, 'ddh'))
        self.assertTrue(hasattr(self.tree, 'dbh'))
        self.assertTrue(hasattr(self.tree, 'crown'))
        self.assertIsInstance(self.tree.crown, np.ndarray)
        self.assertTrue(hasattr(self.tree, 'species'))
        self.assertTrue(hasattr(self.tree, 'x'))
        self.assertTrue(hasattr(self.tree, 'y'))
        self.assertTrue(hasattr(self.tree, 'z'))
        self.assertTrue(hasattr(self.tree, 'height'))

    def test_tree_ids(self):
        self.tree1 = Tree(1, 1, name='mytree',
                          species='Mongolian Oak',
                          dbh=30,
                          height=26,
                          ddh=7)
        self.assertNotEqual(self.tree.id, self.tree1.id)

    def test_tree_height(self):
        self.assertEqual(self.tree.height, 26)
        self.assertEqual(self.tree.dbh, 30)
        self.assertEqual(self.tree.ddh, 7)
        self.assertEqual(self.tree.species, 'mongolian oak')

