from typing import Callable, Optional
from enum import Enum

class TapeVar():
    """
    the tape variable, like, 0 or 1 (notation: 0 or 1)
    """
    __slots__ = ("notation",)

    def __init__(self, notation: Optional[int]):
        self.notation = notation

    def __repr__(self):
        return "_" if self.notation is None else str(self.notation)
    
    def __eq__(self, other):
        return isinstance(other, TapeVar) and self.notation == other.notation

    def __hash__(self):
        return hash(self.notation)

BLANK = TapeVar(None)

class ActionPrimitive():
    """
    the action to perform on the head, like R or L

    args:
    * notation: how you want to notate the state, like R, or L
    * op: what is the action you want to perform on the head (+1 for R, -1 for L)
    """
    def __init__(self, notation: str, op: Callable[[int], int]):
        self.notation = notation
        self.op = op
    
    def __repr__(self):
        return str(self.notation)
    
    def perform(self, head):
        return self.op(head)

class Action(Enum):
    R = ActionPrimitive("R", lambda h: h + 1)
    L = ActionPrimitive("L", lambda h: h - 1)
    N = ActionPrimitive("N", lambda h: h)

class State():
    """
    a state in the state machine
    
    args: 
    * notation: how you want to notate the state, like q1, or A
    * transitions: a dict specifying the the actions to perform on reading a specific TapeVar
    """
    def __init__(self, notation: str, transitions: dict[TapeVar, tuple["State", TapeVar, Action]]):
        self.notation = notation
        self.transitions = transitions
    
    def __repr__(self):
        return str(self.notation)
    
    def update(self, tv:TapeVar, head: int, implicit_blank_halt: bool) -> tuple["State | None", TapeVar, int]:
        if implicit_blank_halt and tv == BLANK and BLANK not in self.transitions:
            return None, tv, head
        result = self.transitions.get(tv, None)
        if result is None:
            return None, tv, head
        nextState, newtv, action = result
        return nextState, newtv, action.value.perform(head)
    

class StateMachine():
    def __init__(self, start: State, inputTape: list[TapeVar], startPoint: int, verbose: bool = True, implicit_blank_halt: bool = True):
        assert 0 <= startPoint < len(inputTape)
        assert isinstance(inputTape[startPoint], TapeVar)
        self.start = start
        self.tape = inputTape
        self.implicit_blank_halt = implicit_blank_halt
        self.verbose = verbose

        # managed by the TM
        self.current = start
        self.head = startPoint
    
    def __str__(self):
        return f"State={self.current}, Head={self.head}, TapeValue={self.tape[self.head]}"

    def step(self):
        # Read the current 
        tape_value = self.tape[self.head]
        nextState, newtv, newhead = self.current.update(tape_value, self.head, self.implicit_blank_halt)

        if nextState is None:
            print("========== Machine has Halted : DUE TO NO TRANSITION AVAILABLE ==========")
            self.current = None
            print(self)
            return False
        
        self.current = nextState

        if newhead < 0:
            self.tape.insert(0, newtv)
            newhead = 0

        elif newhead >= len(self.tape):
            if len(self.tape) > 10**6:
                raise MemoryError("Tape exceeded safe length")
            self.tape.append(newtv)

        self.tape[self.head] = newtv
        self.head = newhead

        if self.verbose:
            print(self)
        return True
    
    def run(self, max_steps: int = 1000):
        for _ in range(max_steps):
            if not self.step():
                break
        print(f"Machine halted after {_+1} steps.")
    
if __name__ == "__main__":
    print("=== Turing Machine Demo ===")

    # Define tape symbols
    zero = TapeVar(0)
    one = TapeVar(1)

    # Define actions
    R, L, N = Action.R, Action.L, Action.N

    # Define states
    q0 = State("q0", {})
    halt = State("HALT", {})

    # Define transitions
    # In state q0:
    #   - If tape reads 0 → write 1, move right, go to HALT
    #   - If tape reads 1 → do nothing (N), go to HALT
    q0.transitions = {
        zero: (halt, one, R),
        one: (halt, one, N),
    }

    # Build initial tape (single 0)
    tape = [TapeVar(0)]

    # Create the machine
    tm = StateMachine(start=q0, inputTape=tape, startPoint=0, verbose=True)

    print("\n--- Initial Configuration ---")
    print(f"State={tm.current}, Head={tm.head}, Tape={tm.tape}")

    # Run until halt
    tm.run()

    print("\n--- Final Configuration ---")
    print(f"State={tm.current}, Head={tm.head}")
    print("Final Tape:", [cell.notation for cell in tm.tape])
    print("=== End of Simulation ===")