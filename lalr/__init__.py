from lalr.parsing import Parser


def compile(productions, target):
    return Parser(productions, target)
