
from unittest import TestCase

from pyforest.actions.allometry import TreeDiamHeightLinearAllometry
from pyforest.actions.death import (KillRandomlyAction,
                                    KillRandomlyAtStepsAction,
                                    DebrisRemoverAction,
                                    KillRandomlyBySpeciesAction,
                                    KillRandomlyBySpeciesAtStepsAction,
                                    KillWhenTooLowGrowthSpeedAction,
                                    GompertzKillerAction,
                                    KillOldSaplings,
                                    KillOldSaplingsPoisson,
                                    KillOldSeedlings,
                                    KillOldSeedlingsPoisson
                                    )
from pyforest.actions.exclusions import ExcludeOutsideBbox
from pyforest.actions.growth import (ConstantRadialGrowthAction,
                                     PowerHeightGrowthActions,
                                     SaplingToAdultAction,
                                     SeedlingToSaplingAction,
                                     RandomRadialGrowthAction)
from pyforest.actions.internal import (_ObjectHistoryRecorderAction,
                                       _FillModelMetasAction)
from pyforest.actions.seeds import (ConstantProbabilityAction,
                                    RemoveOldSeedsAction,
                                    HarvestSeedsRandomlyAction)
from pyforest.actions.spreads import (UniformDisperseTreeAction,
                                      RadialDecayTreeSeedingAction)
from pyforest.core import Model
from pyforest.events.random import CreateRandomSimpleTrees
from pyforest.objects.data import pool
from pyforest.objects.data.fallback import *
from pyforest.objects.shrubs import Shrub
from pyforest.objects.trees import Tree

import numpy as np


pool.autodiscover('./objects/data')


# from objects.trees import Tree
class TestUniformDisperseTreeAction(TestCase):
    '''Testing seed spreading action'''

    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        rnd_trees = CreateRandomSimpleTrees(treenum=100,
                                            species=list(map(str, range(10))),
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 15],
                                            dbhs=[10, 100]
                                            )
        myseeding = UniformDisperseTreeAction(intensity=50,
                                              distribution='uniform',
                                              species='oak tree'
                                              )
        myseeding1 = UniformDisperseTreeAction(intensity=60,
                                               distribution='poisson',
                                               species='fir tree'
                                               )
        self.model.insert_action(myseeding)
        self.model.insert_event(rnd_trees)
        self.model.insert_action(myseeding1)
        for act in self.model.actions:
            act.activate()
        for ev in self.model.events:
            ev.activate()

    def test_seeds_creation(self):
        '''Euristic test for seeds spreading'''

        self.assertIn('oak tree', self.model.seeds.keys())
        self.assertIn('fir tree', self.model.seeds.keys())
        self.assertEqual(self.model.seeds['oak tree'][-1][0], 0)
        self.assertEqual(len(self.model.seeds['oak tree'][-1]), 50)
        self.assertEqual(self.model.seeds['fir tree'][-1][0], 0)
        self.assertGreater(max(self.model.seeds['fir tree'][1]), 10)
        self.assertGreater(max(self.model.seeds['oak tree'][1]), 10)
        self.assertLessEqual(max(self.model.seeds['oak tree'][0]), 10)
        self.assertLessEqual(max(self.model.seeds['fir tree'][0]), 10)

    def test_seeds_another_on_timestep(self):
        '''Check for seed array in the current model have been updated'''
        self.model.step += 1
        for act in self.model.actions:
            act.activate()
        self.assertEqual(len(self.model.seeds['oak tree'][-1]), 100)
        self.assertEqual(self.model.seeds['oak tree'][-1][0], 0)
        self.assertEqual(self.model.seeds['oak tree'][-1][-1], 1)


class TestSeedGermination(TestCase):
    '''Testing seed germination'''

    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        myseeding = UniformDisperseTreeAction(intensity=50,
                                              distribution='uniform',
                                              species='quercus mongolica'
                                              )
        seedling = ConstantProbabilityAction(mortality=0.5,
                                             germination=0.4,
                                             species='Quercus MonGolica'
                                             )
        self.model.insert_action(myseeding)
        self.model.insert_action(seedling)
        self.model.actions[0].activate()

    def test_seeds_created(self):
        '''Just seeds creation without germination'''

        sizes = self.model.seeds['quercus mongolica'].shape
        self.assertGreaterEqual(sizes[1], 20)

    def test_seeds_unchanged_state(self):
        self.model.actions[-1].activate()
        sizes = self.model.seeds['quercus mongolica'].shape
        self.assertGreaterEqual(sizes[1], 0)

    def test_seeds_germinated(self):
        self.model.actions[-1].activate()
        self.assertGreater(len(self.model.objects), 0)

    def test_seedlings_created(self):
        self.model.actions[-1].activate()
        seedling = self.model.objects[0]
        self.assertEqual(seedling.stage, 'seedling')

    def test_seedlings_parameters(self):
        self.model.actions[-1].activate()
        nleave = self.model.seeds['quercus mongolica'].shape[1]
        self.assertGreater(nleave, 0)
        self.assertLess(nleave, 40)

    def test_kill_all_seeds(self):
        act = ConstantProbabilityAction(mortality=1,
                                        germination=0.0,
                                        species='Quercus MonGolica'
                                        )
        self.model.insert_action(act)
        self.model.actions[-1].activate()
        nleave = self.model.seeds['quercus mongolica'].shape[1]
        self.assertEqual(nleave, 0)
        self.assertEqual(len(self.model.objects), 0)

    def test_germinate_all_seeds(self):
        act = ConstantProbabilityAction(mortality=0,
                                        germination=1.0,
                                        species='Quercus MonGolica'
                                        )
        self.model.insert_action(act)
        self.model.actions[-1].activate()
        nleave = self.model.seeds['quercus mongolica'].shape[1]
        self.assertEqual(nleave, 0)
        self.assertEqual(len(self.model.objects), 50)

    def test_probablity_greater_1(self):
        act = ConstantProbabilityAction(mortality=0.1,
                                        germination=1.0,
                                        species='Quercus MonGolica'
                                        )
        self.model.insert_action(act)
        # TODO: It will be implemented, and should changed!
        with self.assertRaises(NotImplementedError):
            self.model.actions[-1].activate()


class TestLinearAllometryAction(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        seedling = Tree(1, 0, ddh=0.1, height=1,
                        species='quercus mongolica',
                        stage='seedling')
        adult = Tree(0, 1, dbh=30, height=20, species='quercus mongolica',
                     stage='adult')
        sapling = Tree(1, 1,  dbh=15, height=8, species='quercus mongolica',
                       stage='sapling')
        adult1 = Tree(5, 1, dbh=30, height=20, species='betula mandshurica',
                      stage='adult')
        self.model.objects.extend([seedling, adult, sapling, adult1])
        # 0
        act = TreeDiamHeightLinearAllometry(model=self.model, parname='height',
                                            species='quercus mongolica')
        self.model.insert_action(act)
        # 1
        act1 = TreeDiamHeightLinearAllometry(model=self.model, parname='dbh',
                                             species='quercus mongolica')
        self.model.insert_action(act1)
        # 2
        act2 = TreeDiamHeightLinearAllometry(model=self.model,
                                             parname='height', species='all')
        self.model.insert_action(act2)

    def test_seedlings_correction(self):
        '''Performs correction by height'''

        trees = self.model.objects.select_by_type('tree').select_by_species(['quercus mongolica'])
        old = (trees[0].ddh, trees[0].height)
        olddbh = trees[0].dbh
        self.model.actions[0].activate()
        self.assertNotEqual(old, (trees[0].ddh, trees[0].height))
        self.assertEqual(olddbh, trees[0].dbh)

    def test_adult_correction(self):
        '''Performs correction by dbh'''
        trees = self.model.objects.select_by_type('tree').select_by_species(['quercus mongolica'])
        betula = self.model.objects.select_by_type('tree').select_by_species(['betula mandshurica'])[0]
        oldbet = (betula.dbh, betula.height)
        old = (trees[1].dbh, )
        self.model.actions[1].activate()
        trees1 = self.model.objects.select_by_type('tree').select_by_species(['quercus mongolica'])
        new = (trees1[1].dbh, )
        self.assertNotEqual(old, new)
        self.assertEqual(oldbet, (betula.dbh, betula.height))

    def test_all_species(self):
        trees = self.model.objects.select_by_type('tree').select_by_species(['quercus mongolica'])
        betula = self.model.objects.select_by_type('tree').select_by_species(['betula mandshurica'])[0]
        oldbet = (betula.dbh, betula.height)
        old = (trees[1].dbh, trees[1].height)
        self.model.actions[-1].activate()
        trees1 = self.model.objects.select_by_type('tree').select_by_species(['quercus mongolica'])
        new = (trees1[1].dbh, trees1[1].height)
        self.assertNotEqual(old, new)
        self.assertNotEqual(oldbet, (betula.dbh, betula.height))


class TestRemoveOldSeedsAction(TestCase):

    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        self.model.seeds['quercus mongolica'] = np.array([[1], [2], [3]])
        act = RemoveOldSeedsAction()
        self.model.insert_action(act)

    def test_remove_old_seeds(self):
        self.model.step = 10
        self.assertEqual(self.model.seeds['quercus mongolica'].shape[1], 1)
        self.model.actions[-1].activate()
        self.assertEqual(self.model.seeds['quercus mongolica'].shape[1], 0)


class TestExclusionActions(TestCase):
    def setUp(self):
        self.model = Model()  # default unity bbox used
        self.model.seeds['quercus mongolica'] = np.array([[0.5, 1, 2], [0.5, 1, 2], [3, 2, 3]])
        act = ExcludeOutsideBbox()
        self.model.insert_action(act)
        adult = Tree(0.5, 0.5, dbh=30, height=20, species='betula mandshurica',
                     stage='adult')
        self.model.objects.append(adult)
        outside = Tree(1.5, 0.5, dbh=30, height=20, species='betula mandshurica',
                       stage='adult')
        self.model.objects.append(outside)

    def test_remove_seeds_and_trees(self):
        self.model.actions[0].activate()
        np.testing.assert_equal(self.model.seeds['quercus mongolica'][0],
                                np.array([0.5, 1]))
        self.assertEqual(len(self.model.objects), 1)
        self.assertEqual(self.model.objects[0].x, 0.5)


class TestConstantRadialGrowth(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        t1 = Tree(5, 1, dbh=30, height=20, species='betula mandshurica',
                  stage='adult')
        t2 = Tree(5, 2, dbh=35, height=20, species='betula mandshurica',
                  stage='sapling')
        t3 = Tree(5, 3, ddh=1, height=2, species='quercus mongolica',
                  stage='seedling')
        self.model.objects.extend([t1, t2, t3])

    def test_growth_for_only_oak(self):
        growth = ConstantRadialGrowthAction(species='quercus mongolica')
        old_ddh = self.model.objects[-1].ddh
        old_ddh_non_quercus = self.model.objects[0].ddh
        old_dbh_non_quercus = self.model.objects[0].dbh
        self.model.insert_action(growth)
        growth.activate()
        new_ddh = self.model.objects[-1].ddh
        self.assertEqual(old_ddh + DIAM_GROWTH_RATE_SEEDLING * 2.0,
                         new_ddh
                         )
        self.assertEqual(old_ddh_non_quercus, self.model.objects[0].ddh)
        self.assertEqual(old_dbh_non_quercus, self.model.objects[0].dbh)

    def test_growth_for_all(self):
        growth = ConstantRadialGrowthAction()
        old_dbh_betula1 = self.model.objects[0].dbh
        old_dbh_betula2 = self.model.objects[1].dbh
        old_ddh_quercus = self.model.objects[-1].ddh
        self.model.insert_action(growth)
        growth.activate()
        self.assertEqual(old_ddh_quercus + DIAM_GROWTH_RATE_SEEDLING * 2.0,
                         self.model.objects[-1].ddh)
        self.assertEqual(old_dbh_betula1 + DIAM_GROWTH_RATE_ADULT * 2.0,
                         self.model.objects[0].dbh)
        self.assertEqual(old_dbh_betula2 + DIAM_GROWTH_RATE_SAPLING * 2.0,
                         self.model.objects[1].dbh)

    def test_growth_two_timesteps(self):
        growth = ConstantRadialGrowthAction()
        old_dbh_betula1 = self.model.objects[0].dbh
        old_dbh_betula2 = self.model.objects[1].dbh
        old_ddh_quercus = self.model.objects[-1].ddh
        self.model.insert_action(growth)
        growth.activate()
        self.model.step += 1
        growth.activate()
        self.assertEqual(old_ddh_quercus + DIAM_GROWTH_RATE_SEEDLING * 4.0,
                         self.model.objects[-1].ddh)
        self.assertEqual(old_dbh_betula1 + DIAM_GROWTH_RATE_ADULT * 4.0,
                         self.model.objects[0].dbh)
        self.assertEqual(old_dbh_betula2 + DIAM_GROWTH_RATE_SAPLING * 4.0,
                         self.model.objects[1].dbh)


class TestPowerHeightGrowth(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        t1 = Tree(5, 1, dbh=30, height=20, species='betula mandshurica',
                  stage='adult')
        s1 = Shrub(5, 1, height=2, species='Unknown shrub', diam=3,
                   stage='live')
        self.model.objects.extend([t1, s1])
        act = PowerHeightGrowthActions()
        self.model.insert_action(act)

    def test_height_growth(self):
        oldh = self.model.objects[0].height
        olds = self.model.objects[1].height
        self.model.actions[0].activate()
        newh = self.model.objects[0].height
        news = self.model.objects[1].height
        self.assertEqual(olds, news)
        self.assertEqual(oldh + HEIGHT_GROWTH_MULT_ADULT * oldh **
                         HEIGHT_GROWTH_EXP_ADULT, newh)


class TestChangeSaplingToAdult(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        t1 = Tree(5, 1, dbh=10, height=20, species='betula mandshurica',
                  stage='sapling')
        t2 = Tree(5, 2, dbh=21, height=21, species='betula mandshurica',
                  stage='sapling')
        self.model.objects.extend([t1, t2])
        self.model.insert_action(SaplingToAdultAction())

    def test_is_stage_changed(self):
        self.model.actions[0].activate()
        self.assertEqual(self.model.objects[0].stage, 'sapling')
        self.assertEqual(self.model.objects[1].stage, 'adult')


class TestChangeSeedlingToSapling(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        t1 = Tree(5, 1, dbh=4, height=2, species='betula mandshurica',
                  stage='seedling')
        t2 = Tree(5, 2, dbh=1, height=4, species='betula mandshurica',
                  stage='seedling')
        self.model.objects.extend([t1, t2])
        self.model.insert_action(SeedlingToSaplingAction())

    def test_is_stage_changed(self):
        self.model.actions[0].activate()
        self.assertEqual(self.model.objects[0].stage, 'seedling')
        self.assertEqual(self.model.objects[1].stage, 'sapling')


class TestKillRandomlyAction(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        rnd_trees = CreateRandomSimpleTrees(treenum=100,
                                            species=list(map(str, range(10))),
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 15],
                                            dbhs=[10, 100],
                                            stage="adult"
                                            )
        self.model.insert_event(rnd_trees)
        self.model.events[-1].activate()
        self.model.insert_action(KillRandomlyAction())

    def test_unconditional_random_killer(self):
        self.assertEqual(len(self.model.objects.select_by_stages(['dead'])), 0)
        self.model.actions[-1].activate()
        self.assertGreater(len(self.model.objects.select_by_stages(['dead'])),
                           0)


class TestKillRandomlyAtStepsAction(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        rnd_trees = CreateRandomSimpleTrees(treenum=100,
                                            species=list(map(str, range(10))),
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 15],
                                            dbhs=[10, 100],
                                            stage="adult"
                                            )
        self.model.insert_event(rnd_trees)
        self.model.events[-1].activate()
        self.model.insert_action(KillRandomlyAtStepsAction(steps=[]))
        self.model.insert_action(KillRandomlyAtStepsAction(steps=[3]))

    def test_conditional_random_killer(self):
        self.model.step = 1
        self.model.actions[0].activate()
        self.model.actions[1].activate()
        self.assertEqual(len(self.model.objects.select_by_stages(['dead'])), 0)
        self.model.step = 3
        self.model.actions[0].activate()
        self.assertEqual(len(self.model.objects.select_by_stages(['dead'])), 0)
        self.model.actions[1].activate()
        self.assertGreater(len(self.model.objects.select_by_stages(['dead'])),
                           0)


class TestKillRandomlyBySpeciesAction(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        rnd_trees = CreateRandomSimpleTrees(treenum=100,
                                            species=['1', '2'],
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 15],
                                            dbhs=[10, 100],
                                            stage="adult"
                                            )
        self.model.insert_event(rnd_trees)
        self.model.events[-1].activate()
        self.model.insert_action(KillRandomlyBySpeciesAction(species=['2']))

    def test_remove_some_spec_species(self):
        old1 = len(self.model.objects.select_by_species(['1']).select_by_stages(['adult']))
        old2 = len(self.model.objects.select_by_species(['2']).select_by_stages(['adult']))
        self.model.actions[-1].activate()
        new1 = len(self.model.objects.select_by_species(['1']).select_by_stages(['adult']))
        new2 = len(self.model.objects.select_by_species(['2']).select_by_stages(['adult']))
        self.assertEqual(old1, new1)
        self.assertLess(new2, old2)


class TestKillRandomlyBySpeciesAtStepsAction(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        rnd_trees = CreateRandomSimpleTrees(treenum=100,
                                            species=['1', '2'],
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 15],
                                            dbhs=[10, 100],
                                            stage="adult"
                                            )
        self.model.insert_event(rnd_trees)
        self.model.events[-1].activate()
        self.model.insert_action(KillRandomlyBySpeciesAtStepsAction(steps=[3], species=['2']))

    def test_conditional_random_killer(self):
        old1 = len(self.model.objects.select_by_species(['1']).select_by_stages(['adult']))
        old2 = len(self.model.objects.select_by_species(['2']).select_by_stages(['adult']))
        self.model.step = 1
        self.model.actions[-1].activate()
        self.assertEqual(len(self.model.objects.select_by_species(['1']).select_by_stages(['adult'])),
                         old1)
        self.assertEqual(len(self.model.objects.select_by_species(['2']).select_by_stages(['adult'])),
                         old2)
        self.model.step = 3
        self.model.actions[0].activate()
        self.assertEqual(len(self.model.objects.select_by_species(['1']).select_by_stages(['adult'])),
                         old1)
        self.assertLess(len(self.model.objects.select_by_species(['2']).select_by_stages(['adult'])), old2)


class TestDebrisRemoverAction(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        rnd_trees = CreateRandomSimpleTrees(treenum=100,
                                            species=list(map(str,  range(10))),
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 15],
                                            dbhs=[10, 100],
                                            stage="debris"
                                            )
        self.model.insert_event(rnd_trees)
        self.model.events[-1].activate()
        self.model.insert_action(DebrisRemoverAction())
        self.model.insert_action(_ObjectHistoryRecorderAction())
        self.tda = pool.get_parameter('1', 'TREE_REMOVE_DEBRIS_AGE')
        self.sda = pool.get_parameter('1', 'SHRUB_REMOVE_DEBRIS_AGE')

    def test_remove_some_tree_debris(self):
        for i in range(10):
            self.model.actions[0].activate()
            self.model.actions[1].activate()
            self.assertEqual(len(self.model.objects), 100)
        self.model.actions[1].activate()
        self.model.actions[0].activate()
        self.assertEqual(len(self.model.objects), 0)


class Test_ObjectHistoryRecorderAction(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        # TODO: Probably should change behaviour of this event when stage = 'all';
        # Stages should be randomly chosen in this case
        rnd_trees = CreateRandomSimpleTrees(treenum=10,
                                            species=list(map(str, range(10))),
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 15],
                                            dbhs=[10, 100],
                                            stage="debris"
                                            )
        rnd_trees1 = CreateRandomSimpleTrees(treenum=1,
                                             species=list(map(str, range(10))),
                                             bbox=[(0, 10), (0, 10)],
                                             heights=[0, 15],
                                             dbhs=[10, 100],
                                             stage="adult"
                                             )
        rnd_trees2 = CreateRandomSimpleTrees(treenum=1,
                                             species=list(map(str,range(10))),
                                             bbox=[(0, 10), (0, 10)],
                                             heights=[0, 15],
                                             dbhs=[10, 100],
                                             stage="seedling"
                                             )
        self.model.insert_event(rnd_trees)
        self.model.insert_event(rnd_trees1)
        self.model.insert_event(rnd_trees2)
        self.model.events[0].activate()
        self.model.events[1].activate()
        self.model.events[2].activate()
        self.model.insert_action(_ObjectHistoryRecorderAction())

    def test_tree_stage_history_recording_action(self):
        for i in range(10):
            self.model.actions[0].activate()
        self.assertEqual(len(self.model.objects), 12)
        self.assertEqual(self.model.objects[0].get_age_on_stage('adult'), 0)
        self.assertEqual(self.model.objects[-1].get_age_on_stage('seedling'), 10)
        self.assertEqual(self.model.objects[0].get_age_on_stage('debris'), 10)
        self.model.actions[0].activate()
        self.assertEqual(self.model.objects[0].get_age_on_stage('debris'), 11)

    def _some_common_inits(self):
        for i in range(10):
            self.model.actions[0].activate()
            self.model.objects[-2].dbh += i
            self.model.objects[-1].ddh += i
            self.model.step += 1

    def test_tree_dbh_rate(self):
        self._some_common_inits()
        comput = self.model.objects[-2].get_dbh_rate(steps=5)
        self.assertAlmostEqual((8+7+6+5)/4.0, comput)

    def test_tree_dbh_history(self):
        '''Only five dbh values remembered'''

        self._some_common_inits()
        ret = self.model.objects[-2].get_dbh_history()
        self.assertEqual(len(ret), 5)
        self.assertAlmostEqual(ret[-1]-ret[-2], 8)
        self.assertAlmostEqual(ret[-2]-ret[-3], 7)
        self.assertAlmostEqual(ret[-3]-ret[-4], 6)
        self.assertAlmostEqual(ret[-4]-ret[-5], 5)

    def test_seedling_ddh_rate(self):
        self._some_common_inits()
        comput = self.model.objects[-1].get_ddh_rate(steps=5)
        self.assertAlmostEqual((8+7+6+5)/4.0, comput)

    def test_seedling_ddh_history(self):
        self._some_common_inits()
        ret = self.model.objects[-1].get_ddh_history()
        self.assertEqual(len(ret), 5)
        self.assertAlmostEqual(ret[-1]-ret[-2], 8)
        self.assertAlmostEqual(ret[-2]-ret[-3], 7)
        self.assertAlmostEqual(ret[-3]-ret[-4], 6)
        self.assertAlmostEqual(ret[-4]-ret[-5], 5)

    def test_adult_ddh_history(self):
        self._some_common_inits()
        ret = self.model.objects[-2].get_ddh_history()
        self.assertEqual(len(ret), 5)
        comput = self.model.objects[-2].get_ddh_rate()
        self.assertTrue(np.isnan(comput))


class TestRadialDecayTreeSeedingAction(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        rnd_trees = CreateRandomSimpleTrees(treenum=10,
                                            species=list(map(str, range(10))),
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 15],
                                            dbhs=[10, 100],
                                            stage='adult'
                                            )
        myseeding = RadialDecayTreeSeedingAction()
        self.model.insert_action(myseeding)
        self.model.insert_event(rnd_trees)
        self.model.events[0].activate()

    def test_seeds_created(self):
        self.assertEqual(len(self.model.seeds), 0)
        self.model.actions[0].activate()
        # Species are created
        self.assertGreater(len(self.model.seeds), 3)
        # Seeds are created for each species
        for sp in self.model.seeds:
            self.assertGreater(self.model.seeds[sp].shape[1], 10)
            self.assertEqual(self.model.seeds[sp].shape[0], 3)

    def test_seeds_diffrenet_places(self):
        self.model.actions[0].activate()
        for sp in self.model.seeds:
            self.assertNotEqual(self.model.seeds[sp][0][0],
                                self.model.seeds[sp][0][1])
            self.assertNotEqual(self.model.seeds[sp][1][0],
                                self.model.seeds[sp][1][1])


class TestKillWhenTooLowGrowthSpeedAction(TestCase):
    def setUp(self):
        self.model = Model()
        self.model.objects += [Tree(1, 1, dbh=30.2,
                                    height=20,
                                    species='Quercus mongolica',
                                    stage='adult')]
        self.model.objects += [Tree(0, 1, dbh=18.0,
                                    height=20,
                                    species='Quercus mongolica',
                                    stage='sapling')]
        self.model.objects += [Tree(1, 0, ddh=3.0,
                                    height=20,
                                    species='Quercus mongolica',
                                    stage='seedling')]
        self.model.insert_action(KillWhenTooLowGrowthSpeedAction())

    def test_no_tree_killed(self):
        self.model.insert_action(ConstantRadialGrowthAction(), 0)
        self.model.run(until=10)
        for item in self.model.objects:
            self.assertNotEqual(item.stage, 'dead')

    def test_when_zero_growth(self):
        self.model.prepend_action(ConstantRadialGrowthAction(species='quercus mongolica',
                                 override_pars=[['none'],
                                                [{'DIAM_GROWTH_RATE_SAPLING': 0.0,
                                                  'DIAM_GROWTH_RATE_ADULT': 0.0,
                                                  'DIAM_GROWTH_RATE_SEEDLING': 0.0},
                                                 ]]))
        self.model.run(until=10)
        for item in self.model.objects:
            self.assertEqual(item.stage, 'dead')

    def test_when_very_slow_growth(self):
        self.model.prepend_action(ConstantRadialGrowthAction(species='quercus mongolica',
                                 override_pars=[['none'],
                                                [{'DIAM_GROWTH_RATE_SAPLING': 1.0e-5,
                                                  'DIAM_GROWTH_RATE_ADULT': 1.0e-5,
                                                  'DIAM_GROWTH_RATE_SEEDLING': 1.0e-5
                                                  }]]))
        self.model.run(until=10)
        for item in self.model.objects:
            self.assertEqual(item.stage, 'dead')

    def test_slow_growth_adult_only(self):
        self.model.prepend_action(ConstantRadialGrowthAction(species='quercus mongolica',
                                 override_pars=[['quercus mongolica'],
                                                [{'DIAM_GROWTH_RATE_ADULT': 0.001,
                                                  'DIAM_GROWTH_RATE_SAPLING': 0.5,
                                                   'DIAM_GROWTH_RATE_SEEDLING': 0.5},
                                                 ]]))
        self.model.run(until=10)
        for item in self.model.objects:
            self.assertNotEqual(item.stage, 'adult')


class TestHarvestSeedsRandomlyAction(TestCase):

    def setUp(self):
        self.model = Model(bbox=[(0, 1), (0, 100)])
        self.model.insert_action(UniformDisperseTreeAction(species='Oak', intensity=300))
        self.model.insert_action(UniformDisperseTreeAction(species='Elm', intensity=400))
        self.model.insert_action(HarvestSeedsRandomlyAction())

    def test_some_seeds_removed(self):
        self.model.actions[0].activate()
        self.model.actions[1].activate()
        oldsize1 = len(self.model.seeds['Oak'][0])
        oldsize2 = len(self.model.seeds['Elm'][0])
        self.model.actions[2].activate()
        self.assertLess(len(self.model.seeds['Oak'][0]), oldsize1)
        self.assertLess(len(self.model.seeds['Elm'][0]), oldsize2)


class TestOverrideActionPars(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        t1 = Tree(5, 1, dbh=30, height=20, species='betula mandshurica',
                  stage='adult')
        t2 = Tree(5, 2, dbh=35, height=20, species='betula mandshurica',
                  stage='sapling')
        t3 = Tree(5, 3, ddh=1, height=2, species='quercus mongolica',
                  stage='seedling')
        self.model.objects.extend([t1, t2, t3])

    def test_pars_overriden(self):
        '''Test for pars was overriden and restored'''
        growth = ConstantRadialGrowthAction(species='quercus mongolica')
        old_ddh = self.model.objects[-1].ddh
        self.model.insert_action(ConstantRadialGrowthAction(species='quercus mongolica',
                                 override_pars=[['none'],
                                                [{'DIAM_GROWTH_RATE_SEEDLING': 0.0}]]))
        self.model.actions[-1].activate()
        new_ddh = self.model.objects[-1].ddh
        self.assertEqual(new_ddh, old_ddh)
        self.model.insert_action(ConstantRadialGrowthAction(species='quercus mongolica'))
        old_ddh = self.model.objects[-1].ddh
        self.model.actions[-1].activate()
        new_ddh = self.model.objects[-1].ddh
        self.assertGreater(new_ddh, old_ddh)


class Test_FillModelMetasAction(TestCase):
    def setUp(self):
        self.model = Model()
        self.model.objects += [Tree(1, 1, dbh=30.2,
                                    height=20,
                                    species='1',
                                    stage='adult')]
        self.model.objects += [Tree(0, 1, dbh=18.0,
                                    height=20,
                                    species='2',
                                    stage='sapling')]
        self.model.objects += [Tree(1, 0, ddh=3.0,
                                    height=20,
                                    species='3',
                                    stage='seedling')]
        self.model.insert_action(_FillModelMetasAction())
        self.model.insert_action(ConstantRadialGrowthAction())

    def test_save_meta_properly(self):
        self.model.actions[0].activate()
        self.assertEqual(self.model._meta.object_coords.shape, (3, 2))
        self.assertAlmostEqual(self.model._meta.object_coords[0, 0], 1)
        self.assertAlmostEqual(self.model._meta.object_coords[0, 1], 1)
        self.assertAlmostEqual(self.model._meta.object_coords[1, 0], 0)
        self.assertAlmostEqual(self.model._meta.object_coords[1, 1], 1)
        self.assertAlmostEqual(self.model._meta.object_coords[2, 0], 1)
        self.assertAlmostEqual(self.model._meta.object_coords[2, 1], 0)
        olddbhs = self.model._meta.object_dbhs
        oldstypes = self.model._meta.object_types
        self.assertEqual(oldstypes[0], 'tree')
        self.assertEqual(oldstypes[-1], 'tree')
        self.model.run(until=10)
        self.assertEqual(oldstypes[0], 'tree')
        self.assertEqual(oldstypes[-1], 'tree')
        newdbhs = self.model._meta.object_dbhs
        self.assertNotEqual(newdbhs[0], olddbhs[0])
        self.assertNotEqual(newdbhs[1], olddbhs[1])
        self.assertNotEqual(newdbhs[2], olddbhs[2])


class TestGompertzKillerAction(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 10)])
        rnd_trees = CreateRandomSimpleTrees(treenum=1000,
                                            species=list(map(str, range(10))),
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 15],
                                            dbhs=[10, 100],
                                            stage='sapling'
                                            )
        self.model.insert_event(rnd_trees)
        self.model.insert_action(GompertzKillerAction())
        self.model.events[0].activate()

    def test_for_killing_something(self):
        self.model.run(until=10)
        self.assertEqual(len(self.model.objects), 1000)
        self.assertLess(sum(self.model._meta.object_stages == 'sapling'), 1000)
        self.assertGreater(sum(self.model._meta.object_stages == 'sapling'), 0)
        self.assertGreater(sum(self.model._meta.object_stages == 'dead'), 0)


class TestRandomRadialGrowthAction(TestCase):
    def setUp(self):
        self.model = Model(bbox=[(0, 10), (0, 20)])
        t1 = Tree(5, 1, dbh=30, height=28, species='betula mandshurica',
                  stage='adult')
        t2 = Tree(5, 2, dbh=12, height=14, species='betula mandshurica',
                  stage='sapling')
        t3 = Tree(5, 3, ddh=1, height=0.5, species='quercus mongolica',
                  stage='seedling')
        self.model.objects.extend([t1, t2, t3])

    def test_growth_only_seedling(self):
        growth = RandomRadialGrowthAction(species='quercus mongolica',
                                          stages='seedling', steps=[1])
        old_ddh = self.model.objects[-1].ddh
        old_ddh_sapling = self.model.objects[1].dbh
        old_dbh_adult = self.model.objects[0].dbh
        self.model.insert_action(growth)
        self.model.step = 1  # to meet activation conditions
        growth.activate()
        new_ddh = self.model.objects[-1].ddh
        self.assertNotEqual(new_ddh, old_ddh)
        self.assertEqual(old_ddh_sapling, self.model.objects[1].dbh)
        self.assertEqual(old_dbh_adult, self.model.objects[0].dbh)

    def test_growth_excluding_condition(self):
        growth = RandomRadialGrowthAction(species='betula mandshurica',
                                          stages='seedling', steps=[1])
        old_ddh = self.model.objects[-1].ddh
        old_ddh_sapling = self.model.objects[1].dbh
        old_dbh_adult = self.model.objects[0].dbh
        self.model.insert_action(growth)
        growth.activate()
        new_ddh = self.model.objects[-1].ddh
        self.assertEqual(new_ddh, old_ddh)
        self.assertEqual(old_ddh_sapling, self.model.objects[1].dbh)
        self.assertEqual(old_dbh_adult, self.model.objects[0].dbh)

    def test_growth_only_one_timestep(self):
        growth = RandomRadialGrowthAction(species='quercus mongolica',
                                          stages='seedling', steps=[1])
        self.model.insert_action(growth)
        growth.activate()
        self.model.step = 2
        old_ddh = self.model.objects[-1].ddh
        old_ddh_sapling = self.model.objects[1].dbh
        old_dbh_adult = self.model.objects[0].dbh
        growth.activate()
        new_ddh = self.model.objects[-1].ddh
        self.assertEqual(new_ddh, old_ddh)
        self.assertEqual(old_ddh_sapling, self.model.objects[1].dbh)
        self.assertEqual(old_dbh_adult, self.model.objects[0].dbh)

    def test_growth_only_sapling(self):
        growth = RandomRadialGrowthAction(stages='sapling', steps=[1])
        old_ddh = self.model.objects[1].dbh
        old_dbh_adult = self.model.objects[0].dbh
        self.model.insert_action(growth)
        growth.activate()
        new_ddh = self.model.objects[1].ddh
        self.assertNotEqual(new_ddh, old_ddh)
        self.assertEqual(old_dbh_adult, self.model.objects[0].dbh)

    def test_growth_only_adult(self):
        growth = RandomRadialGrowthAction(stages='adult')
        old_dbh = self.model.objects[0].dbh
        old_ddh_sapling = self.model.objects[1].dbh
        self.model.insert_action(growth)
        growth.activate()
        new_dbh = self.model.objects[0].dbh
        self.assertNotEqual(new_dbh, old_dbh)
        self.assertEqual(old_ddh_sapling, self.model.objects[1].dbh)



class TestTooLongOnStageActions(TestCase):
    def setUp(self):
        self.model = Model()
        rnd_trees = CreateRandomSimpleTrees(treenum=100,
                                            species=['1', '2'],
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 2],
                                            dbhs=[1, 3],
                                            stage="seedling"
                                            )
        self.model.insert_event(rnd_trees)
        rnd_trees1 = CreateRandomSimpleTrees(treenum=100,
                                            species=['1', '2'],
                                            bbox=[(0, 10), (0, 10)],
                                            heights=[0, 7],
                                            dbhs=[10, 15],
                                            stage="sapling"
                                            )
        self.model.insert_event(rnd_trees1)

        self.model.events[0].activate()
        self.model.events[1].activate()

    def test_kill_old_saplings(self):
        self.model.insert_action(KillOldSaplings())
        self.assertEqual(len(self.model.objects), 200)
        self.model.run(until=12)
        self.assertEqual(len(self.model.objects.select_by_stages(['dead'])), 100)
        self.assertEqual(len(self.model.objects.select_by_stages(['seedling'])), 100)

    def test_kill_old_saplings_poisson(self):
        self.model.insert_action(KillOldSaplingsPoisson())
        self.assertEqual(len(self.model.objects), 200)
        self.model.run(until=12)
        self.assertLessEqual(len(self.model.objects.select_by_stages(['dead'])), 100)
        self.assertEqual(len(self.model.objects.select_by_stages(['seedling'])), 100)
        self.assertGreater(len(self.model.objects.select_by_stages(['dead'])), 70)

    def test_kill_old_seedlings(self):
        self.model.insert_action(KillOldSeedlings())
        self.assertEqual(len(self.model.objects), 200)
        self.model.run(until=12)
        self.assertEqual(len(self.model.objects), 100)

    def test_kill_old_seedlings_poisson(self):
        self.model.insert_action(KillOldSeedlingsPoisson())
        self.assertEqual(len(self.model.objects), 200)
        self.model.run(until=12)
        self.assertGreater(len(self.model.objects), 100)
        self.assertLess(len(self.model.objects), 200)

