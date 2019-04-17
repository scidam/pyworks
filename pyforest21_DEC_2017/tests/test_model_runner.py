#coding: utf-8

import inspect
from unittest import TestCase
import pickle
from pyforest.actions.growth import ConstantRadialGrowthAction
from pyforest.core import MemoryBackend, Model, Snapshots
from pyforest.core import Model
from pyforest.objects.trees import Tree

try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO


class TestCommonRunnerStructure(TestCase):

    def setUp(self):
        self.model = Model()
        self.model.objects += [Tree(1, 1, dbh=30.2, height=20, species='Quercus mongolica', stage='adult')]
        self.model.objects += [Tree(0, 1, dbh=18.0, height=20, species='Quercus mongolica', stage='sapling')]
        self.model.objects += [Tree(1, 0, ddh=3.0, height=20, species='Quercus mongolica', stage='seedling')]

    def test_4_stages_structure(self):
        self.assertIsInstance(self.model._actions_pre, list)
        self.assertIsInstance(self.model._actions_post, list)
        self.assertIsInstance(self.model.actions, list)
        self.assertIsInstance(self.model.events, list)

    def test_run_exists(self):
        self.assertTrue(hasattr(self.model, 'run'))

    def test_run_callable(self):
        self.assertTrue(inspect.ismethod(getattr(self.model, 'run')))

    def test_run_has_until_kwarg(self):
        # Could be used `__code__`, but I prefer inspect...
        self.assertIn('until', inspect.getargspec(self.model.run).args)

    def test_run_has_until_eq_1(self):
        self.assertEqual((1,), inspect.getargspec(self.model.run).defaults)

    def test_actions_to_stream(self):
        self.model._to_stream([[0], 1, 2, [3, [4, 5]]])
        self.assertEqual(list(self.model._action_stream), list(range(6)))

    def test_exec_ten_empty_steps(self):
        self.model.run(until=10)
        self.assertEqual(self.model.step, 10)

    def test_history_was_recordered(self):
        olddbh = self.model.objects[0].get_dbh_history()
        self.assertIsNone(olddbh)
        self.model.run(until=10)
        histdbh = self.model.objects[0].get_dbh_history()
        # History is remembered for 5 steps only
        self.assertEqual(list(histdbh), [30.2]*5)

    def test_simple_growth(self):
        self.model.insert_action(ConstantRadialGrowthAction())
        self.model.run(until=10)
        histdbh = self.model.objects[0].get_dbh_history()
        self.assertNotEqual(histdbh[0], histdbh[-1])
        self.assertGreater(histdbh[-1], histdbh[-2])

    def test_sapling_to_adult_autotransform(self):
        self.model.insert_action(ConstantRadialGrowthAction())
        self.assertEqual(self.model.objects[-2].stage, 'sapling')
        self.model.run(until=10)
        self.assertEqual(self.model.objects[-2].stage, 'adult')

    def test_seedling_to_sapling_autotransform(self):
        self.model.insert_action(ConstantRadialGrowthAction())
        self.assertEqual(self.model.objects[-1].stage, 'seedling')
        self.model.run(until=10)
        self.assertEqual(self.model.objects[-1].stage, 'sapling')

    def test_run_generator_works(self):
        'Rungenerator is needed for making snapshots in time'
        self.model.insert_action(ConstantRadialGrowthAction())
        zz = self.model._run_generator(until=10)
        self.assertIsInstance(next(zz), Model)
        self.assertEqual(next(zz).step, 2)
        self.assertEqual(next(zz).step, 3)
        self.assertEqual(next(zz).step, 4)


class TestMemoryBackend(TestCase):

    def setUp(self):
        self.mem = MemoryBackend()
        self.m1 = Model()
        self.m2 = Model()
        self.m3 = Model()
        self.m1.objects = [1, 2, 3]
        self.m2.objects = [1, 2, 4]
        self.mem.extend([(1, self.m1), (2, self.m2), (3, self.m3)])

    def test_search_by_steps(self):
        self.assertIn(self.m1, self.mem.search_by_steps([1, 3]))
        self.assertNotIn(self.m2, self.mem.search_by_steps([1, 3]))
        self.assertIn(self.m3, self.mem.search_by_steps([1, 3]))

    def test_search_by_condition(self):
        def condition(model):
            '''Look for 4 in model states'''
            return 4 in model.objects
        self.assertIn(self.m2, self.mem.search_by_condition(condition))
        self.assertNotIn(self.m1, self.mem.search_by_condition(condition))
        self.assertNotIn(self.m3, self.mem.search_by_condition(condition))


class TestSnapshotBehaviour(TestCase):

    def setUp(self):
        self.model = Model()
        self.model.objects += [Tree(1, 1, dbh=30.2, height=20, species='Quercus mongolica', stage='adult')]
        self.model.objects += [Tree(0, 1, dbh=18.0, height=20, species='Quercus mongolica', stage='sapling')]
        self.model.objects += [Tree(1, 0, ddh=3.0, height=20, species='Quercus mongolica', stage='seedling')]
        self.model.insert_action(ConstantRadialGrowthAction())
        self.snapshooter = Snapshots()  # Use memory backend by default

    def test_record_ten_timesteps(self):
        olddbh = self.model.objects[0].dbh
        self.snapshooter.attach_model(self.model)
        self.snapshooter.record(until=10)
        mstate = self.snapshooter.get_snapshot(0)
        self.assertEqual(mstate.objects[0].dbh, olddbh)
        mstate1 = self.snapshooter.get_snapshot(1)
        self.assertGreater(mstate1.objects[0].dbh, olddbh)

    def test_init_laststates_properties(self):
        olddbh = self.model.objects[0].dbh
        self.snapshooter.attach_model(self.model)
        self.snapshooter.record(until=10)
        self.assertEqual(self.snapshooter.initstate.objects[0].dbh, olddbh)
        self.assertGreater(self.snapshooter.laststate.objects[0].dbh, olddbh)

    def test_serialize_model(self):
        '''Simple check for serializing deserializing model instance'''
        ss = BytesIO()
        pickle.dump(self.model, ss)
        ss.seek(0)
        mm = pickle.loads(ss.read())
        self.assertIsInstance(mm, Model)
        self.assertEqual(mm.objects[0].dbh, self.model.objects[0].dbh)


