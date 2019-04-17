from copy import deepcopy

from pyforest.objects.data import pool, ObjectDataStorage


def never_activated(obj):
    '''
    Check if an action or event was activated or not
    '''
    history = getattr(obj, 'history', False)
    if not history:
        return True
    else:
        return not any(map(lambda x: x[1], history))


class AbstractAction(object):

    def __init__(self, model=None, pool=pool, override_pars=None,
                 force_restore_pars=True, **kwargs):
        self.model = model
        self.history = []
        self._pool = pool
        self._mempool = None
        self._force_restore_pars = force_restore_pars
        self._override_pars = override_pars
        self._parameters = {}
        self._required_parameters = self._required_parameters if hasattr(self, '_required_parameters') else tuple()

    def __init_parameters(self):
        if self._required_parameters:
            self._parameters = self._pool.get_required_parameters(self._required_parameters)

    @property
    def condition(self):
        '''If True action could be activated'''
        raise NotImplementedError("Should be defined in child classes")

    def _override_parameters(self):
        species = self._override_pars[0]
        newpars = self._override_pars[1]
        self._mempool = deepcopy(self._pool)
        self._pool = deepcopy(self._mempool)
        for sp, pars in zip(species, newpars):
            for par in pars:
                self._pool.set_parameter(sp, par, pars[par], create=True)
        self.__init_parameters()

    def _restore_parameters(self):
        if isinstance(self._mempool, ObjectDataStorage):
            self._pool = self._mempool
        self.__init_parameters()

    def activate(self):
        '''
        Could change everything in the model
        It is invoked by `run` method of the current model instance
        '''
        if self._override_pars:
            self._override_parameters()

        if self.condition:
            if not self._parameters:
                self.__init_parameters()
            self.process()
            self.history.append((self.model.step, True))
        else:
            self.history.append((self.model.step, False))
        if self._force_restore_pars:
            self._restore_parameters()

    def get_parameter(self, species, parname):
        '''Get action parameter'''
        tochose = self._parameters.get(species, self._parameters['none'])
        return tochose.get(parname, self._parameters['none'][parname])

    def process(self):
        raise NotImplementedError("Should be implemented in child classes")


class EachStepRunnerMixin(AbstractAction):
    '''Actions inherited from it will be executed each timestep
    '''

    __activation_conds__ = '''
    **Conditions of activation**

    Each timestep
    '''

    @property
    def condition(self):
        return True


class OnlyOnceMixin(AbstractAction):
    '''
    Child actions or events will be ran only once per modelling process
    '''

    @property
    def condition(self):
        return never_activated(self)


class UniversalActionMixin(AbstractAction):
    ''' Describe common actions behavior'''

    __activation_conds__ = ''' 
    **Conditions of activation**

        Each timestep by default or in a give timesteps if `steps` was passed.
    '''

    __common_par_docs__ = '''
    :param steps: a list of timesteps when the action should be activated; default is None, that means the action will be activated 
                 at each timestep;
    :param species: a list of species, or one species only, that will be affected by the action; default is 'all';
    :type steps: list or str
    :type species: list or str

    # TODO: Probably what raises will occur?!
    '''

    def __init__(self, steps=None, species='all', **kwargs):
        super(UniversalActionMixin, self).__init__(**kwargs)
        self.steps = steps
        self.species = species

    @property
    def condition(self):
        if self.steps is None:
            return True
        elif self.model.step in self.steps:
            return True
        else:
            return False

    def object_selector(self):
        if isinstance(self.species, str):
            if self.species == 'all':
                return self.model.objects
            else:
                return self.model.objects.select_by_species([self.species])
        elif isinstance(self.species, list):
            return self.model.objects.select_by_species(self.species)


class UniversalTreeActionMixin(UniversalActionMixin):
    ''' Describe common actions behavior'''

    def object_selector(self):
        return super(UniversalTreeActionMixin,
                     self).object_selector().select_by_type('tree')


class UniversalShrubActionMixin(UniversalActionMixin):
    ''' Describe common actions behavior'''

    def object_selector(self):
        return super(UniversalTreeActionMixin,
                     self).object_selector().select_by_type('shrub')
