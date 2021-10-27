import pytest

from lalr.grammar import Grammar, Production


def test_production_name_immutable():
    production = Production("A", ("B",))
    with pytest.raises(AttributeError):
        production.name = "a"


def test_production_symbols_immutable():
    production = Production("A", ("B",))
    with pytest.raises(AttributeError):
        production.symbols = ("b",)


def test_terminals_loop():
    grammar = Grammar(
        [
            Production("A", ("B",)),
            Production("A", ("x",)),
            Production("B", ("A",)),
        ],
    )
    assert grammar.terminals() == {"x"}


def test_terminals_example():
    grammar = Grammar(
        [
            Production("N", ("V", "=", "E")),
            Production("N", ("E",)),
            Production("E", ("V",)),
            Production("V", ("x",)),
            Production("V", ("*", "E")),
        ]
    )
    assert grammar.terminals() == {"x", "=", "*"}


def test_first_set_loop():
    grammar = Grammar(
        [
            Production("A", ("B",)),
            Production("A", ("x",)),
            Production("B", ("A",)),
        ]
    )

    assert grammar.first_set("x") == {"x"}
    assert grammar.first_set("A") == {"x"}
    assert grammar.first_set("B") == {"x"}


def test_first_set_example():
    grammar = Grammar(
        [
            Production("N", ("V", "=", "E")),
            Production("N", ("E",)),
            Production("E", ("V",)),
            Production("V", ("x",)),
            Production("V", ("*", "E")),
        ]
    )

    assert grammar.first_set("x") == {"x"}
    assert grammar.first_set("=") == {"="}
    assert grammar.first_set("*") == {"*"}
    assert grammar.first_set("N") == {"*", "x"}
    assert grammar.first_set("E") == {"*", "x"}
    assert grammar.first_set("V") == {"*", "x"}
