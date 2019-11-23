from typing import Generic, Hashable, Iterable, List, Set, TypeVar


T = TypeVar('T', bound=Hashable)


class Queue(Iterable[T], Generic[T]):
    """
    A simple task queue that will yield the items added to it exactly than
    once.
    """
    def __init__(self, items: Iterable[T] = []) -> None:
        # The set of all items that have been added to the queue.
        # TODO:  Benchmark to determine if this is actually faster.
        self._by_identity: Set[T] = set()

        # A list, in order, of all items that have been added to the queue.
        self._by_order: List[T] = list()

        # The index of the next item to be processed in the `_by_order` array.
        self._cursor: int = 0

        self.update(items)

    def add(self, item: T):
        """
        Attempts to add an item to the end of the queue.

        If the item is already in the queue, or has already been processed,
        this call will have no effect.

        :param item:
            The item to add.
        """
        if item not in self._by_identity:
            self._by_order.append(item)
            self._by_identity.add(item)

    def update(self, items: Iterable[T]):
        """
        Adds all new items in iterable, in order, to the end of the queue.

        :param items:
            An iterable of items to process.
        """
        for item in items:
            self.add(item)

    def pop(self) -> T:
        """
        Removes and returns the next item that is waiting to be processed.

        Raises :exception:`IndexError` if there are no unprocessed items
        remaining.

        :return:
            The next item in the queue.
        """
        if self._cursor == len(self._by_order):
            raise IndexError("queue is empty")
        value = self._by_order[self._cursor]
        self._cursor += 1
        return value

    @property
    def processed(self) -> Iterable[T]:
        """
        Returns an iterable over all of the items in the queue that have
        already been processed.

        The items will be returned in their original order.

        :return:
            An iterable of work items.
        """
        return self._by_order[:self._cursor]

    def __len__(self) -> int:
        """
        Returns the number of unprocessed items in the queue.
        """
        return len(self._by_order) - self._cursor

    def __bool__(self) -> bool:
        """
        Returns True if there are any items that are waiting to be processed.
        """
        return self._cursor != len(self._by_order)

    def __iter__(self):
        return self

    def __next__(self) -> T:
        try:
            return self.pop()
        except IndexError:
            raise StopIteration()
