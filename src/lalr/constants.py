class _Constant(object):
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return str(self._name)

    def __repr__(self):
        return "<{name}>".format(name=self._name)


START = _Constant('S')
EMPTY = _Constant('E')
EOF = _Constant('$')
