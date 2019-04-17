
from pyforest.actions.growth import (ConstantRadialGrowthAction, SeedlingToSaplingAction,
                                     SaplingToAdultAction)

from pyforest.actions.death import (KillRandomlyAction,
                                    KillOldSeedlings,
                                    KillOldSaplings)

from pyforest.actions.spreads import RadialDecayTreeSeedingAction


from pyforest.core import MemoryBackend, Model, Snapshots
from pyforest.core import Model
from pyforest.objects.trees import Tree



# ------------ Initialization -----------------------------


# ---------------------------------------------------------


# ------------ Create simple model instance ---------------

model = Model()

# ---------------------------------------------------------



# ------------- Filling the model space with trees --------

model.objects += [Tree(1, 1, dbh=30.2, height=20, species='Quercus mongolica', stage='adult')]
model.objects += [Tree(0, 1, dbh=18.0, height=20, species='Quercus mongolica', stage='sapling')]
model.objects += [Tree(1, 0, ddh=3.0, height=20, species='Quercus mongolica', stage='seedling')]