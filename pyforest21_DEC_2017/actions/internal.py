'''
These actions applied always in model run
'''
from collections import deque

from pyforest.actions import AbstractAction
from pyforest.actions import EachStepRunnerMixin
from pyforest.objects.shrubs import SHRUB_STAGES
from pyforest.objects.trees import TREE_STAGES

import numpy as np


class BaseInternalActionMixin(AbstractAction):
    '''The most base action for internal use
    '''
    pass


class _ObjectHistoryRecorderAction(EachStepRunnerMixin, AbstractAction):
    '''
    Save important object data in `_meta` attribute of :class:`AbstractObject`

    It is applied once per timestep.
    '''

    @staticmethod
    def _init_or_append(obj, where, what):
        if where not in obj:
            obj.update({where: deque([], 5)})
        else:
            obj[where].append(what)

    def process(self):
        # TODO: Revision needed
        for item in self.model.objects:
            if item.type == 'tree':
                self._init_or_append(item._meta.history,
                                     'crown_hashes',
                                     item.crown_hash)
                stages = TREE_STAGES
                self._init_or_append(item._meta.history, 'dbh', item.dbh)
                if item.stage == 'seedling':
                    self._init_or_append(item._meta.history, 'ddh', item.ddh)
                else:
                    self._init_or_append(item._meta.history, 'ddh', np.nan)
            elif item.type == 'shrub':
                self._init_or_append(item._meta.history,
                                     'crown_hashes',
                                     item.crown_hash)
                stages = SHRUB_STAGES
            else:
                stages = []
            for key in [x for x in stages
                        if x not in item._meta.history['stages']]:
                item._meta.history['stages'][key] = []
            for key in stages:
                if key == item.stage:
                    item._meta.history['stages'][key].append(True)
                else:
                    item._meta.history['stages'][key].append(False)


class _FillModelMetasAction(EachStepRunnerMixin, AbstractAction):
    '''
    Save metadata for at the beginning of each timestep 
    '''

    def process(self):
        if self.model.objects:
            _data = [[i.type, i.stage, i.dbh, i.height, i.x, i.y] for i in self.model.objects]
            _data = np.array(_data)
            self.model._meta.object_coords = _data[:, -2:].astype(np.float64)
            self.model._meta.object_types = _data[:, 0].ravel()
            self.model._meta.object_stages = _data[:, 1].ravel()
            self.model._meta.object_dbhs = _data[:, 2].astype(np.float64).ravel()
            self.model._meta.object_heights = _data[:, 3].astype(np.float64).ravel()
