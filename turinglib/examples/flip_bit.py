# turinglib/examples/flip_bit.py
from turinglib.core import TapeVar, State, StateMachine
from turinglib.actions import R, N

# symbols
zero = TapeVar(0)
one = TapeVar(1)

# states
q0 = State("q0", {})
halt = State("HALT", {})

# transitions
q0.transitions = {
    zero: (halt, one, R),
    one: (halt, zero, N)
}

# build machine
tape = [TapeVar(0)]
tm = StateMachine(start=q0, input_tape=tape, start_point=0)
tm.run()
print("Final tape:", [cell.notation for cell in tm.tape])
