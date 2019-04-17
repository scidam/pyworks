
from pyforest.core import Model
from pyforest.events.random import CreateRandomSimpleTrees

from pyforest.visual.D3 import pv


m = Model(bbox=[(0, 20), (0, 40)])

rnd_trees = CreateRandomSimpleTrees(treenum=50,
                                            species=map(lambda x: str(x),
                                                        range(10)),
                                            bbox=[(0, 20), (0, 40)],
                                            heights=[3, 10],
                                            dbhs=[10, 30],
                                            stage='sapling'
                                            )


m.insert_event(rnd_trees)

m.events[0].activate()


d2 = pv.ParaviewSimple3DScene(model=m)
d2.plot_model()
