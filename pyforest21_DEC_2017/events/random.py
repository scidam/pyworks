from pyforest.actions import OnlyOnceMixin
from pyforest.events import AbstractEvent
from pyforest.objects.trees import Tree
from pyforest.utils.randomizer import random


class CreateRandomSimpleTrees(OnlyOnceMixin, AbstractEvent):
    '''Inserts uniformly distributed trees to the model plot

    # TODO: bbox not needed? it could be accessed via model attr?

    :param treenum: the number of trees to be inserted
    :param species: a list of species to be randomly assigned on
                    the trees created;
    :param bbox: a bounding box, where tree will be distributed;
                It is assumed that bbox is [(x_min, x_max),(y_min, y_max)];
    :param heights:  an interval of allowed heights; assigned heights to
                    trees generated will be chosen from it as a
                    a sample from uniform distribution;
    :param dbhs: an interval of allowed widths at breath height (it is
                 used the same way as heights done);
    :param stage: assing stage to the created trees; Default is `seedling`.
    :type treenum: int
    :type species: list
    :type bbox: list of tuples
    :type heights: list
    :type dbhs: list
    :type stage: str

    **How it works**

    Should be documented

    **Conditions of activation**

    Only once per modeling process
    '''

    def __init__(self, *args, **kwargs):

        super(CreateRandomSimpleTrees, self).__init__(*args, **kwargs)
        self._treenum = kwargs['treenum']
        self._treesp = kwargs['species']
        self._bbox = kwargs['bbox'] if 'bbox' in kwargs else self.model.bbox
        self._heights = kwargs['heights']
        self._dbhs = kwargs['dbhs']
        # TODO: Probably more convenient to have stage as a list input
        self._stage = kwargs['stage'] if 'stage' in kwargs else 'seedling'

    def process(self):
        for ind in range(self._treenum):
            tree = Tree(random.uniform(*self._bbox[0]),
                        random.uniform(*self._bbox[1]),
                        species=random.choice(self._treesp),
                        height=random.uniform(*self._heights),
                        dbh=random.uniform(*self._dbhs),
                        stage=self._stage)
            self.model.objects.append(tree)
