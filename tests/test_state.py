import pytest

from dictatore.state import AppState, StateMachine


def test_full_valid_cycle():
    sm = StateMachine()
    assert sm.state is AppState.IDLE
    sm.transition(AppState.RECORDING)
    sm.transition(AppState.PROCESSING)
    sm.transition(AppState.IDLE)
    assert sm.state is AppState.IDLE


def test_recording_lock_transition():
    sm = StateMachine()
    sm.transition(AppState.RECORDING)
    sm.transition(AppState.RECORDING_LOCKED)
    sm.transition(AppState.PROCESSING)
    assert sm.state is AppState.PROCESSING


def test_invalid_transition_raises():
    sm = StateMachine()
    with pytest.raises(ValueError):
        sm.transition(AppState.PROCESSING)  # IDLE -> PROCESSING not allowed
    with pytest.raises(ValueError):
        sm.transition(AppState.IDLE)  # IDLE -> IDLE not allowed


def test_reset_returns_to_idle():
    sm = StateMachine()
    sm.transition(AppState.RECORDING)
    sm.reset()
    assert sm.state is AppState.IDLE
