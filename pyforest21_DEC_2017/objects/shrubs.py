from pyforest.utils import setup_value

from pyforest.objects import WoodyPlantMixin


SHRUB_STAGES = ('live',
                'dead'
                )


class AbstractShrub(WoodyPlantMixin):
    def __init__(self, *args, **kwargs):
        super(AbstractShrub, self).__init__(*args, **kwargs)
        setup_value(self, kwargs, 'species')
        setup_value(self, kwargs, 'height', value=0)
        setup_value(self, kwargs, 'diam', value=0)
        self.type = 'shrub'

    @property
    def stage(self):
        return self._stage

    @stage.setter
    def stage(self, value):
        if value in SHRUB_STAGES:
            self._stage = value


class Shrub(AbstractShrub):
    def __init__(self, *args, **kwargs):
        super(Shrub, self).__init__(*args, **kwargs)
