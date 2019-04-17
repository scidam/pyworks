from pyforest.resources import AbstractResource
from pyforest.resources.light.utils import poly3d_qhull_intersection
import numpy as np
from scipy.spatial import ConvexHull as CH
from scipy.spatial.qhull import QhullError
from copy import copy


def get_intersection_length(point, direction, qhull):
    '''
    Computes length of intersection a convex hull by a ray starting
    from a point toward direction

    :param point: starting point, list of floats or numpy array;
    :param  direction: direction to light source (e.g. sun);
                       assumed to be  a list or numpy array;
    :type point: list
    :type direction: list
    :return: length of intersection a convex
            hull by light ray starting from a point toward given direction.
    :rtype: float
    '''
    length = 0.0
    inside = np.all(np.dot(qhull.equations[:, :3], point) + qhull.equations[:, -1] < 0.0)
    if not inside:
        res = poly3d_qhull_intersection(qhull, point, direction)
        if len(res) == 2:
            length = np.linalg.norm(res[1]-res[0])
    else:
        res = poly3d_qhull_intersection(qhull, point, direction)
        length = np.linalg.norm(res[0] - np.array(point))
    return length


class SimpleSolarIrradianceMixin(AbstractResource):
    '''
    Total Solar Irradiance
    # TODO: Full docs 
    '''

    def __init__(self, maxirradiance=100,
                 stepx=1, stepy=1, stepz=1, maxz=70, *args, **kwargs):
        '''Initialization
        '''
        self.maxirradiance = maxirradiance
        self.sundirection = kwargs['sundirection'] if 'sundirection' in kwargs else (0.0, 1./np.sqrt(2.), -1./np.sqrt(2.));
        self.stepx, self.stepy, self.stepz, self.maxz = stepx, stepy, stepz, maxz
        super(SimpleSolarIrradianceMixin, self).__init__(*args, **kwargs)

    def validate(self):
        '''
        Model should have some parameters defined in order
        to estimate Solar Irradiance properly
        '''

        if not hasattr(self.model, 'data'):
            pass
            # TODO: raise exception HERE, data is required
        elif 'orientation' in self.model.data:
            pass
            # TODO: raise exception HERE, orientation is required
        elif 'xaxis' in self.model.data['orientation']:
            # TODO: raise exception HERE, xaxis orientation is
            # required for this action
            pass

    def _get_direction(self):
        '''Get direction to south for the local coordinate system

        It is assumed that `sundirection` is a unity length vector in 3D space.
        '''

        d = np.array([self.sundirection[0], self.sundirection[1]])
        orientx = np.array([np.cos(self.model.data['orientation']['xaxis']- 3 * np.pi / 2.0),
                            np.sin(self.model.data['orientation']['xaxis'] - 3 * np.pi / 2.0)])
        if np.linalg.norm(d) > np.finfo(float).eps:
            d = d / (d[0] * d[0] + d[1] * d[1]) ** 0.5
        else:
            return np.array([0.0, 0.0, 1.0])
        zscale = np.sqrt(1.0 - self.sundirection[2] ** 2.0)
        val1 = zscale * np.dot(d, orientx)
        val2 = zscale * float(-np.cross(d, orientx))
        return np.array([val1, val2, self.sundirection[2]])

    def _generate_metadata(self, use_relief=False):
        '''Collects array of cronwn's for all objects at the plot
        '''
        crowns = []
        coords = []
        heights = []
        species = []
        for item in self.model.objects.select_by_stages(['sapling',
                                                         'adult',
                                                         'live']):
            if len(item.crown.shape) == 2:
                try:
                    crowns.append(CH(item.crown))
                    coords.append(np.mean(crowns[-1].points, axis=0))
                except QhullError:
                    crowns.append(None)
                    coords.append([None, None])
            else:
                crowns.append(None)
                coords.append([None, None])
            heights.append(item.height)
            species.append(item.species)
        self.crowns = np.array(crowns)
        self.heights = np.array(heights)
        self.coords = np.array(coords)
        self.species = np.array(species)

    def _create_meshs(self):
        '''Get meshes where light intensity will be calculated
        '''

        mx, my, mz = np.meshgrid(np.arange(self.model.bbox[0][0],
                                           self.model.bbox[0][1],
                                           self.stepx),
                                 np.arange(self.model.bbox[1][0],
                                           self.model.bbox[1][1],
                                           self.stepy),
                                 np.arange(0, self.maxz, self.stepz),
                                 )
        self.meshx = mx.ravel()
        self.meshy = my.ravel()
        self.meshz = mz.ravel()
        self.values = np.zeros(np.shape(self.meshx))

    def _lookup_crowns(self, x, y, z):
        ''' '''
        r0 = np.array([x, y, z])
        maxcrad = self._pool.get_parameter('none', 'MAX_CROWN_RADIUS')
        newr0 = r0 - self.localsun * maxcrad * 2.0
        main_filter_rule = np.dot(self.coords - newr0, self.localsun) > 0.0
        aux_filter_rule = np.linalg.norm(np.cross(self.coords - newr0,
                                                  self.localsun), axis=1) > maxcrad
        return (self.crowns[main_filter_rule & aux_filter_rule],
                self.species[main_filter_rule & aux_filter_rule])

    def _pre_computations(self):
        self.validate()
        self._generate_metadata()
        self._create_meshs()
        self.localsun = self._get_direction()
        self.mlin = self.maxirradiance * self._pool.get_parameter('none', 'MIN_LIGHT_IRRADIANCE')

    def light_model(self, lengths, sps):
        raise NotImplementedError('This method should be implemented\
        in child classes')

    def update(self):
        ''' Recompute resource data or get it from cache
        '''
        self._pre_computations()
        ind = 0
        for x, y, z in zip(self.meshx, self.meshy, self.meshz):
            crown_list, species = self._lookup_crowns(x, y, z)
            if len(crown_list) == 0:
                self.values[ind] = self.maxirradiance
                continue
            lengths, sps = [], []
            for crown, sp in zip(crown_list, species):
                if isinstance(crown, CH):
                    lengths.append(get_intersection_length(np.array([x, y, z]),
                                                           self.localsun,
                                                           crown))
                    sps.append(sp)
            self.values[ind] = self.light_model(lengths, sps)
            ind += 1


class SolarDirectIrradiance(SimpleSolarIrradianceMixin):

    def light_model(self, lengths, sps):
        curint = self.maxirradiance
        for sp, l in zip(sps, lengths):
            slope = self._pool.get_parameter(sp,
                                             'LIGHT_INTENSITY_LINEAR_SLOPE')
            slope = slope if 0.0 <= slope <= 1.0 else 0.0
            curint -= -slope * l
            if curint < self.mlin:
                curint = self.mlin
                break
        return curint


class SolarDirectMonsiSaekiIrradiance(SimpleSolarIrradianceMixin):
    def light_model(self, lengths, sps):
        curint = self.maxirradiance
        for sp in sps:
            k = self._pool.get_parameter(sp,
                                             'LIGHT_ABSORPTION_MONSI_SAEKI')
            LAI = self._pool.get_parameter(sp,
                                             'LEAF_AREA_INDEX')
            curint = curint * np.exp(-k * LAI)
        return curint


class SolarDirectMonsiSaekiAdoptedIrradiance(SimpleSolarIrradianceMixin):
    def light_model(self, lengths, sps):
        curint = self.maxirradiance
        for l, sp in zip(lengths, sps):
            lmax = self._pool.get_parameter(sp,
                                            'CANOPY_LEN_MAX_MONSI_SAEKI_ADOPTED')
            LAI = self._pool.get_parameter(sp,
                                             'LEAF_AREA_INDEX')
            kmax = self._pool.get_parameter(sp,
                                            'LIGHT_ABSORPTION_MAX_MONSI_SAEKI_ADOPTED')
            if 0.0 <= l <= lmax:
                k = l * kmax / lmax
            elif l > lmax:
                k = kmax
            else:
                continue
            curint = curint * np.exp(-k * LAI)
        return curint
