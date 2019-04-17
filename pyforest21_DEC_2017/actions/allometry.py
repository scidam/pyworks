'''
Allometry constraints actions

'''
from pyforest.actions import EachStepRunnerMixin

# TODO: Illegal action docs! Review needed!
class TreeDiamHeightLinearAllometry(EachStepRunnerMixin):
    '''
    Seed germination action

    This action is applied to all seeds in the model at
    each timestep. Action transforms some seeds into seedlings
    or excludes them from the model. Some seed states remain
    unchanged.

    :param parname: parameter name to be adjusted according
                    to allometric equations
    :param species: species to which this action will be applied
    :type parname: str
    :type species: str

    **How it works**

    Should be documented

    **Conditions of activation**

    Applied at each timestep
    '''

    def __init__(self, *args, **kwargs):
        self._required_parameters = ('LIN_ALLOM_SEEDLING_DDH_HEIGHT_A',
                                     'LIN_ALLOM_SEEDLING_DDH_HEIGHT_B',
                                     'LIN_ALLOM_SAPLING_DBH_HEIGHT_A',
                                     'LIN_ALLOM_SAPLING_DBH_HEIGHT_B',
                                     'LIN_ALLOM_ADULT_DBH_HEIGHT_A',
                                     'LIN_ALLOM_ADULT_DBH_HEIGHT_B')
        super(TreeDiamHeightLinearAllometry, self).__init__(*args, **kwargs)
        self.parname = kwargs['parname']
        self.species = kwargs['species']

    def _allometry_fitting(self, objects):
        for item in [x for x in objects if x.type == 'tree']:
            tochose = self._parameters.get(item.species, self._parameters['none'])
            if item.stage == 'seedling':
                a = tochose.get('LIN_ALLOM_SEEDLING_DDH_HEIGHT_A',
                                self._parameters['none']['LIN_ALLOM_SEEDLING_DDH_HEIGHT_A'])
                b = tochose.get('LIN_ALLOM_SEEDLING_DDH_HEIGHT_B',
                                self._parameters['none']['LIN_ALLOM_SEEDLING_DDH_HEIGHT_B'])
            elif item.stage == 'sapling':
                a = tochose.get('LIN_ALLOM_SAPLING_DBH_HEIGHT_A',
                                self._parameters['none']['LIN_ALLOM_SAPLING_DBH_HEIGHT_A'])
                b = tochose.get('LIN_ALLOM_SAPLING_DBH_HEIGHT_B',
                                self._parameters['none']['LIN_ALLOM_SAPLING_DBH_HEIGHT_B'])
            elif item.stage == 'adult':
                a = tochose.get('LIN_ALLOM_ADULT_DBH_HEIGHT_A',
                                self._parameters['none']['LIN_ALLOM_ADULT_DBH_HEIGHT_A'])
                b = tochose.get('LIN_ALLOM_ADULT_DBH_HEIGHT_B',
                                self._parameters['none']['LIN_ALLOM_ADULT_DBH_HEIGHT_B'])
            if self.parname == 'height':
                item.height = a + b * (item.ddh if item.stage == 'seedling'
                                       else item.dbh)
            elif self.parname == 'dbh' and item.stage != 'seedling':
                item.dbh = (item.height - a) / b
            elif self.parname == 'ddh' and item.stage == 'seedling':
                item.ddh = (item.height - a) / b

    def process(self):
        if self.species == 'all':
            objects = self.model.objects
        else:
            objects = self.model.objects.select_by_type('tree').select_by_species([self.species])
        if objects:
            self._allometry_fitting(objects)
