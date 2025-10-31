from typing import Callable

class TapeVar():
    """
    the tape variable, like, 0 or 1 (notation: 0 or 1)
    """
    __slots__ = ("notation",)

    def __init__(self, notation: int):
        self.notation = notation

    def __repr__(self):
        return str(self.notation)
    
    def __eq__(self, other):
        return isinstance(other, TapeVar) and self.notation == other.notation

    def __hash__(self):
        return hash(self.notation)

class Action():
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
    
    def update(self, tv:TapeVar, head: int) -> tuple["State | None", TapeVar, int]:
        result = self.transitions.get(tv, None)
        if result is None:
            return None, tv, head
        nextState, newtv, action = result
        return nextState, newtv, action.perform(head)
    

class StateMachine():
    def __init__(self, start: State, inputTape: list[TapeVar], startPoint: int):
        assert 0 <= startPoint < len(inputTape)
        assert isinstance(inputTape[startPoint], TapeVar)
        self.start = start
        self.tape = inputTape

        # managed by the TM
        self.current = start
        self.head = startPoint
    
    def __str__(self):
        return f"State={self.current}, Head={self.head}, TapeValue={self.tape[self.head]}"

    def step(self):
        # Read the current 
        tape_value = self.tape[self.head]
        nextState, newtv, newhead = self.current.update(tape_value, self.head)

        if newhead < 0 or newhead >= len(self.tape):
            print("========== Machine has Halted : DUE TO TAPE ERROR ==========")
            return False

        if nextState is None:
            print("========== Machine has Halted : DUE TO NO TRANSITION AVAILABLE ==========")
            self.current = None
            return False
        
        self.current = nextState
        self.tape[self.head] = newtv
        self.head = newhead

        print(self)
        return True
    
if __name__ == "__main__":
    print("=== Turing Machine Simulation Test ===")

    # Define tape symbols
    zero = TapeVar(0)
    one = TapeVar(1)

    # Define actions (move right or left)
    R = Action("R", lambda x: x + 1)
    L = Action("L", lambda x: x - 1)
    N = Action("N", lambda x: x)  # No movement

    # Create placeholder for states (we’ll fill transitions after)
    q0 = State("q0", {})
    q1 = State("q1", {})
    halt = State("HALT", {})

    # Define transitions:
    # q0: if reads 0 → write 1, move right, go to q1
    # q0: if reads 1 → no change, no move, halt
    q0.transitions = {
        zero: (q1, one, R),
        one: (halt, one, N)
    }

    # q1 has no transitions (forces halt)
    q1.transitions = {}

    # Build the input tape and machine
    tape = [TapeVar(0), TapeVar(0), TapeVar(1)]
    machine = StateMachine(start=q0, inputTape=tape, startPoint=0)

    print("Initial:", machine)

    # Run until halt
    while machine.step():
        pass

    print("Final tape:", [cell.notation for cell in machine.tape])
    print("=== End of Simulation ===")