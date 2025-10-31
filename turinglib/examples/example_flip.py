"""
example_flip.py

Demonstrates a simple Turing Machine that flips all bits (0 → 1, 1 → 0)
on the input tape, then halts at the rightmost blank cell.
"""

from turinglib import TapeVar, State, StateMachine, Action, BLANK

# Define symbols
zero, one = TapeVar(0), TapeVar(1)
R = Action.R

# Define states
q0 = State("q0", {})
halt = State("HALT", {})

# Transitions for q0
q0.transitions = {
    zero: (q0, one, R),
    one: (q0, zero, R),
    BLANK: (halt, BLANK, R),
}

# Input tape
tape = [TapeVar(0), TapeVar(1), TapeVar(1), TapeVar(0)]

tm = StateMachine(start=q0, input_tape=tape, start_point=0, verbose=True)
print("\n--- Starting Bit-Flip Machine ---")
tm.run()
print("Final Tape:", [cell.notation for cell in tm.tape])
