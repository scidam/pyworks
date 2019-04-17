
from pyforest.actions import AbstractAction
from pyforest.actions.growth import (SaplingToAdultAction,
                                     SeedlingToSaplingAction)
from pyforest.actions.internal import (_ObjectHistoryRecorderAction,
                                       _FillModelMetasAction)
from pyforest.events import AbstractEvent
from pyforest.resources import AbstractResource
from pyforest.utils import load_inits


def _chek_data(data):
    # TODO: checking for data consistency
    pass


class AbstractObjectContainer(list):
    '''
    Currently, it is just a list, but some methods, such as `append`,
    could be overridden in the future...
    '''

    def select_by_type(self, typename):
        _typename = typename.lower()
        return AbstractObjectContainer(list(filter(lambda x: x.type == _typename,
                                              self)))

    def select_by_species(self, species):
        lspecies = list(map(str.lower, species))
        return AbstractObjectContainer(filter(lambda x: x.species in lspecies,
                                              self))

    def select_by_stages(self, stages):
        lstages = list(map(str.lower, stages))
        return AbstractObjectContainer(filter(lambda x: x.stage in lstages,
                                              self))


class AbstractBackend(object):
    def __init__(self, *args, **kwargs):
        pass


class AbstractSnapshots(object):

    def __init__(self, *args, **kwargs):
        pass


class AbstractModelMeta(object):
    def __init__(self, *args, **kwargs):
        self.object_coords = None
        self.object_types = None
        self.object_dbhs = None
        self.object_stages = None
        self.object_heights = None


class AbstractModel(object):
    '''Abstract class for representing models'''

    def __init__(self, *args, **kwargs):
        self.events = load_inits('events')
        self.actions = load_inits('actions')
        self.resources = load_inits('resources')
        self.data = {}
        if 'data' in kwargs: self.data.update(kwargs['data'])
        self.step = 0
        self.bbox = kwargs['bbox'] if 'bbox' in kwargs else [(0, 1), (0, 1)]
        self.objects = AbstractObjectContainer()
        self.seeds = {}
        # ---------------- auxiliary attributes -------------------------------
        self._actions_pre = []
        self._actions_post = []
        self._action_stream = None  # Just initialization
        self._meta = AbstractModelMeta()

    def _insert(self, fieldname, newitem, index=-1):
        if hasattr(self, fieldname):
            data = getattr(self, fieldname)
            if newitem.model is None:
                setattr(newitem, 'model', self)
            if index == -1:
                data.append(newitem)
            elif 0 <= index < len(data):
                data.insert(index + 1, newitem)
            else:
                data.append(newitem)
            setattr(self, fieldname, data)

    def insert_event(self, obj, index=-1):
        '''Inserts an event into the event's chain after a given index

        :param obj: an event to be inserted;
        :param index: where the event should be inserted;
                      default is -1, i.e. event will be appended;
        :type obj: `AbstractEvent`

        .. note::
            If index is invalid, function will work in a `silent mode`,
            that means the event will be appended to the event's chain

        # TODO: raises needed
        '''

        if isinstance(obj, AbstractEvent):
            self._insert('events', obj, index=index)
        else:
            # TODO: Should raise exception
            pass

    def prepend_action(self, newitem):
        '''Prepends an action into the action's chain

        :param newitem: an action to be inserted;
        :type newitem: `AbstractAction`

        # TODO: Type validation needed&raises
        '''
        if newitem.model is None:
                setattr(newitem, 'model', self)
        if hasattr(self, 'actions'):
            data = getattr(self, 'actions')
            setattr(self, 'actions', [newitem] + data)

    def prepend_event(self, newitem):
        '''Prepends an event into the event's chain

        :param newitem: an event to be inserted;
        :type newitem: `AbstractEvent`

        # TODO: Type validation needed&raises
        '''

        if newitem.model is None:
                setattr(newitem, 'model', self)
        if hasattr(self, 'events'):
            data = getattr(self, 'events')
            setattr(self, 'events', [newitem] + data)

    def insert_action(self, obj, index=-1):
        '''Inserts an action into the action's chain after a given index

        :param obj: an action to be inserted;
        :param index: where the action should be inserted;
                      default is -1, i.e. action will be appended;
        :type obj: `AbstractAction`

        .. note::
            If index is invalid, function will work in a `silent mode`,
            that means the action will be appended to the action's chain

        # TODO: raises needed
        '''

        if isinstance(obj, AbstractAction):
            self._insert('actions', obj, index=index)
        else:
            # TODO: Should raise exception
            pass

    def insert_resource(self, obj):
        '''Inserts a resource into the model resource list

        Resources are treated as unordered list.

        :param obj: a resource to be inserted;
        :param index: where the resource should be inserted;
                      default is -1, i.e. action will be appended;
        :type obj: `AbstractResource`

        # TODO: raises needed
        '''

        if isinstance(obj, AbstractResource):
            self._insert('resources', obj, index=-1)
        else:
            # TODO: Should raise exception
            pass

    def _to_stream(self, lists):
        '''Converts list of lists to list'''
        import collections

        def _flatten(inp):
            for el in inp:
                if isinstance(el, collections.Iterable):
                    for sub in _flatten(el):
                        yield sub
                else:
                    yield el
        self._action_stream = list(_flatten(lists))

    def _preliminary_runs(self):

        # Internal actions should be here
        self._insert('_actions_pre', _FillModelMetasAction())

        self._insert('_actions_post', SeedlingToSaplingAction())
        self._insert('_actions_post', SaplingToAdultAction())
        self._insert('_actions_post', _ObjectHistoryRecorderAction())

        # Build action stream iterator
        self._to_stream([self._actions_pre,
                         self.events,
                         self.actions,
                         self._actions_post
                         ])

    def run(self, until=1):
        self._preliminary_runs()
        # Main modeling loop (iterate over all actions and execute them)
        while self.step <= until:
            for action in self._action_stream:
                action.activate()
            self.step += 1
        self.step -= 1

    def _run_generator(self, until=1):
        self._preliminary_runs()
        while self.step <= until:
            for action in self._action_stream:
                action.activate()
            self.step += 1
            yield self
