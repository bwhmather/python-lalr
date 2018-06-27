from typing import TypeVar, Generic, Iterable, Hashable, Set, List


T = TypeVar('T', bound=Hashable)


class Queue(Iterable[T], Generic[T]):
    def __init__(self, items: Iterable[T]=[]) -> None:
        # The set of all items that have been added to the queue.
        # TODO:  Benchmark to determine if this is actually faster.
        self._by_identity: Set[T] = set()

        # A list, in order, of all items that have been added to the queue.
        self._by_order: List[T] = list()

        # The index of the next item to be processed in the `_by_order` array.
        self._cursor: int = 0

        self.update(items)

    def add(self, item: T):
        if item not in self._by_identity:
            self._by_order.append(item)
            self._by_identity.add(item)

    def update(self, items: Iterable[T]):
        for item in items:
            self.add(item)

    def pop(self) -> T:
        if self._cursor == len(self._by_order):
            raise IndexError()
        value = self._by_order[self._cursor]
        self._cursor += 1
        return value

    @property
    def processed(self) -> Iterable[T]:
        return self._by_order[:self._cursor]

    def __len__(self) -> int:
        return len(self._by_order) - self._cursor

    def __bool__(self) -> bool:
        return self._cursor != len(self._by_order)

    def __iter__(self):
        return self

    def __next__(self) -> T:
        try:
            return self.pop()
        except IndexError:
            raise StopIteration()
