class Queue(object):
    def __init__(self, items=[]):
        self._queued = list(items)
        self._all = set(items)

    def add(self, item):
        if item not in self._all:
            self._queued.append(item)
            self._all.add(item)

    def update(self, items):
        for item in items:
            self.add(item)

    def pop(self):
        return self._queued.pop()

    def __len__(self):
        return len(self._queued)

    def __bool__(self):
        return bool(self._queued)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.pop()
        except IndexError:
            raise StopIteration()
