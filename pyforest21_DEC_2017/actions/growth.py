from pyforest.actions import UniversalTreeActionMixin
from pyforest.utils.randomizer import random

import numpy as np


class AnyGrowthAction(UniversalTreeActionMixin):
    # TODO: a piece of docs needed

    def __init__(self, *args, **kwargs):
        self.stages = kwargs['stages'] if 'stages' in kwargs else 'all'
        self._required_parameters = ('DIAM_GROWTH_RATE_ADULT',
                                     'DIAM_GROWTH_RATE_SAPLING',
                                     'DIAM_GROWTH_RATE_SEEDLING',
                                     'MIN_DIAM_GROWTH_RATE_ADULT',
                                     'MAX_DIAM_GROWTH_RATE_ADULT',
                                     'MIN_DIAM_GROWTH_RATE_SAPLING',
                                     'MAX_DIAM_GROWTH_RATE_SAPLING',
                                     'MIN_DIAM_GROWTH_RATE_SEEDLING',
                                     'MAX_DIAM_GROWTH_RATE_SEEDLING',
                                     'HEIGHT_GROWTH_MULT_ADULT',
                                     'HEIGHT_GROWTH_EXP_ADULT',
                                     'HEIGHT_GROWTH_MULT_SAPLING',
                                     'HEIGHT_GROWTH_EXP_SAPLING',
                                     'HEIGHT_GROWTH_EXP_SEEDLING',
                                     'HEIGHT_GROWTH_MULT_SEEDLING',
                                     'MIN_DBH_FOR_ADULT',
                                     'MIN_DDH_FOR_SAPLING',
                                     'MIN_HEIGHT_FOR_SAPLING'
                                     )
        super(AnyGrowthAction, self).__init__(*args, **kwargs)

    def _make_selection(self):
        selection = self.object_selector()
        if self.stages != 'all':
            selection = selection.select_by_stages([self.stages])
        return selection

    __common_par_docs__ = '''
    :param species: tree species to which this action will be applied; default is all;
    :param stages: tree stages to which this action will be applied; default is all (this
                   action affects on 'adult', 'sapling' and 'seedling' trees);
    :param steps: list of steps, when the action will be applied; default is None, that means
                  it will be applied at each timestep.
    :type species: str
    :type stages : str or list
    :type steps : list'''

    __activation_conds__ = '''
    **Conditions of activation**

        By default it is applied at each timestep; if `steps`
    is provided it will be applied at these steps only.
    '''

class ConstantRadialGrowthAction(AnyGrowthAction):
    '''
    Increments tree diameter on a species-specific
    value

    %s

    **How it works**

    It uses `DIAM_GROWTH_RATE_ADULT`, `DIAM_GROWTH_RATE_SAPLING`
    or `DIAM_GROWTH_RATE_SEEDLING` to get appropriate
    increment to diameter. The actions uses the formula:

    :math:`\Delata DBH = GROWTH_RATE*2.0`

    `GROWTH_RATE` is measured in `cm/year`; it is equal either to
    `DIAM_GROWTH_RATE_ADULT` or  `DIAM_GROWTH_RATE_SAPLING`
    or `DIAM_GROWTH_RATE_SEEDLING`, according to stage of
    the current object affected by the action.

    %s

    ''' % (AnyGrowthAction.__common_par_docs__,
           AnyGrowthAction.__activation_conds__)

    def process(self):
        for item in self._make_selection():
            tochose = self._parameters.get(item.species, self._parameters['none'])
            dbh_rate, ddh_rate = 0.0, 0.0
            if item.stage == 'adult':
                dbh_rate = tochose.get('DIAM_GROWTH_RATE_ADULT',
                                       self._parameters['none']['DIAM_GROWTH_RATE_ADULT'])
                item.dbh += 2.0 * dbh_rate
            elif item.stage == 'sapling':
                dbh_rate = tochose.get('DIAM_GROWTH_RATE_SAPLING',
                                       self._parameters['none']['DIAM_GROWTH_RATE_SAPLING'])
                item.dbh += 2.0 * dbh_rate
            elif item.stage == 'seedling':
                ddh_rate = tochose.get('DIAM_GROWTH_RATE_SEEDLING',
                                       self._parameters['none']['DIAM_GROWTH_RATE_SEEDLING'])
                item.ddh += 2.0 * ddh_rate


class RandomRadialGrowthAction(AnyGrowthAction):
    '''
    Increments tree diameter on a species-specific
    random value

    %s

    **How it works**

    It uses:

        * `MIN_DIAM_GROWTH_RATE_ADULT`, `MAX_DIAM_GROWTH_RATE_ADULT` -- for adult trees;
        * `MIN_DIAM_GROWTH_RATE_SAPLING`, `MAX_DIAM_GROWTH_RATE_SAPLING` -- for saplings;
        * `MIN_DIAM_GROWTH_RATE_SEEDLING`, `MAX_DIAM_GROWTH_RATE_SEEDLING` -- for seedlings;

    Starting from these parameters, the action generates a uniformly distributed
    value of `GROWTH_RATE`  at the stage-specific interval and increments a tree
    diameter on :math:`\Delata DBH` as follows:

    :math:`\Delata DBH = GROWTH_RATE*2.0`

    `GROWTH_RATE` units is `cm/year`.

    %s

    ''' % (AnyGrowthAction.__common_par_docs__,
           AnyGrowthAction.__activation_conds__)

    def process(self):
        for item in self._make_selection():
            tochose = self._parameters.get(item.species, self._parameters['none'])
            d_rate = 0.0
            if item.stage == 'adult':
                a = tochose.get('MIN_DIAM_GROWTH_RATE_ADULT',
                                self._parameters['none']['MIN_DIAM_GROWTH_RATE_ADULT'])
                b = tochose.get('MAX_DIAM_GROWTH_RATE_ADULT',
                                self._parameters['none']['MAX_DIAM_GROWTH_RATE_ADULT'])
                d_rate = random.uniform(a, b)
                item.dbh += 2.0 * d_rate
            elif item.stage == 'sapling':
                a = tochose.get('MIN_DIAM_GROWTH_RATE_SAPLING',
                                self._parameters['none']['MIN_DIAM_GROWTH_RATE_SAPLING'])
                b = tochose.get('MAX_DIAM_GROWTH_RATE_SAPLING',
                                self._parameters['none']['MAX_DIAM_GROWTH_RATE_SAPLING'])
                d_rate = random.uniform(a, b)
                item.dbh += 2.0 * d_rate
            elif item.stage == 'seedling':
                a = tochose.get('MIN_DIAM_GROWTH_RATE_SEEDLING',
                                self._parameters['none']['MIN_DIAM_GROWTH_RATE_SEEDLING'])
                b = tochose.get('MAX_DIAM_GROWTH_RATE_SEEDLING',
                                self._parameters['none']['MAX_DIAM_GROWTH_RATE_SEEDLING'])
                d_rate = random.uniform(a, b)
                item.ddh += 2.0 * d_rate


class PowerHeightGrowthActions(AnyGrowthAction):
    '''
    Increments tree height according to power-law

    %s

    **How it works**

    It uses `HEIGHT_GROWTH_MULT_ADULT`, `HEIGHT_GROWTH_EXP_ADULT`,
    'HEIGHT_GROWTH_MULT_SAPLING', `HEIGHT_GROWTH_EXP_SAPLING`,
    `HEIGHT_GROWTH_MULT_SEEDLING`, `HEIGHT_GROWTH_EXP_SEEDLING`
    to compute increment for tree height parameter as follows:

    :math:`\Delata Height = HEIGHT_GROWTH_MULT_ADULT\cdot H^HEIGHT_GROWTH_EXP_ADULT`

    where :math:`H` is current height of the tree.

    %s

    ''' % (AnyGrowthAction.__common_par_docs__,
           AnyGrowthAction.__activation_conds__)

    def process(self):
        for item in self._make_selection():
            tochose = self._parameters.get(item.species, self._parameters['none'])
            mult_coef = 0.0
            if item.stage == 'adult':
                mult_coef = tochose.get('HEIGHT_GROWTH_MULT_ADULT',
                                        self._parameters['none']['HEIGHT_GROWTH_MULT_ADULT'])
                exp_coef = tochose.get('HEIGHT_GROWTH_EXP_ADULT',
                                        self._parameters['none']['HEIGHT_GROWTH_EXP_ADULT'])
            elif item.stage == 'sapling':
                mult_coef = tochose.get('HEIGHT_GROWTH_MULT_SAPLING',
                                        self._parameters['none']['HEIGHT_GROWTH_MULT_SAPLING'])
                exp_coef = tochose.get('HEIGHT_GROWTH_EXP_SAPLING',
                                        self._parameters['none']['HEIGHT_GROWTH_EXP_SAPLING'])
            elif item.stage == 'seedling':
                mult_coef = tochose.get('HEIGHT_GROWTH_MULT_SEEDLING',
                                        self._parameters['none']['HEIGHT_GROWTH_MULT_SEEDLING'])
                exp_coef = tochose.get('HEIGHT_GROWTH_EXP_SEEDLING',
                                        self._parameters['none']['HEIGHT_GROWTH_EXP_SEEDLING'])
            if mult_coef:
                item.height += mult_coef * np.power(item.height, exp_coef)


class SaplingToAdultAction(AnyGrowthAction):
    '''
    Transforms saplings to adult trees

    **How it works**

    If current diameter at breast height is greater than
    `MIN_DBH_FOR_ADULT` the stage of a tree is assigned
    to `adult`.

    **Conditions of activation**

    Applied at each timestep. This is internal action and included into
    the model by default. You don't need to include it.
    '''

    def process(self):
        for item in self._make_selection():
            tochose = self._parameters.get(item.species, self._parameters['none'])
            mindbh = tochose.get('MIN_DBH_FOR_ADULT',
                                 self._parameters['none']['MIN_DBH_FOR_ADULT'])
            if item.dbh >= mindbh and item.stage == 'sapling':
                item.stage = 'adult'


class SeedlingToSaplingAction(AnyGrowthAction):
    '''
    Transforms seedlings to saplings

    **How it works**

    If current diameter at decimal (10 cm above the ground) height
    of a tree is greater than
    `MIN_DDH_FOR_SAPLING` the stage of the tree is assigned
    to `sapling`. If current diameter at 10cm-height above the ground
    is lower `MIN_DBH_FOR_SAPLING`, but height is greater than
    `MIN_HEIGHT_FOR_SAPLING`, the tree stage is assigned to `sapling`.

    **Conditions of activation**

    Applied at each timestep. This is internal action and included into
    the model by default. You don't need to include it.
    '''

    def process(self):
        for item in self._make_selection():
            tochose = self._parameters.get(item.species, self._parameters['none'])
            minddh = tochose.get('MIN_DDH_FOR_SAPLING',
                                 self._parameters['none']['MIN_DDH_FOR_SAPLING'])
            minheight = tochose.get('MIN_HEIGHT_FOR_SAPLING',
                                    self._parameters['none']['MIN_HEIGHT_FOR_SAPLING'])            
            if (item.ddh >= minddh or item.height >= minheight)\
               and item.stage == 'seedling':
                item.stage = 'sapling'
# TODO: dbh should be initialized here !!!, but we are still working without this feature
#                 item.dbh = item.ddh # simplest case, should be upgraded 

