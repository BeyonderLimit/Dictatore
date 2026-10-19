from dictatore.events import Event, EventBus


def test_emit_calls_subscribers_with_event_and_data():
    bus = EventBus()
    received = []
    bus.on(Event.AUDIO_CHUNK, lambda event, **data: received.append((event, data)))
    bus.emit(Event.AUDIO_CHUNK, chunk=b"123")
    assert received == [(Event.AUDIO_CHUNK, {"chunk": b"123"})]


def test_multiple_handlers_all_called():
    bus = EventBus()
    calls = []
    bus.on(Event.KEY_DOWN, lambda event, **d: calls.append("first"))
    bus.on(Event.KEY_DOWN, lambda event, **d: calls.append("second"))
    bus.emit(Event.KEY_DOWN)
    assert calls == ["first", "second"]


def test_off_removes_handler():
    bus = EventBus()
    handler = lambda event, **d: calls.append("x")  # noqa: E731
    calls = []
    bus.on(Event.KEY_UP, handler)
    bus.off(Event.KEY_UP, handler)
    bus.emit(Event.KEY_UP)
    assert calls == []


def test_emit_without_handlers_is_noop():
    bus = EventBus()
    bus.emit(Event.STATE_CHANGED)
