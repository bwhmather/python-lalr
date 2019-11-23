import unittest

from lalr.analysis import _build_item_set, _build_transition_table, _Item
from lalr.grammar import Grammar, InternalProduction


class _ItemSetTestCase(unittest.TestCase):
    def test_zero(self):
        grammar = Grammar([])

        starting_item = _Item(
            InternalProduction('S', ('a',)), 0, {'$'},
        )

        item_set = _build_item_set(grammar, {starting_item})
        self.assertEqual(item_set.items, {starting_item})

    def test_one(self):
        grammar = Grammar([
            InternalProduction('A', ('a',)),
        ])

        starting_item = _Item(
            InternalProduction('S', ('A',)), 0, {'$'},
        )

        item_set = _build_item_set(grammar, {starting_item})

        self.assertEqual(item_set.items, {
            _Item(InternalProduction('S', ('A',)), 0, {'$'}),
            _Item(InternalProduction('A', ('a',)), 0, {'$'}),
        })

    def test_example(self):
        grammar = Grammar([
            InternalProduction("N", ("V", "=", "E")),
            InternalProduction("N", ("E",)),
            InternalProduction("E", ("V",)),
            InternalProduction("V", ("x",)),
            InternalProduction("V", ("*", "E")),
        ])

        sets, transitions = _build_transition_table(grammar, "N")

        for num, item_set in enumerate(sets):
            print(num)
            for item in item_set.kernel:
                print(item)
            for item in item_set.derived:
                print('+ ' + str(item))
            print()

            print(transitions[num])
