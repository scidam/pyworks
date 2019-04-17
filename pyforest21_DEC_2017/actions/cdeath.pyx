from pyforest.actions import EachStepRunnerMixin
from pyforest.utils.randomizer import random


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
        self._required_parameters = ['DEATH_PROB_TREE_SAPLING',
                                 'DEATH_PROB_TREE_ADULT',
                                 'DEATH_PROB_TREE_SEEDLING',
                                 'DEATH_PROB_SHRUB']        
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
