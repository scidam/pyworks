'''
Mortality actions
'''

from collections import deque

from pyforest.actions import AbstractAction
from pyforest.actions import EachStepRunnerMixin, UniversalTreeActionMixin
from pyforest.core.base import AbstractObjectContainer
from pyforest.utils.randomizer import random, nrandom
from scipy.spatial import cKDTree

import numpy as np

# TODO: Complete refactoring needed: each step runner defines conditions of activations;

class KillRandomlyAction(EachStepRunnerMixin):
    '''
    Randomly kill anything in the plot

    **Parameters**

    No extra parameters needed for this actions.

    **How it works**

    It uses `DEATH_PROB_TREE_SEEDLING`,
    `DEATH_PROB_TREE_SAPLING`, `DEATH_PROB_TREE_ADULT`,
    `DEATH_PROB_SHRUB` parameters to decide would
    be an object to live or not.

    {0}
    '''.format(EachStepRunnerMixin.__activation_conds__)

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('DEATH_PROB_TREE_SAPLING',
                                 'DEATH_PROB_TREE_ADULT',
                                 'DEATH_PROB_TREE_SEEDLING',
                                 'DEATH_PROB_SHRUB')
        super(KillRandomlyAction, self).__init__(*args, **kwargs)
 
    def process(self):
        for item in self.model.objects:
            tochose = self._parameters.get(item.species, self._parameters['none'])
            if item.stage == 'sapling':
                prob = tochose.get('DEATH_PROB_TREE_SAPLING',
                                   self._parameters['none']['DEATH_PROB_TREE_SAPLING'])
            elif item.stage == 'adult':
                prob = tochose.get('DEATH_PROB_TREE_ADULT',
                                   self._parameters['none']['DEATH_PROB_TREE_ADULT'])
            elif item.stage == 'seedling':
                prob = tochose.get('DEATH_PROB_TREE_SEEDLING',
                                   self._parameters['none']['DEATH_PROB_TREE_SEEDLING'])
            elif item.stage == 'live':
                prob = tochose.get('DEATH_PROB_SHRUB',
                                   self._parameters['none']['DEATH_PROB_SHRUB'])
            else:
                prob = 0.0
            if random.random() <= prob:
                item.stage = 'dead'


class KillRandomlyAtStepsAction(KillRandomlyAction):
    '''
    Randomly kill anything in the plot

    :param steps: a list of timesteps of activation; default is empty list.
    :type steps: list

    No extra parameters needed for this actions.

    **How it works**

    The same behaviour as :class:`KillRandomlyAction`, but
    applied at specified timesteps only. If no timesteps will passed,
    it will never activated.

    {0}

    '''.format(KillRandomlyAction.__activation_conds__)


    def __init__(self, *args, **kwargs):
        super(KillRandomlyAtStepsAction, self).__init__(*args, **kwargs)
        self.activationsteps = kwargs['steps'] if 'steps' in kwargs else []

    @property
    def condition(self):
        return self.model.step in self.activationsteps


class DebrisRemoverAction(EachStepRunnerMixin, AbstractAction):
    '''
    Removes old woody debris from model

    **Parameters**

    No extra parameters needed for this actions.

    **How it works**

        *Every tree-type debris is removed if its current
        age is greater than species-specific parameter
        `TREE_REMOVE_DEBRIS_AGE`.

        *Every shrub-type debris is removed if its current
        age is greater than species-specific parameter
        `SHRUB_REMOVE_DEBRIS_AGE`.

    Currently, it handles both `tree` and `shrub`-type objects.

    {0}
    '''.format(EachStepRunnerMixin.__activation_conds__)

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('TREE_REMOVE_DEBRIS_AGE',
                                     'SHRUB_REMOVE_DEBRIS_AGE')
        super(DebrisRemoverAction, self).__init__(*args, **kwargs)

    def process(self):
        toremove = []
        for ind, item in enumerate(self.model.objects):
            tochose = self._parameters.get(item.species, self._parameters['none'])
            tage = tochose.get('TREE_REMOVE_DEBRIS_AGE',
                               self._parameters['none']['TREE_REMOVE_DEBRIS_AGE'])
            sage = tochose.get('SHRUB_REMOVE_DEBRIS_AGE',
                               self._parameters['none']['SHRUB_REMOVE_DEBRIS_AGE'])
            if item.type == 'tree':
                if item._meta.get_age_on_stage('debris') > tage:
                    toremove.append(ind)
            elif item.type == 'shrub':
                if item._meta.get_age_on_stage('debris') > sage:
                    toremove.append(ind)
        self.model.objects = AbstractObjectContainer([v for i, v in enumerate(self.model.objects) if i not in toremove])


class KillRandomlyBySpeciesAction(KillRandomlyAction):
    '''
    Do the same things as :class:`KillRandomlyAction` do, but
    affects on specified tree species only

    :param species: a list of species the action will applied to
    :type species: list

    **How it works**

    %s
    '''.format(KillRandomlyAction.__activation_conds__)

    def __init__(self, *args, **kwargs):
        self._required_parameters = ['DEATH_PROB_TREE_SAPLING',
                                     'DEATH_PROB_TREE_ADULT',
                                     'DEATH_PROB_TREE_SEEDLING',
                                     'DEATH_PROB_SHRUB']   
        super(KillRandomlyBySpeciesAction, self).__init__(*args, **kwargs)
        self._species = kwargs['species']

    def process(self):
        for item in self.model.objects.select_by_species(self._species):
            tochose = self._parameters.get(item.species, self._parameters['none'])
            if item.stage == 'sapling':
                prob = tochose.get('DEATH_PROB_TREE_SAPLING',
                                   self._parameters['none']['DEATH_PROB_TREE_SAPLING'])
            elif item.stage == 'adult':
                prob = tochose.get('DEATH_PROB_TREE_ADULT',
                                   self._parameters['none']['DEATH_PROB_TREE_ADULT'])
            elif item.stage == 'seedling':
                prob = tochose.get('DEATH_PROB_TREE_SEEDLING',
                                   self._parameters['none']['DEATH_PROB_TREE_SEEDLING'])
            elif item.stage == 'live':
                prob = tochose.get('DEATH_PROB_SHRUB',
                                   self._parameters['none']['DEATH_PROB_SHRUB'])
            else:
                prob = 0.0
            if random.random() <= prob:
                item.stage = 'dead'


class KillRandomlyBySpeciesAtStepsAction(KillRandomlyBySpeciesAction):
    '''
    Do the same things as :class:`KillRandomlyBySpeciesAction` do, but
    affects on specified tree species only

    :param species: a list of species the action will applied to
    :type species: list

    **How it works**

    {0}

    '''.format(KillRandomlyBySpeciesAction.__activation_conds__)

    def __init__(self, *args, **kwargs):
        super(KillRandomlyBySpeciesAtStepsAction,
              self).__init__(*args, **kwargs)
        self.activationsteps = kwargs['steps'] if 'steps' in kwargs else []

    @property
    def condition(self):
        return self.model.step in self.activationsteps


class KillWhenTooLowGrowthSpeedAction(EachStepRunnerMixin, AbstractAction):
    '''
    It is applied to all adult trees

    # TODO: Docs needed

    **How it works**

    It estimates mean growth speed (dbh increments) taking
    into account `MEAN_GROWTH_SPEED_NSTEPS` and
    `MIN_DBH_SPEED_FOR_DEATH`.

    {0}
    '''.format(EachStepRunnerMixin.__activation_conds__)

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('MEAN_GROWTH_SPEED_NSTEPS_SEEDLING',
                                     'MEAN_GROWTH_SPEED_NSTEPS_SAPLING',
                                     'MEAN_GROWTH_SPEED_NSTEPS_ADULT',
                                     'MIN_DDH_SPEED_FOR_DEATH_SEEDLING',
                                     'MIN_DBH_SPEED_FOR_DEATH_SAPLING',
                                     'MIN_DBH_SPEED_FOR_DEATH_ADULT')
        self._memory = {}
        super(KillWhenTooLowGrowthSpeedAction, self).__init__(*args, **kwargs)

    def process(self):
        for item in self.model.objects.select_by_type('tree').select_by_stages(['seedling',
                                                                                'sapling',
                                                                                'adult']):
            tochose = self._parameters.get(item.species, self._parameters['none'])
            if item.stage == 'seedling':
                vddh = item.get_ddh_rate()
                if item.id in self._memory:
                    self._memory[item.id].append(vddh)
                else:
                    n = tochose.get('MEAN_GROWTH_SPEED_NSTEPS_SEEDLING',
                                    self._parameters['none']['MEAN_GROWTH_SPEED_NSTEPS_SEEDLING'])
                    self._memory.update({item.id: deque([], n)})
                cmem = self._memory[item.id]
                v_min = tochose.get('MIN_DDH_SPEED_FOR_DEATH_SEEDLING',
                                   self._parameters['none']['MIN_DDH_SPEED_FOR_DEATH_SEEDLING'])
            elif item.stage == 'sapling':
                vdbh = item.get_dbh_rate()
                if item.id in self._memory:
                    self._memory[item.id].append(vdbh)
                else:
                    n = tochose.get('MEAN_GROWTH_SPEED_NSTEPS_SAPLING',
                                    self._parameters['none']['MEAN_GROWTH_SPEED_NSTEPS_SAPLING'])
                    self._memory.update({item.id: deque([], n)})
                cmem = self._memory[item.id]
                v_min = tochose.get('MIN_DBH_SPEED_FOR_DEATH_SAPLING',
                                   self._parameters['none']['MIN_DBH_SPEED_FOR_DEATH_SAPLING'])
            elif item.stage == 'adult':
                vdbh = item.get_dbh_rate()
                if item.id in self._memory:
                    self._memory[item.id].append(vdbh)
                else:
                    n = tochose.get('MEAN_GROWTH_SPEED_NSTEPS_ADULT',
                                    self._parameters['none']['MEAN_GROWTH_SPEED_NSTEPS_ADULT'])
                    self._memory.update({item.id: deque([], n)})
                cmem = self._memory[item.id]
                v_min = tochose.get('MIN_DBH_SPEED_FOR_DEATH_ADULT',
                                   self._parameters['none']['MIN_DBH_SPEED_FOR_DEATH_ADULT'])
            if len(cmem) == cmem.maxlen and\
               np.nanmean(cmem) <= v_min:
                    item.stage = 'dead'


class GompertzKillerAction(UniversalTreeActionMixin):
    r'''
    Kill nearest trees according to the Gompertz law

    {0}

    **How it works**

    For each tree object selected for evaluation, the action looks for neighbors
    growing within
    radius `GOMPERTZ_KILLER_NEIGH_RADIUS` and having
    height, that is greater species-specific 
    `GOMPERTZ_KILLER_MIN_HEIGHT_TREE` parameter.
    The number of such object is a tree density value, that affects on probability of death for the object. 

    This probability is computed according to the Gompertz law:

    :math:`prob = \exp{{-\beta \cdot \exp{{-\gamma * (density - \delta)}}}}`,

    where :math:`\beta` is

        * `GOMPERTZ_KILLER_BETA_SEEDLING`, `GOMPERTZ_KILLER_BETA_SAPLING` or `GOMPERTZ_KILLER_BETA_ADULT`

    :math:`\gamma` is:

        * `GOMPERTZ_KILLER_GAMMA_SEEDLING`, `GOMPERTZ_KILLER_GAMMA_SAPLING` or `GOMPERTZ_KILLER_GAMMA_ADULT`

    :math:`\delta`:

        * `GOMPERTZ_KILLER_DELTA_SEEDLING`, `GOMPERTZ_KILLER_DELTA_SAPLING` or `GOMPERTZ_KILLER_DELTA_ADULT`

    When the `prob` parameter is computed, the Bernoulli trial
    is simulated to decide whether the object will be killed or not.

    {1}
    '''.format(UniversalTreeActionMixin.__common_par_docs__,
               UniversalTreeActionMixin.__activation_conds__)

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('GOMPERTZ_KILLER_BETA_SEEDLING',
                                 'GOMPERTZ_KILLER_GAMMA_SEEDLING',
                                 'GOMPERTZ_KILLER_DELTA_SEEDLING',
                                 'GOMPERTZ_KILLER_BETA_ADULT',
                                 'GOMPERTZ_KILLER_GAMMA_ADULT',
                                 'GOMPERTZ_KILLER_DELTA_ADULT',
                                 'GOMPERTZ_KILLER_BETA_SAPLING',
                                 'GOMPERTZ_KILLER_GAMMA_SAPLING',
                                 'GOMPERTZ_KILLER_DELTA_SAPLING',
                                 'GOMPERTZ_KILLER_MIN_HEIGHT_TREE',
                                 'GOMPERTZ_KILLER_NEIGH_RADIUS')
        self.stage = kwargs['stage'] if 'stage' in kwargs else 'all'
        super(GompertzKillerAction, self).__init__(*args, **kwargs)

    def _make_selection(self):
        selection = self.object_selector()
        if self.stage != 'all':
            selector = [self.stage]
            selector = list(set(selector) - set(['dead', 'snag', 'debris']))
        else:
            selector = ['seedling', 'sapling', 'adult']
        selection = selection.select_by_stages(selector)
        return selection

    def process(self):
        mheight_filter = self._pool.get_parameter('none',
                                                  'GOMPERTZ_KILLER_MIN_HEIGHT_TREE')
        rmin_filter = self._pool.get_parameter('none',
                                               'GOMPERTZ_KILLER_NEIGH_RADIUS')
        metadata = self.model._meta
        indexer = (metadata.object_heights >= mheight_filter) *\
                  (metadata.object_stages != 'dead') *\
                  (metadata.object_stages != 'debris') *\
                  (metadata.object_stages != 'snag')
        coords = metadata.object_coords[indexer]
        if coords.any():
            kdtree = cKDTree(coords)
        else:
            kdtree = None
        for item in self._make_selection():
            tochose = self._parameters.get(item.species, self._parameters['none'])
            if item.stage == 'seedling':
                beta = tochose.get('GOMPERTZ_KILLER_BETA_SEEDLING',
                                   self._parameters['none']['GOMPERTZ_KILLER_BETA_SEEDLING'])
                gamma = tochose.get('GOMPERTZ_KILLER_GAMMA_SEEDLING',
                                   self._parameters['none']['GOMPERTZ_KILLER_GAMMA_SEEDLING'])
                delta = tochose.get('GOMPERTZ_KILLER_DELTA_SEEDLING',
                                   self._parameters['none']['GOMPERTZ_KILLER_DELTA_SEEDLING'])
            elif item.stage == 'adult':
                beta = tochose.get('GOMPERTZ_KILLER_BETA_ADULT',
                                   self._parameters['none']['GOMPERTZ_KILLER_BETA_ADULT'])
                gamma = tochose.get('GOMPERTZ_KILLER_GAMMA_ADULT',
                                   self._parameters['none']['GOMPERTZ_KILLER_GAMMA_ADULT'])
                delta = tochose.get('GOMPERTZ_KILLER_DELTA_ADULT',
                                   self._parameters['none']['GOMPERTZ_KILLER_DELTA_ADULT'])                
            elif item.stage == 'sapling':
                beta = tochose.get('GOMPERTZ_KILLER_BETA_SAPLING',
                                   self._parameters['none']['GOMPERTZ_KILLER_BETA_SAPLING'])
                gamma = tochose.get('GOMPERTZ_KILLER_GAMMA_SAPLING',
                                   self._parameters['none']['GOMPERTZ_KILLER_GAMMA_SAPLING'])
                delta = tochose.get('GOMPERTZ_KILLER_DELTA_SAPLING',
                                   self._parameters['none']['GOMPERTZ_KILLER_DELTA_SAPLING'])
            if kdtree:
                density = float(len(kdtree.query_ball_point([item.x,
                                                            item.y],
                                                            rmin_filter)))
            else:
                density = 0.0
            prob = np.exp(-beta * np.exp(-gamma * (density - delta)))
            if random.random() <= prob:
                item.stage = 'dead'


class KillOldSeedlings(UniversalTreeActionMixin):
    '''Kills seedlings that don't change its stage too long

    {0}

    **How it works**

    It looks for each sapling that existing in the plot more than
    `MAX_SEEDLING_AGE` timesteps and kill it by removing
    from the model plot.

    {1}

    '''.format(UniversalTreeActionMixin.__common_par_docs__,
               UniversalTreeActionMixin.__activation_conds__)

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('MAX_SEEDLING_AGE',)
        super(KillOldSeedlings, self).__init__(*args, **kwargs)

    def process(self):
        for item in self.object_selector().select_by_stages(['seedling']):
            tochose = self._parameters.get(item.species, self._parameters['none'])
            param = tochose.get('MAX_SEEDLING_AGE',
                                self._parameters['none']['MAX_SEEDLING_AGE'])
            if item._meta.history['stages']:
                if sum(item._meta.history['stages']['seedling']) > param:
                    self.model.objects.remove(item)


class KillOldSeedlingsPoisson(UniversalTreeActionMixin):
    '''Kills seedlings that don't change its stage too long

    {0}

    **How it works**

    It looks for each seedling that existing in the plot more than
    :math:`tau` timesteps, where :math:`tau` comes from
    Poisson distribution with parameter `POISSON_LAMBDA_SEEDLING_AGE`.
    It completely removes such seedlings from the model plot.

    {1}

    '''.format(UniversalTreeActionMixin.__common_par_docs__,
               UniversalTreeActionMixin.__activation_conds__, )

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('POISSON_LAMBDA_SEEDLING_AGE',)
        super(KillOldSeedlingsPoisson, self).__init__(*args, **kwargs)

    def process(self):
        for item in self.object_selector().select_by_stages(['seedling']):
            tochose = self._parameters.get(item.species, self._parameters['none'])
            param = tochose.get('POISSON_LAMBDA_SEEDLING_AGE',
                                self._parameters['none']['POISSON_LAMBDA_SEEDLING_AGE'])
            if item._meta.history['stages']:
                if sum(item._meta.history['stages']['seedling']) > nrandom.poisson(param):
                    self.model.objects.remove(item)


class KillOldSaplings(UniversalTreeActionMixin):
    '''
    Kills saplings that don't change its stage too long

    {0}

    **How it works**

    It looks for each sapling that existing in the plot more than
    `MAX_SAPLING_AGE` timesteps and kill it, i.e. marks as deed trees.

    {1}

    '''.format(UniversalTreeActionMixin.__common_par_docs__,
               UniversalTreeActionMixin.__activation_conds__, )

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('MAX_SAPLING_AGE',)
        super(KillOldSaplings, self).__init__(*args, **kwargs)


    def process(self):
        for item in self.object_selector().select_by_stages(['sapling']):
            tochose = self._parameters.get(item.species,  self._parameters['none'])
            param = tochose.get('MAX_SAPLING_AGE',
                                 self._parameters['none']['MAX_SAPLING_AGE'])            
            if item._meta.history['stages']:
                if sum(item._meta.history['stages']['sapling']) > param:
                    item.stage = 'dead'


class KillOldSaplingsPoisson(UniversalTreeActionMixin):
    '''
    Kills saplings that don't change its stage too long

    {0}

    **How it works**

    It looks for each sapling that existing in the plot more than
    :math:`tau` timesteps, where :math:`tau` comes from
    Poisson distribution with parameter `POISSON_LAMBDA_SAPLING_AGE`.
    It marks saplings as dead trees.

    {1}

    '''.format(UniversalTreeActionMixin.__common_par_docs__,
               UniversalTreeActionMixin.__activation_conds__, )

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('POISSON_LAMBDA_SAPLING_AGE',)
        super(KillOldSaplingsPoisson, self).__init__(*args, **kwargs)

    def process(self):
        for item in self.object_selector().select_by_stages(['sapling']):
            tochose = self._parameters.get(item.species, self._parameters['none'])
            param = tochose.get('POISSON_LAMBDA_SAPLING_AGE',
                                self._parameters['none']['POISSON_LAMBDA_SAPLING_AGE'])
            if item._meta.history['stages']:
                if sum(item._meta.history['stages']['sapling']) > nrandom.poisson(param):
                    item.stage = 'dead'
