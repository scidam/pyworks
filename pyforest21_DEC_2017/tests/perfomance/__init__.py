
from pyforest.core import Model
from pyforest.events.random import CreateRandomSimpleTrees
from pyforest.objects.data import pool

pool.autodiscover('./objects/data')

# ------------ Test Model initialization -----------------------
model = Model(bbox=[(0, 10), (0, 20)])
seedlings = CreateRandomSimpleTrees(treenum=1000,
                                    species=list(map(str, range(10))),
                                    bbox=[(0, 10), (0, 10)],
                                    heights=[0, 15],
                                    dbhs=[10, 100],
                                    stage='seedling'
                                    )
saplings = CreateRandomSimpleTrees(treenum=1000,
                                   species=list(map(str, range(10))),
                                   bbox=[(0, 10), (0, 10)],
                                   heights=[0, 15],
                                   dbhs=[10, 100],
                                   stage='sapling'
                                   )

adult = CreateRandomSimpleTrees(treenum=1000,
                                species=list(map(str, range(10))),
                                bbox=[(0, 10), (0, 10)],
                                heights=[0, 15],
                                dbhs=[10, 100],
                                stage='adult'
                                )

model.insert_event(seedlings)
model.insert_event(saplings)
model.insert_event(adult)

for ev in model.events:
    ev.activate()
# --------------------------------------------------
