from unittest import TestCase

from pyforest.actions import AbstractAction
from pyforest.actions.death import KillWhenTooLowGrowthSpeedAction
from pyforest.actions.seeds import HarvestSeedsRandomlyAction
from pyforest.core import Model
from pyforest.events import AbstractEvent
from pyforest.objects.shrubs import Shrub
from pyforest.objects.trees import Tree
from pyforest.resources import AbstractResource


class TestModelCreation(TestCase):

    def setUp(self):
        self.model = Model()
        self.model_with_pars = Model()
        # ------------- set ups of objects -------------
        actions = [AbstractAction(model=self.model_with_pars),
                   AbstractAction(model=self.model_with_pars)]
        events = [AbstractEvent(model=self.model_with_pars)]
        resources = [AbstractResource(model=self.model_with_pars),
                     AbstractResource(model=self.model_with_pars),
                     AbstractResource(model=self.model_with_pars),
                     ]

        self.model_with_pars.actions = actions
        self.model_with_pars.events = events
        self.model_with_pars.resources = resources

    def test_settingup_resources(self):
        testdata = {'value': 1, 'name': 'noname'}
        for item in self.model_with_pars.resources:
            item.data = testdata
        for item in self.model_with_pars.resources:
            self.assertEqual(item.data, testdata)

    def test_models_created(self):
        self.assertIsInstance(self.model, Model)
        self.assertIsInstance(self.model_with_pars, Model)

    def test_actions_inside(self):
        for item in self.model_with_pars.actions:
            self.assertIsInstance(item, AbstractAction)

    def test_events_inside(self):
        for item in self.model_with_pars.events:
            self.assertIsInstance(item, AbstractEvent)

    def test_using_insert_event(self):
        self.model_with_pars.events = []
        event = AbstractEvent()
        self.model_with_pars.insert_event(event)
        self.assertIsInstance(self.model_with_pars.events[0].model, Model)

    def test_using_insert_action(self):
        self.model_with_pars.actions = []
        action = AbstractAction()
        self.model_with_pars.insert_action(action)
        self.assertIsInstance(self.model_with_pars.actions[0].model, Model)

    def test_object_container_select_by_type(self):
        tree = Tree(1, 1, species='Mongolian Oak',
                    dbh=30,
                    height=26,
                    ddh=7)
        shrub = Shrub(3, 3, species='Nothing',
                      height=26,
                      diam=7)
        self.model.objects.append(tree)
        self.model.objects.append(shrub)
        self.assertEqual(self.model.objects.select_by_type('tree')[0], tree)
        self.assertEqual(self.model.objects.select_by_type('shrub')[0], shrub)


class TestWorkingWithActions(TestCase):
    ''' Actions & events controls: prepending, appending, insertion'''

    def setUp(self):
        self.model = Model()
        self.model.insert_action(KillWhenTooLowGrowthSpeedAction())
        class C(AbstractEvent):
            pass
        class D(AbstractEvent):
            pass
        self.A = C()
        self.B = D()
        self.CA = C
        self.CB = D

    def test_append_action(self):
        self.model.insert_action(HarvestSeedsRandomlyAction())
        self.assertIsInstance(self.model.actions[-1], HarvestSeedsRandomlyAction)
        self.assertIsInstance(self.model.actions[0], KillWhenTooLowGrowthSpeedAction)
        self.assertNotIsInstance(self.model.actions[0], HarvestSeedsRandomlyAction)

    def test_prepend_action(self):
        self.model.prepend_action(HarvestSeedsRandomlyAction())
        self.assertIsInstance(self.model.actions[0], HarvestSeedsRandomlyAction)
        self.assertIsInstance(self.model.actions[-1], KillWhenTooLowGrowthSpeedAction)

    def test_append_event(self):
        self.model.insert_event(self.A)
        self.model.insert_event(self.B)
        self.assertIsInstance(self.model.events[-1], self.CB)
        self.assertIsInstance(self.model.events[0], self.CA)

    def test_prepend_event(self):
        self.model.prepend_event(self.A)
        self.model.prepend_event(self.B)
        self.assertIsInstance(self.model.events[0], self.CB)
        self.assertIsInstance(self.model.events[-1], self.CA)

    def test_insert_in_position_actions(self):
        self.model.insert_action(AbstractAction())
        self.model.insert_action(AbstractAction())
        self.model.insert_action(HarvestSeedsRandomlyAction(), 1)
        self.assertIsInstance(self.model.actions[0],
                              KillWhenTooLowGrowthSpeedAction)
        self.assertIsInstance(self.model.actions[1], AbstractAction)
        self.assertIsInstance(self.model.actions[2],
                              HarvestSeedsRandomlyAction)
        self.assertIsInstance(self.model.actions[3], AbstractAction)

    def test_insert_in_poisition_events(self):
        self.model.insert_event(AbstractEvent())
        self.model.insert_event(self.A)
        self.model.insert_event(self.B, 0)
        self.assertIsInstance(self.model.events[0], AbstractEvent)
        self.assertIsInstance(self.model.events[1], self.CB)
        self.assertIsInstance(self.model.events[2], self.CA)


class TestModelMetaProperties(TestCase):
    def setUp(self):
        self.model = Model()

    def test_has_meta_obj_coords(self):
        self.assertIsNone(self.model._meta.object_coords)

    def test_has_meta_obj_dbhs(self):
        self.assertIsNone(self.model._meta.object_dbhs)

    def test_has_meta_obj_types(self):
        self.assertIsNone(self.model._meta.object_types)

    def test_has_meta_obj_stages(self):
        self.assertIsNone(self.model._meta.object_stages)

    def test_has_meta_obj_heights(self):
        self.assertIsNone(self.model._meta.object_heights)
        
