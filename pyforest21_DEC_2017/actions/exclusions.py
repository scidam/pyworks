
from pyforest.actions import AbstractAction


class ExcludeOutsideBbox(AbstractAction):
    '''
    Exclude everything from the model that placed
    outside it bounding box

    :param steps: array of step values when the
                   action should be activated; e.g.
                   `steps=[1, 2, 4]` tells
                   to activate this action at 1, 2 and 4
                   timesteps. Default value is [1], in this case
                   the action will be activated only once, at
                   the first timestep.
    :type steps: list or numpy array

    **How it works**

    Objects or seeds outside bounding box
    of the model are removed completely.

    **Conditions of activation**

    Activated at the provided timesteps in `steps` argument. If no
    `steps` parameter provided, it will be activated only once at first
    timestep.
    '''

    def __init__(self, *args, **kwargs):
        super(ExcludeOutsideBbox, self).__init__(*args, **kwargs)
        self.activationsteps = kwargs['steps'] if 'steps' in kwargs else [1]

    def condition(self):
        return self.model.step in self.activationsteps

    def process(self):
        # TODO: This function should be reviewed!!!
        # Which model objects affected by this action? only trees,
        # or only those, that have `x` and `y` attributes as coordinates

        # remove seeds
        for key in self.model.seeds:
            data = self.model.seeds[key]
            todel = (data[0] < self.model.bbox[0][0]) +\
                    (data[0] > self.model.bbox[0][1]) +\
                    (data[1] > self.model.bbox[1][1]) +\
                    (data[1] < self.model.bbox[1][0])
            data = data[:, ~todel]
            self.model.seeds[key] = data

        # TODO: This is probably most inefficient way to remove objects
        # It is required to find new approach! e.g. based on numpy arrays
        # manipulations
        for item in self.model.objects:
            if item.x < self.model.bbox[0][0] or\
               item.x > self.model.bbox[0][1] or\
               item.y < self.model.bbox[1][0] or\
               item.y > self.model.bbox[1][1]:
                self.model.objects.remove(item)
