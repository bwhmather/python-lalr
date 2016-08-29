class Queue(object):
    def __init__(self, items=[]):
        self._cursor = 0
        self._by_order = list()
        self._by_identity = set()

        self.update(items)

    def add(self, item):
        if item not in self._by_identity:
            self._by_order.append(item)
            self._by_identity.add(item)

    def update(self, items):
        for item in items:
            self.add(item)

    def pop(self):
        if self._cursor == len(self._by_order):
            raise IndexError()
        value = self._by_order[self._cursor]
        self._cursor += 1
        return value

    @property
    def processed(self):
        return self._by_order[:self._cursor]

    def __len__(self):
        return len(len(self._by_order) - self._cursor)

    def __bool__(self):
        return self._cursor != len(self._by_order)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.pop()
        except IndexError:
            raise StopIteration()
