
from pyforest.actions.spreads import UniformDisperseTreeAction
from pyforest.core import Model
from pyforest.events.random import CreateRandomSimpleTrees

from pyforest.visual.D2 import Scene2D


m = Model(bbox=[(0, 10), (0, 40)], data={'orientation': {'xaxis': 45}})

rnd_trees = CreateRandomSimpleTrees(treenum=100,
                                            species=list(map(lambda x: str(x),
                                                        range(10))),
                                            bbox=[(0, 10), (0, 40)],
                                            heights=[0, 15],
                                            dbhs=[10, 100]
                                            )
myseeding = UniformDisperseTreeAction(intensity=50,
                                      distribution='uniform',
                                      species='oak tree'
                                      )

m.insert_action(myseeding)
m.insert_event(rnd_trees)

m.events[0].activate()

m.actions[0].activate()
m.step+=1
m.actions[0].activate()



d2 = Scene2D()
d2.plot_model(m)
d2.show()
