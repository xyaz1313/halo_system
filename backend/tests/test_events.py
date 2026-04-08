"""Event bus tests — publish/subscribe, exception isolation, reset."""

from backend.events.bus import bus


class TestEventBus:
    def test_subscribe_and_publish(self):
        received = []

        def handler(**kwargs):
            received.append(kwargs)

        bus.subscribe("test_event", handler)
        bus.publish("test_event", data="hello")

        assert len(received) == 1
        assert received[0]["event_type"] == "test_event"
        assert received[0]["data"] == "hello"

    def test_multiple_handlers(self):
        calls = []

        def h1(**kwargs):
            calls.append("h1")

        def h2(**kwargs):
            calls.append("h2")

        bus.subscribe("multi", h1)
        bus.subscribe("multi", h2)
        bus.publish("multi")

        assert calls == ["h1", "h2"]

    def test_handler_exception_isolation(self):
        """A failing handler must not prevent other handlers from running."""
        calls = []

        def bad_handler(**kwargs):
            raise RuntimeError("I fail")

        def good_handler(**kwargs):
            calls.append("ok")

        bus.subscribe("error_test", bad_handler)
        bus.subscribe("error_test", good_handler)
        bus.publish("error_test")

        assert calls == ["ok"]

    def test_unsubscribe(self):
        calls = []

        def handler(**kwargs):
            calls.append(1)

        bus.subscribe("unsub_test", handler)
        bus.unsubscribe("unsub_test", handler)
        bus.publish("unsub_test")

        assert calls == []

    def test_unsubscribe_idempotent(self):
        """Unsubscribing a handler that is not registered should not error."""

        def handler(**kwargs):
            pass

        # Should not raise
        bus.unsubscribe("no_such_event", handler)

    def test_reset_clears_all(self):
        calls = []

        def handler(**kwargs):
            calls.append(1)

        bus.subscribe("reset_test", handler)
        bus.reset()
        bus.publish("reset_test")

        assert calls == []

    def test_publish_no_subscribers(self):
        """Publishing an event with no subscribers should not error."""
        bus.publish("nobody_listens", data="value")
