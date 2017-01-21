import unittest
from lalr.frontend import _parse_production_spec


class MiniLanguageTestCase(unittest.TestCase):
    def test_symbol(self):
        symbols, bindings = _parse_production_spec('a')

        self.assertEqual(symbols, ('a',))
        self.assertEqual(bindings, (None,))

    def test_symbol_binding(self):
        symbols, bindings = _parse_production_spec('symbol:binding')

        self.assertEqual(symbols, ('symbol',))
        self.assertEqual(bindings, ('binding',))

    def test_multiple_symbol_bindings(self):
        symbols, bindings = _parse_production_spec(
            'symbol_a:binding_a symbol_b:binding_b',
        )

        self.assertEqual(symbols, ('symbol_a', 'symbol_b'))
        self.assertEqual(bindings, ('binding_a', 'binding_b'))

    def test_unbound_symbols(self):
        symbols, bindings = _parse_production_spec(
            'symbol_a symbol_b:binding_b',
        )

        self.assertEqual(symbols, ('symbol_a', 'symbol_b'))
        self.assertEqual(bindings, (None, 'binding_b'))

    def test_whitespace(self):
        symbols, bindings = _parse_production_spec('''
            symbol_a: binding_a
            symbolb : binding_b
        ''')
