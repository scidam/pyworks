import collections
from copy import deepcopy

from pyforest.core.base import (AbstractModel, AbstractSnapshots,
                                AbstractBackend)


class Model(AbstractModel):
    '''Most base class for models creation.

    Any model created via `pyforest` framework is stored in the
    instance of this class.

    **Constructor parameters**

    :param bbox: model plot size, default is a unit square = [(0 ,1), (0, 1)]
    :param events: array of events to be applied to the model; Empty by default.
    :param resources: array of resources used by actions during the model running; Empty by default;
    :param actions: array of actions to be applied to objects; Empty by default;
    :param data: Python dictionary for passing extra parameters to the model; default = {};

    **Public attributes**

    :param objects: a list-like object for storing objects those behaviour is modelled;
    :param step:  an integer value, it is descrete counter of the model time;
    :param seeds: Python dictionary; stores species specific array of seed positions during model run;
   '''

class MemoryBackend(AbstractBackend, list):
    '''
    Backend for saving snapshots in memory
    '''

    def __init__(self, *args, **kwargs):
        super(MemoryBackend, self).__init__(*args, **kwargs)

    def search_by_steps(self, steps):
        '''
        Searches for model states by passed timesteps

        :param steps: a list of timesteps of requested model states;
                      passing `[-1]` causes returning last state
        :type steps: list
        :return: a list of model states or empty list
        :rtype: list
        '''

        if steps == [-1]:
            return [self[-1][1]] if self else None # TODO Should raise not found here
        return list(map(lambda y: y[1], filter(lambda x: x[0] in steps, self)))

    def search_by_condition(self, condition):
        '''
        Searches for model states by passed condition

        :param condition: search condition -- a python callable; It is assumed
                          that input parameter of the condition is a model
                          instance.
                          Condition should return boolean value, i.e. `True` --
                          means a model to be included into search results and
                          `False` a model a model will be excluded.

        .. note::
                As mentioned above, it is assumed that `condition` is of the
                form:

                .. code-block:: python

                    def condition(model):
                        """Example of a simple condition"""
                        if len(model.objects) > 100:
                            return True
                        else:
                            return False

                This condition means that model snapshots with the number of
                objects greater 100 will be selected. But if you need
                to pass an extra argument to such condition statement, e.g.
                100, you need to use :func:`partial` from :module:`functools`.

                If you need to pass an extra arguments to your condition,
                :func:`functools.partial` may be helpful:

                .. code-block:: python

                    from functools import partial

                    def condition_with_parameters(par1, par2, model):
                        """Returns snapshots with the number of objects
                        belonging to range (par1, par2)."""
                        if par1 < len(model.objects) < par2:
                            return True
                        else:
                            return False

                    new_cond = partial(condition_with_parameters, 50, 100)

                 Now, created condition :func:`new_cond`
                 could be passed as a search criteria.
        '''
        return list(map(lambda y: y[1], filter(lambda x: condition(x[1]), self)))


class FileStorageBackend(AbstractBackend, list):
    # TODO: Not implemented yet

    def __init__(self, *args, **kwargs):
        super(FileStorageBackend, self).__init__(*args, **kwargs)


class RedisBackend(AbstractBackend, list):
    # TODO: Not implemented yet

    def __init__(self, *args, **kwargs):
        super(RedisBackend, self).__init__(*args, **kwargs)


class Snapshots(AbstractSnapshots):
    '''
    Model snapshot handler.

    It is used for recording model states when modeling process is run.

    :param backend: either MemoryBackend instance (by default) or FileStorageBackend instance;
    :param model: a model instance to be tracked;
    '''

    def __init__(self, *args, **kwargs):
        super(Snapshots, self).__init__(*args, **kwargs)
        self.backend = kwargs['backend'] if 'backend' in\
                                            kwargs else MemoryBackend()
        self._model = kwargs['model'] if 'model' in kwargs else None

    def attach_model(self, model):
        if self._model:
            # TODO: Raise exception (create new snapshot instead)
            raise NotImplementedError
        else:
            self._model = model

    def record(self, until=1):
        '''
        Record model states when model is run.

        :param until: record the model states until the step specified by the `until`; default  is 1.
        :type until: int
        '''

        self.backend.append((0, deepcopy(self._model)))
        for model in self._model._run_generator(until=until):
            self.backend.append((model.step, deepcopy(model)))

    def get_snapshot(self, timesteps):
        '''
        Returns a list of snapshots at specified timesteps.
        '''

        # This function shoudl handle both scalars and list of scalars
        # It should handle negative indicies too.
        if isinstance(timesteps, int):
            res = self.backend.search_by_steps([timesteps])
            if res:
                return res[0]
            else:
                # TODO: should raise Not found exception?
                # or be silent?!...
                raise NotImplementedError
        elif isinstance(timesteps, collections.Iterable):
            res = self.backend.search_by_steps([timesteps])
        else:
            # TODO: Raise special exception here!
            raise NotImplementedError
        if res:
                return res[0]
        else:
            # TODO: should raise Not found exception?
            # or be silent?!...
            raise NotImplementedError

    @property
    def initstate(self):
        return self.get_snapshot(0)

    @property
    def laststate(self):
        return self.get_snapshot(-1)
