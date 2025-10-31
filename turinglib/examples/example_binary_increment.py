"""
example_binary_increment.py

Adds 1 to a binary number stored on the tape.
Example: 1011 → 1100
"""

from turinglib import TapeVar, State, StateMachine, Action, BLANK

zero, one = TapeVar(0), TapeVar(1)
R, L, N = Action.R, Action.L, Action.N

# States
move_right = State("MOVE_RIGHT", {})
add = State("ADD", {})
carry = State("CARRY", {})
halt = State("HALT", {})

# Move to end of number
move_right.transitions = {
    zero: (move_right, zero, R),
    one: (move_right, one, R),
    BLANK: (add, BLANK, L),
}

# Perform addition
add.transitions = {
    zero: (halt, one, N),      # 0 → 1, halt
    one: (carry, zero, L),     # 1 → 0, carry left
    BLANK: (halt, one, N),     # overflow → new 1
}

# Propagate carry
carry.transitions = {
    one: (carry, zero, L),
    zero: (halt, one, N),
    BLANK: (halt, one, N),
}

tape = [one, zero, one, one]
tm = StateMachine(start=move_right, input_tape=tape, start_point=0, verbose=True)
print("\n--- Binary Increment Machine ---")
tm.run()
print("Final Tape:", [cell.notation for cell in tm.tape])
