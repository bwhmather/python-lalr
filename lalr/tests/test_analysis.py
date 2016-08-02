import unittest
from lalr.analysis import Item, build_item_set, build_transition_table
from lalr.grammar import Grammar, Production


class ItemSetTestCase(unittest.TestCase):
    def test_zero(self):
        grammar = Grammar([])

        starting_item = Item(
            Production('S', ('a',)), 0, {'$'},
        )

        item_set = build_item_set(grammar, {starting_item})
        self.assertEqual(item_set.items, {starting_item})

    def test_one(self):
        grammar = Grammar([
            Production('A', ('a',)),
        ])

        starting_item = Item(
            Production('S', ('A',)), 0, {'$'},
        )

        item_set = build_item_set(grammar, {starting_item})

        self.assertEqual(item_set.items, {
            Item(Production('S', ('A',)), 0, {'$'}),
            Item(Production('A', ('a',)), 0, {'$'}),
        })

    def test_example(self):
        grammar = Grammar([
            Production("N", ("V", "=", "E")),
            Production("N", ("E",)),
            Production("E", ("V",)),
            Production("V", ("x",)),
            Production("V", ("*", "E")),
        ])

        sets, transitions = build_transition_table(grammar, "N")

        for num, item_set in enumerate(sets):
            print(num)
            for item in item_set.kernel:
                print(item)
            for item in item_set.derived:
                print('+ ' + str(item))
            print()

            print(transitions[num])
