import unittest

from lalr.utils import Queue


class ParseTestCase(unittest.TestCase):
    def test_iteration(self):
        tasks = ['A', 'B', 'C', 'D', 'E', 'F']
        queue = Queue(tasks)

        self.assertEqual([task for task in queue], tasks)

    def test_insertion_during_iteration(self):
        queue = Queue([1])

        for task in queue:
            if task >= 128:
                break
            queue.add(task * 2)

        self.assertEqual(
            list(queue.processed),
            [1, 2, 4, 8, 16, 32, 64, 128],
        )

    def test_reinsertion_before_pop(self):
        tasks = [1, 2, 3, 4, 5]
        queue = Queue(tasks)

        processed = []
        processed += [queue.pop(), queue.pop()]
        queue.add(3)

        processed += [queue.pop(), queue.pop(), queue.pop()]

        self.assertEqual(processed, tasks)
        self.assertFalse(queue)
        self.assertRaises(IndexError, queue.pop)

    def test_reinsertion_after_pop(self):
        tasks = [1, 2, 3, 4, 5]
        queue = Queue(tasks)

        processed = []
        processed += [queue.pop(), queue.pop(), queue.pop()]
        queue.add(3)

        processed += [queue.pop(), queue.pop()]

        self.assertEqual(processed, tasks)
        self.assertFalse(queue)
        self.assertRaises(IndexError, queue.pop)

    def test_processed(self):
        queue = Queue([1, 2, 3, 4, 5])
        processed = set([queue.pop(), queue.pop()])
        self.assertEqual(set(queue.processed), processed)
