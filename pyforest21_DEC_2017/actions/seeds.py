from pyforest.actions import AbstractAction
from pyforest.actions import EachStepRunnerMixin
from pyforest.objects.trees import Tree
from pyforest.utils.randomizer import irand, random, nrandom

import numpy as np

# TODO: Bad action name, need to be fixed!
class ConstantProbabilityAction(EachStepRunnerMixin):
    '''
    Seed germination action

    This action is applied to all seeds in the model at
    each timestep. Action transforms some seeds into seedlings
    or excludes them from the model. Some seeds remain
    unchanged.

    :param mortality: probability of seed death (:math:`p_d`);
    :param grow: probability of seed 
                  germination at current timestep (:math:`p_g`);
    :type mortality: float
    :type grow: float

    **How it works**

    1. At first, the number of seeds to be excluded
       from the model is derived. Seeds are excluded by two reasons:
       germination and death. The number of seeds to be excluded
       is determined as a random number sampled from binomial
       distribution with parameters :math:`p_d + p_g` as probability
       and :math:`n` as the current number of seeds.
    2. Given the number of seeds to be excluded (denote it :math:`n_m`),
       the number of seeds
       for death (denote it :math:`n_d`) is defined as a random value
       sampled from binomial distribution with parameters 
       :math:`\\frac{{p_d}}{{p_d + p_g}}` and :math:`n_m`.  
       Then the number of seeds for germination is defined as :math:`n_m - n_d`.
    3. Given the numbers :math:`n_d` and :math:`n_m - n_d`, seeds are excluded
       randomly from the model. :math:`n_d` seeds just excluded, 
       without any further activity. :math:`n_m-n_d` seeds are excluded, but
       :math:`n_m-n_d` of seedling objects is created at the same time.
    4. The following parameters assigned to the seedlings created:
        * :math:`dbh=0` - diameter at breast height
        * :math:`height` - random value from uniform distribution defined on
                           the species-specific interval (`SEEDLINGS_CREATION_MIN_HEIGHT`
                           `SEEDLINGS_CREATION_MAX_HEIGHT`)
        * :math:`ddh` - assigned in the same manner as pervious,
                        but (`SEEDLINGS_CREATION_MIN_DDH`,
                        `SEEDLINGS_CREATION_MAX_DDH`) used instead.


    {0}


    .. note::

        It is assumed that constraint :math:`p_d + p_g\leq 1`
        takes place. If :math:`p_d + p_g < 1`, then
        :math:`1 - p_d + p_g` is probability of a seed
        state will remain unchanged.

    '''.format(EachStepRunnerMixin.__activation_conds__)

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('SEEDLINGS_CREATION_MAX_DDH',
                                     'SEEDLINGS_CREATION_MIN_DDH',
                                     'SEEDLINGS_CREATION_MAX_HEIGHT',
                                     'SEEDLINGS_CREATION_MIN_HEIGHT')
        super(ConstantProbabilityAction, self).__init__(*args, **kwargs)
        self.mortality = kwargs['mortality']
        self.germination = kwargs['germination']

    def process(self):
        def _get_indicies(array):
            if not(0 < self.mortality + self.germination <= 1):
                # TODO: raise exception here
                raise NotImplementedError
            n = np.shape(array)[1]
            if n == 0:
                return (0, 0)
            inds = set(np.arange(n))
            nall = nrandom.binomial(n, self.mortality + self.germination)
            n_death = nrandom.binomial(nall, self.mortality/(self.mortality +
                                                             self.germination)
                                       )
            n_grow = nall - n_death
            to_death = random.sample(inds, n_death)
            remains = inds - set(to_death)
            to_grow = random.sample(remains, n_grow)
            return (to_death, to_grow)

        def _create_seedlings(gi, species, cdata, tochose):
            for ind in range(len(gi)):
                ddhi_max = tochose.get('SEEDLINGS_CREATION_MAX_DDH',
                                   self._parameters['none']['SEEDLINGS_CREATION_MAX_DDH'])
                ddhi_min = tochose.get('SEEDLINGS_CREATION_MIN_DDH',
                                   self._parameters['none']['SEEDLINGS_CREATION_MIN_DDH'])
                heighti_max = tochose.get('SEEDLINGS_CREATION_MAX_HEIGHT',
                                      self._parameters['none']['SEEDLINGS_CREATION_MAX_HEIGHT'])
                heighti_min = tochose.get('SEEDLINGS_CREATION_MIN_HEIGHT',
                                      self._parameters['none']['SEEDLINGS_CREATION_MIN_HEIGHT'])                
                tree = Tree(cdata[0, ind], cdata[1, ind],
                            species=species,
                            dbh=0.0,
                            height=irand(heighti_min, heighti_max),
                            ddh=irand(ddhi_min, ddhi_max))
                tree.stage = 'seedling'
                self.model.objects.append(tree)

        for sp in self.model.seeds.keys():
            tochose = self._parameters.get(sp, self._parameters['none'])
            cdata = self.model.seeds[sp]
            di, gi = _get_indicies(cdata)
            if gi:
                _create_seedlings(gi, sp, cdata, tochose)
            if di or gi:
                cdata = np.delete(cdata, di + gi, axis=1)
            self.model.seeds[sp] = cdata


class RemoveOldSeedsAction(EachStepRunnerMixin):
    '''
    Removes old seeds from the model

    **How it works**

    It searches for seeds that lie in the ground more than
    predefined species-specific value and excludes
    them from the model.

    {0}

    '''.format(EachStepRunnerMixin.__activation_conds__)

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('MAX_TIME_SEED_EXIST',)
        super(RemoveOldSeedsAction, self).__init__(*args, **kwargs)

    def process(self):
        for sp in self.model.seeds:
            tochose = self._parameters.get(sp, self._parameters['none'])
            data = self.model.seeds[sp]
            ctime = tochose.get('MAX_TIME_SEED_EXIST',
                                self._parameters['none']['MAX_TIME_SEED_EXIST'])
            data = data[:, data[2, :] > self.model.step - ctime]
            self.model.seeds[sp] = data


class HarvestSeedsRandomlyAction(EachStepRunnerMixin):
    '''Randomly removes some amount of seeds from the model plot

    **How it works**

    Starting from `SEED_HARVEST_INDEX` value (that must belong to [0, 1]),
    it determines the number of seeds to be removed as a value
    from poisson distribution with :math:`lambda = SEED_HARVEST_INDEX * N`,
    where :math:`N` -- the number of seeds of the current species;
    When the number of seeds to be removed is computed, seeds removing
    is made by random selection.

    {0}
    '''.format(EachStepRunnerMixin.__activation_conds__)

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('SEED_HARVEST_INDEX',)
        super(HarvestSeedsRandomlyAction, self).__init__(*args, **kwargs)

    def process(self):
        for sp in self.model.seeds:
            tochose = self._parameters.get(sp, self._parameters['none'])
            data = self.model.seeds[sp]
            ind = tochose.get('SEED_HARVEST_INDEX',
                              self._parameters['none']['SEED_HARVEST_INDEX'])
            num = len(data[0, :])
            nnr = nrandom.poisson(ind * float(num))
            if nnr > num:
                data = np.array([[], [], []])
            else:
                leave_indecies = nrandom.choice(num, num - nnr, replace=False)
                data = data[:, leave_indecies]
            self.model.seeds[sp] = data
