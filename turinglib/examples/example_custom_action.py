"""
example_custom_action.py

Shows how to define a custom head movement action
and use it in a Turing Machine.
"""

from turinglib import TapeVar, State, StateMachine, ActionPrimitive, BLANK

# Define a custom action: move two steps right
R2 = ActionPrimitive("R2", lambda h: h + 2)

zero, one = TapeVar(0), TapeVar(1)

# States
q0 = State("q0", {})
halt = State("HALT", {})

# On reading 0, write 1 and move two steps right; else halt
q0.transitions = {
    zero: (q0, one, R2),
    one: (halt, one, R2),
    BLANK: (halt, BLANK, R2),
}

# Tape and machine
tape = [zero, zero, zero, zero, zero]
tm = StateMachine(start=q0, input_tape=tape, start_point=0, verbose=True)
print("\n--- Custom Action Machine (R2 move) ---")
tm.run(max_steps=5)
print("Final Tape:", [cell.notation for cell in tm.tape])
