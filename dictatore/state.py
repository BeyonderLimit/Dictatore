from enum import Enum, auto


class AppState(Enum):
    IDLE = auto()
    RECORDING = auto()
    RECORDING_LOCKED = auto()
    PROCESSING = auto()


_TRANSITIONS: dict[AppState, set[AppState]] = {
    AppState.IDLE: {AppState.RECORDING},
    AppState.RECORDING: {AppState.RECORDING_LOCKED, AppState.PROCESSING},
    AppState.RECORDING_LOCKED: {AppState.PROCESSING},
    AppState.PROCESSING: {AppState.IDLE},
}


class StateMachine:
    def __init__(self) -> None:
        self._state = AppState.IDLE

    @property
    def state(self) -> AppState:
        return self._state

    def transition(self, new_state: AppState) -> None:
        allowed = _TRANSITIONS.get(self._state)
        if allowed is None or new_state not in allowed:
            raise ValueError(
                f"Cannot transition from {self._state.name} to {new_state.name}"
            )
        self._state = new_state

    def reset(self) -> None:
        self._state = AppState.IDLE
