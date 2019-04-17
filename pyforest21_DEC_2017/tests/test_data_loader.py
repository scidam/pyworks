
from unittest import TestCase
import unittest

from pyforest.objects.data import ObjectParameter, ObjectDataStorage


class TestDataPoolWorkingProcess(TestCase):
    def setUp(self):
        self.pool = ObjectDataStorage()
        # TODO: autodiscover uses path where from discovery starts
        self.pool.autodiscover(path='./objects/data')

    def test_set_data(self):
        species = 'Betula mandshurica'
        parameter = 'MAX_HEIGHT'
        value = 54.0
        self.pool.set_parameter(species, parameter, value)
        self.assertEqual(self.pool.get_parameter(species, parameter), value)

    def test_get_stored_data(self):
        species = 'quercuS monGolica'  # Case insensitive!
        parameter = 'SEEDLINGS_CREATION_MAX_DDH'
        self.assertEqual(self.pool.get_parameter(species, parameter), 0.5)

    def test_autodiscover_works(self):
        self.assertIsInstance(self.pool._pool[0], ObjectParameter)

    def test_keys_not_include___(self):
        '''Check for parameter names to not inclue `__` '''
        for item in self.pool._auxilary:
            self.assertFalse(item.startswith('__'))

    def test_minmax_getting(self):
        values = self.pool.get_minmax_data('quercus mongolica',
                                           'SEEDLINGS_CREATION_MIN_DDH')
        self.assertEqual(values, (0.1, 0.5))
