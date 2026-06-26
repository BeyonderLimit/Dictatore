from enum import Enum, auto
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable


class Event(Enum):
    KEY_DOWN = auto()
    KEY_UP = auto()
    HOLD_TOGGLE = auto()
    RECORDER_STARTED = auto()
    RECORDER_STOPPED = auto()
    AUDIO_CHUNK = auto()
    PARTIAL_RECOGNITION = auto()
    FINAL_RECOGNITION = auto()
    RECOGNITION_ERROR = auto()
    STATE_CHANGED = auto()
    TEXT_PIPELINE_DONE = auto()
    OUTPUT_DONE = auto()
    DAEMON_QUIT = auto()


Handler = Callable[..., None]


@dataclass
class EventBus:
    _handlers: dict[Event, list[Handler]] = field(
        default_factory=lambda: defaultdict(list), init=False, repr=False
    )

    def on(self, event: Event, handler: Handler) -> None:
        self._handlers[event].append(handler)

    def off(self, event: Event, handler: Handler) -> None:
        self._handlers[event].remove(handler)

    def emit(self, event: Event, **data: Any) -> None:
        for handler in self._handlers[event]:
            handler(event=event, **data)
