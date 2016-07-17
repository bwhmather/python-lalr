import unittest

import lalr


class ItemSetTestCase(unittest.TestCase):
    def test_zero(self):

        grammar = lalr.Grammar(
            set(), {'a'},
        )

        starting_item = lalr.Item(lalr.Production('S', ('a',)))
        item_set = lalr.build_item_set(grammar, {starting_item})
        self.assertEqual(item_set.items, {starting_item})

    def test_one(self):
        grammar = lalr.Grammar(
            {lalr.Production('A', ('a',))},
            {'a'},
        )

        starting_item = lalr.Item(lalr.Production('S', ('A',)))

        item_set = lalr.build_item_set(grammar, {starting_item})

        self.assertEqual(item_set.items, {
            lalr.Item(lalr.Production('S', ('A',))),
            lalr.Item(lalr.Production('A', ('a',))),
        })


class ItemSetTestCase(unittest.TestCase):
    def test_example(self):
        grammar = lalr.Grammar([
            lalr.Production("S", ("N",)),
            lalr.Production("N", ("V", "=", "E")),
            lalr.Production("N", ("E",)),
            lalr.Production("E", ("V",)),
            lalr.Production("V", ("x",)),
            lalr.Production("V", ("*", "E")),
        ], {"x", "=", "*"})
        print(grammar)
        sets, transitions = lalr.build_transition_table(grammar, "S")

        for num, item_set in enumerate(sets):
            print(num)
            for item in item_set.items:
                print(item)
            print()

            print(transitions[num])

        


loader = unittest.TestLoader()
suite = unittest.TestSuite((
    loader.loadTestsFromTestCase(ItemSetTestCase),
))
