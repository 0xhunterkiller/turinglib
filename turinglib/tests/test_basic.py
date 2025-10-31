# tests/test_basic.py
import pytest
from turinglib.core import TapeVar, State, StateMachine, Action, BLANK


def test_single_step_transition():
    zero, one = TapeVar(0), TapeVar(1)
    R = Action.R

    q0 = State("q0", {})
    halt = State("HALT", {})

    # On reading 0 → write 1, move right, go to HALT
    q0.transitions = {zero: (halt, one, R)}

    tape = [zero]
    tm = StateMachine(start=q0, inputTape=tape, startPoint=0, verbose=False)

    tm.step()

    assert tm.tape[0].notation == 1
    assert tm.head == 1
    assert tm.current == halt


def test_halts_on_no_transition():
    zero = TapeVar(0)
    q0 = State("q0", {})
    tm = StateMachine(start=q0, inputTape=[zero], startPoint=0, verbose=False)
    
    # Should halt immediately (no transition defined)
    result = tm.step()
    assert result is False
    assert tm.current is None


def test_dynamic_tape_growth_right():
    zero, one = TapeVar(0), TapeVar(1)
    R = Action.R

    q0 = State("q0", {})
    halt = State("HALT", {})

    q0.transitions = {zero: (halt, one, R)}

    tape = [zero]
    tm = StateMachine(start=q0, inputTape=tape, startPoint=0, verbose=False)
    tm.step()

    # Tape should extend with a blank cell
    assert len(tm.tape) == 2
    assert tm.tape[1] == BLANK


def test_dynamic_tape_growth_left():
    zero, one = TapeVar(0), TapeVar(1)
    L = Action.L

    q0 = State("q0", {})
    halt = State("HALT", {})

    q0.transitions = {zero: (halt, one, L)}

    tape = [zero]
    tm = StateMachine(start=q0, inputTape=tape, startPoint=0, verbose=False)
    tm.step()

    # Tape should grow left with a blank
    assert len(tm.tape) == 2
    assert tm.tape[0] == BLANK
