import unittest
from sim import burnin
from sim import model
import copy

class BurinTestCases(unittest.TestCase):
    """Tests for `burnin.py`."""

    def test_test_adf_threshold(self): 
        params = exec(open('./params.py', 'r').read())
        mod = model.Model(params = params)
        pop = None #TODO: place holder for pop after testing model
        self.assertEquals(True, burnin.test_adf_threshold(pop, 1))

    def test_test_t_threshold(self): 
        params = exec(open('./params.py', 'r').read())
        pop = None
        self.assertEquals(True, burnin.test_t_threshold(pop, 2))


if __name__ == '__main__':
    unittest.main()