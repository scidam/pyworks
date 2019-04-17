'''
Data file for tree species defined in `__species__` variable.

It is part of `pyforest` -- a framework for trees growth modeling.

This is file of fallback parameters. It is used when no species was defined.
'''

# This special constant used by data autodiscovery function
__species__ = 'none'
__checked__ = False
__checkedby__ = 'Noname'



# in cm
SEEDLINGS_CREATION_MAX_DDH = 0.7

# in cm
SEEDLINGS_CREATION_MIN_DDH = 0.05

# in meters
SEEDLINGS_CREATION_MAX_HEIGHT = 0.5

# in meters
SEEDLINGS_CREATION_MIN_HEIGHT = 0.01


# ----------------- Allometric relations between height and diameter ----------
# It is assumed that height = a + b*(ddh or dbh)

LIN_ALLOM_SEEDLING_DDH_HEIGHT_A = 0.1
LIN_ALLOM_SEEDLING_DDH_HEIGHT_B = 2

LIN_ALLOM_SAPLING_DBH_HEIGHT_A = 0.4
LIN_ALLOM_SAPLING_DBH_HEIGHT_B = 1.2

LIN_ALLOM_ADULT_DBH_HEIGHT_A = 3.4
LIN_ALLOM_ADULT_DBH_HEIGHT_B = 5.6

# -----------------------------------------------------------------------------

# -------------------- Seed parameters ----------------------------------------
MAX_TIME_SEED_EXIST = 4  # Max time seed exists in the ground

# -----------------------------------------------------------------------------


# ------------------- Linear growth parameters --------------------------------
# Used by ConstantRadialGrowthAction
DIAM_GROWTH_RATE_ADULT = 0.4
DIAM_GROWTH_RATE_SAPLING = 0.8
DIAM_GROWTH_RATE_SEEDLING = 0.3  # affects on ddh only!
# -----------------------------------------------------------------------------


# ------------------- Power Height growth -------------------------------------
# PowerHeightGrowthActions
HEIGHT_GROWTH_MULT_ADULT = 0.01
HEIGHT_GROWTH_EXP_ADULT = 0.01
HEIGHT_GROWTH_MULT_SEEDLING = 0.01
HEIGHT_GROWTH_EXP_SEEDLING = 0.01
HEIGHT_GROWTH_MULT_SAPLING = 0.01
HEIGHT_GROWTH_EXP_SAPLING = 0.01
# -----------------------------------------------------------------------------


# ----------------- Stage change action ---------------------------------------
# SaplingToAdultAction
MIN_DBH_FOR_ADULT = 20

# SeedlingToSaplingAction
MIN_DDH_FOR_SAPLING = 5
MIN_HEIGHT_FOR_SAPLING = 3
# -----------------------------------------------------------------------------


# ----------------- Random Killer action --------------------------------------
# KillRandomlyAction
DEATH_PROB_TREE_SAPLING = 0.1
# High value for testing purposes!!!
DEATH_PROB_TREE_ADULT = 0.9
DEATH_PROB_TREE_SEEDLING = 0.05
DEATH_PROB_SHRUB = 0.01
# -----------------------------------------------------------------------------


# ---------------- Debris Remover action --------------------------------------
# TreeDebrisRemoverAction
TREE_REMOVE_DEBRIS_AGE = 10
SHRUB_REMOVE_DEBRIS_AGE = 10
# -----------------------------------------------------------------------------


# ---------------- Radial spreading action ------------------------------------
# RadialDecayTreeSeedingAction

MAX_INTENSITY_SEEDING_R_DECAY = 300.0
INTENSITY_SLOPE_SEEDING_R_DECAY = 2.0
INTENSITY_SHIFT_SEEDING_R_DECAY = 3.0
H_MAX_DIST_SEEDING_R_DECAY = 4.0
K_HEIGHT_IMPACT_SEEDING_R_DECAY = 1.0
H0_HEIGHT_DIST_SEEDING_R_DECAY = 2.0
# -----------------------------------------------------------------------------


# ---------------- Kill when growth too slow action ---------------------------
# KillWhenTooLowGrowthSpeedAction
MEAN_GROWTH_SPEED_NSTEPS_SEEDLING = 4
MEAN_GROWTH_SPEED_NSTEPS_SAPLING = 5
MEAN_GROWTH_SPEED_NSTEPS_ADULT = 7
MIN_DDH_SPEED_FOR_DEATH_SEEDLING = 0.1
MIN_DBH_SPEED_FOR_DEATH_SAPLING = 0.2
MIN_DBH_SPEED_FOR_DEATH_ADULT = 0.2
# -----------------------------------------------------------------------------

# ----------------- Remove some seed randomly ---------------------------------
#HarvestSeedsRandomlyAction
SEED_HARVEST_INDEX = 0.5 # Should be in [0, 1]
# -----------------------------------------------------------------------------


# ---------------- Kill tree when it has lots of neighbors  -------------------
# GompertzKillerAction
GOMPERTZ_KILLER_MIN_HEIGHT_TREE = 3
GOMPERTZ_KILLER_NEIGH_RADIUS = 0.5
GOMPERTZ_KILLER_BETA_SEEDLING = 0.6
GOMPERTZ_KILLER_GAMMA_SEEDLING = 0.5
GOMPERTZ_KILLER_DELTA_SEEDLING = 3
GOMPERTZ_KILLER_BETA_SAPLING = 0.4
GOMPERTZ_KILLER_GAMMA_SAPLING = 0.5
GOMPERTZ_KILLER_DELTA_SAPLING = 4
GOMPERTZ_KILLER_BETA_ADULT = 0.2
GOMPERTZ_KILLER_GAMMA_ADULT = 0.1
GOMPERTZ_KILLER_DELTA_ADULT = 5
# -----------------------------------------------------------------------------


# ----------------- Radial growth at random rate ------------------------------
# RandomRadialGrowthAction
MIN_DIAM_GROWTH_RATE_ADULT = 0.01
MAX_DIAM_GROWTH_RATE_ADULT = 0.5
MIN_DIAM_GROWTH_RATE_SAPLING = 0.2
MAX_DIAM_GROWTH_RATE_SAPLING = 0.9
MIN_DIAM_GROWTH_RATE_SEEDLING = 0.2
MAX_DIAM_GROWTH_RATE_SEEDLING = 0.5
# -----------------------------------------------------------------------------


# --------------- Kill saplings that don't change its stage too long ----------
# KillOldSapling
MAX_SAPLING_AGE = 10
# -----------------------------------------------------------------------------

# --------------- Kill seedlings that don't change its stage too long ----------
# KillOldSeedling
MAX_SEEDLING_AGE = 10
# -----------------------------------------------------------------------------

# --------------- Kill saplings that don't change its stage too long ----------

# KillOldSaplingPoisson
POISSON_LAMBDA_SAPLING_AGE = 10

# -----------------------------------------------------------------------------

# --------------- Kill seedling that don't change its stage too long ----------

# KillOldSeedlingPoisson
POISSON_LAMBDA_SEEDLING_AGE = 10

# -----------------------------------------------------------------------------



# ---------------- Resource: Light: -------------------------------------------
# at least SolarDirectIrradiance resource calculation
MAX_CROWN_RADIUS = 15 # given in meters
MIN_LIGHT_IRRADIANCE = 0.1  # Min allowed light intensity under canopy


# ---------------- Resource: Light: SolarDirectIrradiance----------------------
# SolarDirectIrradiance
LIGHT_INTENSITY_LINEAR_SLOPE = 0.001
# -----------------------------------------------------------------------------


# ---------------- Resource: Light: SolarDirectMonsiSaekiIrradiance------------
#SolarDirectMonsiSaekiIrradiance
LIGHT_ABSORPTION_MONSI_SAEKI = 0.2
LEAF_AREA_INDEX = 0.7
# -----------------------------------------------------------------------------


# ------------- Resource: Light: SolarDirectMonsiSaekiAdoptedIrradiance--------
#SolarDirectMonsiSaekiAdoptedIrradiance
CANOPY_LEN_MAX_MONSI_SAEKI_ADOPTED = 20
LIGHT_ABSORPTION_MAX_MONSI_SAEKI_ADOPTED = 1.5
# -----------------------------------------------------------------------------

