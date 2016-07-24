import unittest

import lalr


class ItemSetTestCase(unittest.TestCase):
    def test_zero(self):
        grammar = lalr.Grammar(
            set(), {'a'},
        )

        starting_item = lalr.Item(lalr.Production('S', ('a',)), 0, {'$'})

        item_set = lalr.build_item_set(grammar, {starting_item})
        self.assertEqual(item_set.items, {starting_item})

    def test_one(self):
        grammar = lalr.Grammar(
            {lalr.Production('A', ('a',))},
            {'a'},
        )

        starting_item = lalr.Item(lalr.Production('S', ('A',)), 0, {'$'})

        item_set = lalr.build_item_set(grammar, {starting_item})

        self.assertEqual(item_set.items, {
            lalr.Item(lalr.Production('S', ('A',)), 0, {'$'}),
            lalr.Item(lalr.Production('A', ('a',)), 0, {'$'}),
        })

    def test_example(self):
        grammar = lalr.Grammar([
            lalr.Production("N", ("V", "=", "E")),
            lalr.Production("N", ("E",)),
            lalr.Production("E", ("V",)),
            lalr.Production("V", ("x",)),
            lalr.Production("V", ("*", "E")),
        ], {"x", "=", "*"})

        sets, transitions = lalr.build_transition_table(grammar, "N")

        for num, item_set in enumerate(sets):
            print(num)
            for item in item_set.kernel:
                print(item)
            for item in item_set.derived:
                print('+ ' + str(item))
            print()

            print(transitions[num])


class FirstSetsTestCase(unittest.TestCase):
    def test_loop(self):
        grammar = lalr.Grammar([
            lalr.Production("A", ("B",)),
            lalr.Production("A", ("x",)),
            lalr.Production("B", ("A",)),
        ], {"x"})

        self.assertEqual(lalr.build_first_sets(grammar), {
            "x": {"x"},
            "A": {"x"},
            "B": {"x"},
        })

    def test_example(self):
        grammar = lalr.Grammar([
            lalr.Production("N", ("V", "=", "E")),
            lalr.Production("N", ("E",)),
            lalr.Production("E", ("V",)),
            lalr.Production("V", ("x",)),
            lalr.Production("V", ("*", "E")),
        ], {"x", "=", "*"})

        self.assertEqual(lalr.build_first_sets(grammar), {
            "x": {"x"},
            "=": {"="},
            "*": {"*"},
            "N": {"*", "x"},
            "N": {"*", "x"},
            "E": {"*", "x"},
            "V": {"*", "x"},
            "V": {"*", "x"},
        })


class ParseTestCase(unittest.TestCase):
    def test_example(self):
        grammar = lalr.Grammar([
            lalr.Production("N", ("V", "=", "E")),
            lalr.Production("N", ("E",)),
            lalr.Production("E", ("V",)),
            lalr.Production("V", ("x",)),
            lalr.Production("V", ("*", "E")),
        ], {"x", "=", "*"})

        item_sets, transitions = lalr.build_transition_table(grammar, "N")

        shifts = lalr.build_shift_table(grammar, item_sets, transitions)
        gotos = lalr.build_goto_table(grammar, item_sets, transitions)
        reductions = lalr.build_reduction_table(
            grammar, item_sets, transitions,
        )
        accepts = lalr.build_accept_table(grammar, item_sets, transitions)

        parser = lalr.Parser(item_sets, shifts, reductions, gotos, accepts)

        parser.parse(["x", "=", "*", "x"])

    def test_bad_example(self):
        grammar = lalr.Grammar([
            lalr.Production("N", ("V", "=", "E")),
            lalr.Production("N", ("E",)),
            lalr.Production("E", ("V",)),
            lalr.Production("V", ("x",)),
            lalr.Production("V", ("*", "E")),
        ], {"x", "=", "*"})

        item_sets, transitions = lalr.build_transition_table(grammar, "N")

        shifts = lalr.build_shift_table(grammar, item_sets, transitions)
        gotos = lalr.build_goto_table(grammar, item_sets, transitions)
        reductions = lalr.build_reduction_table(
            grammar, item_sets, transitions,
        )
        accepts = lalr.build_accept_table(grammar, item_sets, transitions)

        parser = lalr.Parser(item_sets, shifts, reductions, gotos, accepts)

        with self.assertRaises(lalr.ParseError):
            parser.parse(["x", "*", "x"])


loader = unittest.TestLoader()
suite = unittest.TestSuite((
    loader.loadTestsFromTestCase(ItemSetTestCase),
    loader.loadTestsFromTestCase(FirstSetsTestCase),
    loader.loadTestsFromTestCase(ParseTestCase),
))
