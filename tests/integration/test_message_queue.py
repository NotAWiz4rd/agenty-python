"""Integration tests: message queue concurrency."""
import threading

import pytest

import context_handling
from context_handling import add_to_message_queue, get_all_from_message_queue


@pytest.fixture(autouse=True)
def drain_queue():
    while not context_handling.message_queue.empty():
        context_handling.message_queue.get()
    yield
    while not context_handling.message_queue.empty():
        context_handling.message_queue.get()


class TestMessageQueueConcurrency:
    def test_no_messages_lost_under_concurrent_writes(self):
        """Simulate API endpoint calling add_to_message_queue from multiple threads."""
        num_threads = 50
        barrier = threading.Barrier(num_threads)

        def producer(i):
            barrier.wait()
            add_to_message_queue(f"message_{i}")

        threads = [threading.Thread(target=producer, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        all_msgs = get_all_from_message_queue()
        assert len(all_msgs) == num_threads
        assert set(all_msgs) == {f"message_{i}" for i in range(num_threads)}

    def test_queue_empty_after_full_drain(self):
        for i in range(10):
            add_to_message_queue(f"msg_{i}")
        msgs = get_all_from_message_queue()
        assert len(msgs) == 10
        # Queue should now be empty
        assert get_all_from_message_queue() == []

    def test_concurrent_write_and_drain(self):
        """Writers and a single drainer run concurrently; no messages are lost."""
        collected = []
        stop_event = threading.Event()
        num_writers = 20

        def writer(i):
            add_to_message_queue(f"w_{i}")

        def drainer():
            while not stop_event.is_set() or not context_handling.message_queue.empty():
                msgs = get_all_from_message_queue()
                collected.extend(msgs)

        drain_thread = threading.Thread(target=drainer)
        drain_thread.start()

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(num_writers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stop_event.set()
        drain_thread.join()

        # Drain any remaining
        collected.extend(get_all_from_message_queue())
        assert len(collected) == num_writers
        assert set(collected) == {f"w_{i}" for i in range(num_writers)}

    def test_add_returns_true_always(self):
        for i in range(5):
            assert add_to_message_queue(f"m{i}") is True
