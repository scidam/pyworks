import itertools
import hashlib
import numpy as np


class MetaProperty(object):
    '''
    Used to store auxilary object properties, e.g.
    history of object parameters
    '''

    def __init__(self):
        self.history = {'stages': {}, 'crown_hashes': []}

    def get_age_on_stage(self, stage):
        '''
        Returns the number of timesteps the object had the requested stage
        '''
        return sum(self.history['stages'][stage])\
            if stage in self.history['stages'] else 0


class AbstractObject(object):

    newid = itertools.count()

    def __init__(self, x, y, z=None,
                 components={}, **kwargs):
        self.x = x
        self.y = y
        self.z = z  # 3D models, but currently only 2D
        self.crown = {}  # a dictionary
        self.id = next(AbstractObject.newid)
        self.type = kwargs['type'] if 'type' in kwargs else 'tree'
        self._meta = MetaProperty()


class WoodyPlantMixin(AbstractObject):
    '''Common methods for shrub and tree objects'''

    def add_crown(self, crown, relative=True):
        crown = np.array(crown)
        if len(crown.shape) != 2:
            pass
            # TODO: Raise exception here, tree crown is invalid
        elif crown.shape[1] != 3:
            pass
            # TODO: Raise exception here, tree crown is invalid
        elif relative:
            crown[:, 0] += self.x
            crown[:, 1] += self.y
        self.crown = crown

    def replace_crown(self, newcrown):
        self.crown = newcrown

    @property
    def crown_hash(self):
        '''Get sha1 hash of object crown'''

        if isinstance(self.crown, np.ndarray):
            tohash = self.crown.view(np.uint8)
        else:
            try:
                self.crown = np.array(self.crown)
                tohash = self.crown.view(np.uint8)
            except:
                pass
        return hashlib.sha1(tohash).hexdigest()
