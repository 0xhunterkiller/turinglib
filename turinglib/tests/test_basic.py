# turinglib/tests/test_basic.py
from turinglib.core import TapeVar, State, StateMachine
from turinglib.actions import R, N

def test_flip_bit():
    zero, one = TapeVar(0), TapeVar(1)
    q0, halt = State("q0", {}), State("HALT", {})
    q0.transitions = {zero: (halt, one, R), one: (halt, zero, N)}
    tape = [TapeVar(0)]
    tm = StateMachine(q0, tape, 0)
    tm.run()
    assert tm.tape[0].notation == 1
