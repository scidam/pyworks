from pyforest.objects.data import pool
from copy import deepcopy


class AbstractResource(object):
    # Most abstract class of resources
    '''
    Creates abstract resource

    :param model: instance of the `pyforest.core.Model` class
    :type model: pyforest.core.Model
    :returns: Resource object
    :rtype: pyforest.resources.AbstractResource

    **Internal Structure**

    '''

    def __init__(self, model=None, pool=pool,  *args, **kwargs):
        self.model = model
        self._pool = deepcopy(pool)

    def update(self):
        '''
        Resource computation function
        '''
        raise NotImplementedError("Should be implemented in child classes")
