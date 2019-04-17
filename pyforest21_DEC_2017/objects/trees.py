from pyforest.objects import  WoodyPlantMixin
from pyforest.utils import setup_value

import numpy as np


TREE_STAGES = ('seedling',
               'sapling',
               'adult',
               'dead',
               'snag',
               'debris'
               )


class AbstractTree(WoodyPlantMixin):
    def __init__(self, *args, **kwargs):
        super(AbstractTree, self).__init__(*args, **kwargs)
        setup_value(self, kwargs, 'species')
        setup_value(self, kwargs, 'height', value=0)
        setup_value(self, kwargs, 'dbh', value=0)
        setup_value(self, kwargs, 'ddh', value=0)
        setup_value(self, kwargs, 'crown', value=np.array([]))
        self.type = 'tree'
        if 'stage' in kwargs:
            if kwargs['stage'] in TREE_STAGES:
                self._stage = kwargs['stage']
            else:
                self._stage = 'seedling'
        else:
            self._stage = 'seedling'

    @property
    def stage(self):
        return self._stage

    @stage.setter
    def stage(self, value):
        if value in TREE_STAGES:
            self._stage = value


class Tree(AbstractTree):

    def __init__(self, *args, **kwargs):
        super(Tree, self).__init__(*args, **kwargs)
        if isinstance(self.species, str):
            self.species = self.species.lower()

    def _tree_history_by_par(self, par):
        return self._meta.history[par]\
            if par in self._meta.history else None

    def _growth_rate_by_par(self, par, steps):
        hist = self._tree_history_by_par(par)
        steps = 5 if steps > 5 else steps
        steps = 2 if steps == 1 else steps
        if hist is not None:
            hist = np.array(hist)
            hist = hist[~np.isnan(hist)]
            return np.mean(np.diff(hist[-steps:])) if len(hist) > 0 else np.nan
        else:
            return np.nan

    def get_dbh_history(self):
        '''Returns `dbh` history of a tree if it is available

        Only five timesteps are recordered.'''

        return self._tree_history_by_par('dbh')

    def get_ddh_history(self):
        '''Returns `ddh` history of a tree if it is available

        Only five timesteps are recordered.'''

        return self._tree_history_by_par('ddh')

    def get_dbh_rate(self, steps=2):
        '''Gets estimate of growing speed

        :param steps: the number of backward steps to get average;
                      if `steps` > 5, it will be silently reduced to 5.
                      If `steps` == 1, it will be silently increaced to 2.
                      Allowed values of steps are 2, 3, 4 or 5.
                      Default is 2.
        :type steps: int
        :return: average growth rate of a tree
                 (or `None` if no tree dbh-history is available).
        :rtype: float
        '''

        return self._growth_rate_by_par('dbh', steps)

    def get_ddh_rate(self, steps=2):
        '''Gets estimate of growing speed

        :param steps: the number of backward steps to get average;
                      if `steps` > 5, it will be silently reduced to 5.
                      If `steps` == 1, it will be silently increaced to 2.
                      Allowed values of steps are 2, 3, 4 or 5.
                      Default is 2.

        :type steps: int
        :return: average growth rate of a tree
                 (or `None` if no tree ddh-history is available).
        :rtype: float
        '''

        return self._growth_rate_by_par('ddh', steps)

    def get_age_on_stage(self, stage):
        '''Returns time that tree spent
        on a requested stage.

        :param stage: string, requested stage
        :type stage: str
        :return: the number of timesteps when
                 a tree had requested stage
        :rtype: int
        '''

        return self._meta.get_age_on_stage(stage)


