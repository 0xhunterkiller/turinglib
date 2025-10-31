# examples/example_binary_increment.py
from turinglib.core import TapeVar, State, StateMachine, Action

def main():
    zero, one = TapeVar(0), TapeVar(1)
    R, L, N = Action.R, Action.L, Action.N

    # States
    q_scan = State("SCAN_RIGHT", {})
    q_add = State("ADD_ONE", {})
    q_done = State("HALT", {})

    # Transitions:
    # Move right until blank, then go left to add 1
    q_scan.transitions = {
        zero: (q_scan, zero, R),
        one: (q_scan, one, R),
        # Found blank: move left, go to ADD_ONE
        TapeVar(0): (q_add, TapeVar(0), L),
    }

    # Perform the binary addition
    q_add.transitions = {
        zero: (q_done, one, N),     # Add 1 to 0 → done
        one: (q_add, zero, L),      # Carry: flip 1→0 and move left
    }

    # Initial tape: binary 111 (i.e. 7)
    tape = [TapeVar(1), TapeVar(1), TapeVar(1)]
    tm = StateMachine(start=q_scan, inputTape=tape, startPoint=0, verbose=True)
    tm.run(max_steps=50)

    print("\nFinal tape:", [t.notation for t in tm.tape])

if __name__ == "__main__":
    main()
