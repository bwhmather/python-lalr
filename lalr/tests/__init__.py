import unittest
from lalr.tests import test_grammar
from lalr.tests import test_analysis
from lalr.tests import test_parsing


loader = unittest.TestLoader()
suite = unittest.TestSuite((
    loader.loadTestsFromModule(test_parsing),
    loader.loadTestsFromModule(test_analysis),
    loader.loadTestsFromModule(test_grammar),
))
