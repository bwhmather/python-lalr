import unittest

from lalr.analysis import (
    ParseTable,
    _build_item_set,
    _build_transition_table,
    _Item,
)
from lalr.exceptions import ReduceReduceConflictError
from lalr.grammar import Grammar, Production


class _ItemSetTestCase(unittest.TestCase):
    def test_zero(self):
        grammar = Grammar([])

        starting_item = _Item(
            Production("S", ("a",)),
            0,
            {"$"},
        )

        item_set = _build_item_set(grammar, {starting_item})
        self.assertEqual(item_set.items, {starting_item})

    def test_one(self):
        grammar = Grammar(
            [
                Production("A", ("a",)),
            ]
        )

        starting_item = _Item(
            Production("S", ("A",)),
            0,
            {"$"},
        )

        item_set = _build_item_set(grammar, {starting_item})

        self.assertEqual(
            item_set.items,
            {
                _Item(Production("S", ("A",)), 0, {"$"}),
                _Item(Production("A", ("a",)), 0, {"$"}),
            },
        )

    def test_example(self):
        grammar = Grammar(
            [
                Production("N", ("V", "=", "E")),
                Production("N", ("E",)),
                Production("E", ("V",)),
                Production("V", ("x",)),
                Production("V", ("*", "E")),
            ]
        )

        sets, transitions = _build_transition_table(grammar, "N")

        for num, item_set in enumerate(sets):
            print(num)
            for item in item_set.kernel:
                print(item)
            for item in item_set.derived:
                print("+ " + str(item))
            print()

            print(transitions[num])

    def test_lalr_reduce_reduce(self):
        grammar = Grammar(
            [
                Production("S", ("a", "E", "c")),
                Production("S", ("a", "F", "d")),
                Production("S", ("b", "F", "c")),
                Production("S", ("b", "E", "d")),
                Production("E", ("e",)),
                Production("F", ("e",)),
            ]
        )

        with self.assertRaises(ReduceReduceConflictError):
            ParseTable(grammar, "S")
