'''
Data file for tree species defined in `__species__` variable.

It is part of `pyforest` -- a framework for tree growth modeling.

'''

# This special constant used by data autodiscovery function
__species__ = 'betula mandshurica'
__checked__ = False
__checkedby__ = 'Noname'

# in cm
SEEDLINGS_CREATION_MAX_DDH = 0.5

# in cm
SEEDLINGS_CREATION_MIN_DDH = 0.1

# in meters
SEEDLINGS_CREATION_MAX_HEIGHT = 0.3

# in meters
SEEDLINGS_CREATION_MIN_HEIGHT = 0.05


# in meters
MAX_HEIGHT = 50


# ----------------- Allometric relations between height and diameter ----------
# It is assumed that height = a + b*(ddh or dbh)

LIN_ALLOM_SEEDLING_DDH_HEIGHT_A = 0.1
LIN_ALLOM_SEEDLING_DDH_HEIGHT_B = 2

LIN_ALLOM_SAPLING_DBH_HEIGHT_A = 0.4
LIN_ALLOM_SAPLING_DBH_HEIGHT_B = 1.2

LIN_ALLOM_ADULT_DBH_HEIGHT_A = 3.4
LIN_ALLOM_ADULT_DBH_HEIGHT_B = 5.6

# -----------------------------------------------------------------------------
