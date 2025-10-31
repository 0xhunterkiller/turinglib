# examples/example_flip.py
from turinglib.core import TapeVar, State, StateMachine, Action

def main():
    zero = TapeVar(0)
    one = TapeVar(1)
    R, N = Action.R, Action.N

    q0 = State("q0", {})
    halt = State("HALT", {})

    q0.transitions = {
        zero: (halt, one, R),
        one: (halt, one, N),
    }

    tape = [TapeVar(0)]
    tm = StateMachine(start=q0, inputTape=tape, startPoint=0, verbose=True)
    tm.run()

    print("\nFinal tape:", [cell.notation for cell in tm.tape])

if __name__ == "__main__":
    main()
