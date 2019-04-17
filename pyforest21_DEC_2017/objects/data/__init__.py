import os
import six


class ObjectParameter(object):
    ''' Used to store species-specific data for modeling purposes'''

    def __init__(self, parameter, value=None, comment=''):
        self.parameter = parameter.upper()
        self.value = value
        self.comment = comment


class ObjectDataStorage(object):
    '''Main data storage

    Used to store constant species-specific parameters
    '''

    def __init__(self):
        self._pool = []
        self._auxilary = []

    def get_required_parameters(self, parameters):
        # TODO: Docs required (used for perfomance tuning)
        result = {}
        for sp in self._species:
            if sp not in result: result.update({sp: {}})
            for parname in parameters:
                result[sp].update({parname.upper():
                                   self.get_parameter(sp,
                                                      parname.upper())})
        return result

    def get_minmax_data(self, species, parameter):
        '''Get conjugate data for a given parameter and species

        This function searches couple of species and parameter in the
        current pool of loaded data. It returns (None, None) if one or both
        conditions not satisfied, otherwise it returns (value, value). It tries
        to find `Min` and `Max` values of the parameter requested.

        :param species: a species
        :param parameter: parameter name, i.e. requested parameter
        :type species: str
        :type parameter: str
        :return: tuple of min- and max- values of a parameter
        :rtype: tuple -- either (float, float) or (None, None)
        '''
        _parameter = parameter.lower()
        if '_min_' in _parameter:
            parname_min = _parameter
            parname_max = _parameter.replace('_min_', '_max_')
        elif 'min_' in _parameter:
            parname_min = _parameter
            parname_max = _parameter.replace('min_', 'max_')
        elif '_min' in _parameter:
            parname_min = _parameter
            parname_max = _parameter.replace('_min', '_max')
        elif '_max_' in _parameter:
            parname_max = _parameter
            parname_min = _parameter.replace('_max_', '_min_')
        elif '_max' in _parameter:
            parname_max = _parameter
            parname_min = _parameter.replace('_max', '_min')
        elif 'max_' in _parameter:
            parname_max = _parameter
            parname_min = _parameter.replace('max_', 'min_')
        else:
            return (None, None)
        return (self.get_parameter(species, parname_min),
                self.get_parameter(species, parname_max))

    def get_parameter(self, species, parameter):
        '''Get value for a given species and parameter name

        Searches for parameter value in the current data pool.

        It tries searching over all species for parameter requested,
        if none appropriate case (species, parameter) found, it goes
        to `fallback` parameter value defined in `fallback.py`. Finally,
        If no fallback value found it will raise exception.

        :param species: a species, e.g. tree species
        :param parameter: parameter name
        :type species: str
        :type parameter: str
        :return: requested parameter value
        :rtype: float or None 
        '''

        ckey = (species.strip() + parameter.strip()).lower()
        fallback_key = ('none' + parameter).lower()
        if ckey in self._auxilary:
            return self._pool[self._auxilary.index(ckey)].value
        elif fallback_key in self._auxilary:
            return self._pool[self._auxilary.index(fallback_key)].value
        else:
            # TODO: Raise an exeption here!!!!
            return None

    def set_parameter(self, species, parameter, value, create=False):
        '''Set value for a given species and parameter name

        Performs setting up parameter just in memory. You need
        to edit data files manually to add
        species-specific parameters

        :param species: a species, e.g. tree species
        :param parameter: parameter name
        :param value: parameter value; It could be of any type, but common
                       types used are `float`, `int` and `str`.
        :param create: If True parameter will be created if it isn't exists; default is False;
        :type species: str
        :type parameter: str
        :type value: float, int, str
        :type create: bool
        '''

        ckey = (species + parameter).lower()
        if ckey in self._auxilary:
            self._pool[self._auxilary.index(ckey)].value = value
        else:
            if create:
                self._auxilary.append(ckey)
                self._pool.append(ObjectParameter(parameter, value=value))
            else:
                # TODO: If key not found it doesn't create a new one, but raise exception
                #  Currently, it is just silent, i.e. do nothing
                pass

    def autodiscover(self, path=None):
        '''Performs data autodiscovery from current or specified folder

        Each data file is just a Python file. To be  valid it should
        have `__species__` variable defined.

        :param path: path to folder where data is stored
        :type path: string

        '''
        
        self._species = []
        if not path:
            path = os.path.dirname(os.path.abspath('__file__'))
        else:
            path = os.path.dirname(os.path.abspath(path))
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), 'r') as cf:
                        try:
                            cdict = {}
                            obj = compile(cf.read(), '', 'exec')
                            six.exec_(obj, cdict)
                            if '__species__' in cdict.keys():
                                for item in [j for j in cdict.keys() if not j.startswith('__')]:
                                    objpar = ObjectParameter(item, value=cdict[item])
                                    self._pool.append(objpar)
                                    self._auxilary.append(cdict['__species__'].lower() + item.lower())
                                    self._species.append(cdict['__species__'].lower())
                        except:
                            # TODO: Exception should be invoked here
                            pass
        self._species = set(self._species + ['none'])

pool = ObjectDataStorage()
