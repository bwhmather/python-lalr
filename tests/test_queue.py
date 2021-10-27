import pytest

from lalr.utils import Queue


def test_iteration():
    tasks = ["A", "B", "C", "D", "E", "F"]
    queue = Queue(tasks)

    assert [task for task in queue] == tasks


def test_insertion_during_iteration():
    queue = Queue([1])

    for task in queue:
        if task >= 128:
            break
        queue.add(task * 2)

    assert list(queue.processed) == [1, 2, 4, 8, 16, 32, 64, 128]


def test_reinsertion_before_pop():
    tasks = [1, 2, 3, 4, 5]
    queue = Queue(tasks)

    processed = []
    processed += [queue.pop(), queue.pop()]
    queue.add(3)

    processed += [queue.pop(), queue.pop(), queue.pop()]

    assert processed == tasks
    assert not queue
    with pytest.raises(IndexError):
        queue.pop()


def test_reinsertion_after_pop():
    tasks = [1, 2, 3, 4, 5]
    queue = Queue(tasks)

    processed = []
    processed += [queue.pop(), queue.pop(), queue.pop()]
    queue.add(3)

    processed += [queue.pop(), queue.pop()]

    assert processed == tasks
    assert not queue
    with pytest.raises(IndexError):
        queue.pop()


def test_processed():
    queue = Queue([1, 2, 3, 4, 5])
    processed = set([queue.pop(), queue.pop()])
    assert set(queue.processed) == processed
