import unittest

from lalr.tests import test_analysis, test_grammar, test_parsing, test_queue


loader = unittest.TestLoader()
suite = unittest.TestSuite((
    loader.loadTestsFromModule(test_queue),
    loader.loadTestsFromModule(test_parsing),
    loader.loadTestsFromModule(test_analysis),
    loader.loadTestsFromModule(test_grammar),
))
