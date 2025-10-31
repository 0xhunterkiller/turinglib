# tests/test_core.py
import pytest
from turinglib import TapeVar, State, StateMachine, Action, ActionPrimitive, BLANK


# ---------------------------------------------------------------------
# TapeVar Tests
# ---------------------------------------------------------------------

def test_tapevar_equality_and_hash():
    """TapeVars with the same notation should compare equal and hash identically."""
    a, b, c = TapeVar(0), TapeVar(0), TapeVar(1)
    assert a == b
    assert a != c
    assert hash(a) == hash(b)
    assert not a.is_blank
    assert TapeVar(None).is_blank


def test_blank_constant_equivalence():
    """BLANK should be equal to TapeVar(None)."""
    assert BLANK == TapeVar(None)
    assert BLANK.is_blank
    assert repr(BLANK) == "_"


def test_tapevar_is_immutable():
    """TapeVar objects must be immutable after creation."""
    a = TapeVar(1)
    with pytest.raises(AttributeError):
        a._notation = 0


# ---------------------------------------------------------------------
# Action / ActionPrimitive Tests
# ---------------------------------------------------------------------

def test_action_perform():
    """Actions should correctly transform head positions."""
    assert Action.R.value.perform(0) == 1
    assert Action.L.value.perform(0) == -1
    assert Action.N.value.perform(5) == 5

def test_custom_actionprimitive():
    """Custom ActionPrimitives should behave as defined."""
    R2 = ActionPrimitive("R2", lambda h: h + 2)
    assert R2.perform(0) == 2
    assert repr(R2) == "R2"


# ---------------------------------------------------------------------
# State Tests
# ---------------------------------------------------------------------

def test_state_basic_transition():
    """A simple State transition should yield the expected next state and write."""
    zero, one = TapeVar(0), TapeVar(1)
    q0 = State("q0", {})
    q1 = State("q1", {})
    q0.transitions = {zero: (q1, one, Action.R)}

    next_state, new_tv, new_head = q0.update(zero, 0, implicit_blank_halt=True)
    assert next_state == q1
    assert new_tv == one
    assert new_head == 1


def test_state_halts_on_no_transition():
    """If no transition is defined, update() should return None as next state."""
    zero = TapeVar(0)
    q0 = State("q0", {})
    next_state, new_tv, new_head = q0.update(zero, 0, implicit_blank_halt=True)
    assert next_state is None
    assert new_tv == zero
    assert new_head == 0


# ---------------------------------------------------------------------
# StateMachine Tests
# ---------------------------------------------------------------------

def test_machine_right_growth():
    """Machine should extend tape to the right when head moves beyond end."""
    zero, one = TapeVar(0), TapeVar(1)
    q0 = State("q0", {})
    halt = State("HALT", {})
    q0.transitions = {zero: (halt, one, Action.R)}
    tm = StateMachine(start=q0, input_tape=[zero], start_point=0, verbose=False)

    tm.step()
    assert len(tm.tape) == 2
    assert tm.tape[-1] == BLANK
    assert tm.current == halt


def test_machine_left_growth():
    """Machine should extend tape to the left when head moves past left edge."""
    zero, one = TapeVar(0), TapeVar(1)
    q0 = State("q0", {})
    halt = State("HALT", {})
    q0.transitions = {zero: (halt, one, Action.L)}
    tm = StateMachine(start=q0, input_tape=[zero], start_point=0, verbose=False)

    tm.step()
    assert tm.tape[0] == BLANK
    assert len(tm.tape) == 2


def test_machine_respects_start_point():
    """Machine should start reading from the user-specified start_point."""
    tape = [TapeVar(0), TapeVar(1), TapeVar(0)]
    q0 = State("q0", {})
    halt = State("HALT", {})
    q0.transitions = {TapeVar(1): (halt, TapeVar(0), Action.N)}

    tm = StateMachine(start=q0, input_tape=tape, start_point=1, verbose=False)
    tm.step()
    # head was at tape[1], wrote 0 there
    assert tm.tape[1].notation == 0


def test_machine_halts_properly():
    """Machine should halt when update() returns None as next state."""
    zero = TapeVar(0)
    q0 = State("q0", {})
    tm = StateMachine(start=q0, input_tape=[zero], start_point=0, verbose=False)
    result = tm.step()
    assert result is False
    assert tm.current is None


def test_custom_action_with_large_move():
    """Machine should handle arbitrary custom head displacements safely."""
    zero, one = TapeVar(0), TapeVar(1)
    R3 = ActionPrimitive("R3", lambda h: h + 3)
    q0 = State("q0", {})
    halt = State("HALT", {})
    q0.transitions = {zero: (halt, one, R3)}
    tape = [zero]
    tm = StateMachine(start=q0, input_tape=tape, start_point=0, verbose=False)
    tm.step()
    assert len(tm.tape) >= 4
