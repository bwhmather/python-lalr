import unittest
from lalr.tests import test_queue
from lalr.tests import test_grammar
from lalr.tests import test_analysis
from lalr.tests import test_parsing
from lalr.tests import test_frontend


loader = unittest.TestLoader()
suite = unittest.TestSuite((
    loader.loadTestsFromModule(test_queue),  # type: ignore
    loader.loadTestsFromModule(test_parsing),  # type: ignore
    loader.loadTestsFromModule(test_analysis),  # type: ignore
    loader.loadTestsFromModule(test_grammar),  # type: ignore
    loader.loadTestsFromModule(test_frontend),  # type: ignore
))
