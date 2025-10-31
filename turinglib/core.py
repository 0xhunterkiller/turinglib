from __future__ import annotations
from typing import Callable, Optional
from enum import Enum

class TapeVar():
    """
    Represents a single immutable symbol on the Turing Machine's tape.

    A TapeVar corresponds to one element of the tape alphabet Γ.
    The blank symbol is represented internally by ``None`` and displayed as ``_``.

    Attributes
    ----------
    notation : Optional[str | int]
        The stored symbol. Can be a string or integer, or ``None`` for blank.
    is_blank : bool
        True if the symbol is blank (``None``).

    Notes
    -----
    TapeVar objects are immutable, hashable, and comparable by value.
    They can be safely used as dictionary keys in state transition tables.

    Examples
    --------
    >>> zero = TapeVar(0)
    >>> blank = TapeVar(None)
    >>> print(zero, blank)
    0 _
    >>> zero == TapeVar(0)
    True
    >>> blank.is_blank
    True
    """

    __slots__ = ("_notation",)

    def __init__(self, notation: Optional[str | int]):
        object.__setattr__(self, "_notation", notation)
    
    @property
    def notation(self):
        """Return the stored symbol (or None if blank)."""
        return self._notation
    
    @property
    def is_blank(self) -> bool:
        """True if this symbol represents a blank cell."""
        return self.notation is None

    def __setattr__(self, *_):
        """Prevent reassignment after initialization."""
        raise AttributeError("TapeVar is immutable")

    def __repr__(self):
        """Return '_' for blank, or the symbol itself as a string."""
        return "_" if self.notation is None else str(self.notation)
    
    def __eq__(self, other):
        """Compare two TapeVar objects for symbol equality."""
        return isinstance(other, TapeVar) and self.notation == other.notation

    def __hash__(self):
        """Compute a hash based on the symbol value."""
        return hash(self.notation)

BLANK = TapeVar(None)
""" 
The blank tape symbol (⊔) used by the Turing Machine.

The canonical blank symbol used by the Turing Machine.

Equivalent to `TapeVar(None)`, but provided as a shared constant
for convenience and identity clarity.

Represents an empty cell on the tape.
Internally, this is a `TapeVar` with `notation=None`, 
and it prints as an underscore ('_').

Notes
-----
In formal Turing Machine notation, the blank symbol is part of the tape alphabet Γ.
It is distinct from all input symbols and usually appears on all unused tape cells.

Examples
--------
>>> BLANK
_
>>> BLANK.is_blank
True
"""

class ActionPrimitive():
    """
    Represents a primitive head movement operation on the Turing Machine tape.

    Each ActionPrimitive defines how the tape head moves after reading
    and writing a symbol — for example, move right (R), move left (L),
    or stay in place (N).

    Parameters
    ----------
    notation : str
        A short label for the action (usually 'R', 'L', or 'N').
    op : Callable[[int], int]
        A function that takes the current head index and returns
        the new head position.

    Examples
    --------
    >>> right = ActionPrimitive("R", lambda h: h + 1)
    >>> right.perform(3)
    4
    """

    def __init__(self, notation: str, op: Callable[[int], int]):
        self.notation = notation
        self.op = op
    
    def __repr__(self):
        """Return the action notation (e.g. 'R', 'L', or 'N')."""
        return str(self.notation)
    
    def perform(self, head):
        """Apply the head movement function and return the new head index."""
        return self.op(head)

class Action(Enum):
    """
    Defines the set of basic head movement actions for the Turing Machine.

    Members
    -------
    R : ActionPrimitive
        Move the head one cell to the right.
    L : ActionPrimitive
        Move the head one cell to the left.
    N : ActionPrimitive
        No movement (the head stays in place).

    Examples
    --------
    >>> Action.R.value.perform(2)
    3
    >>> Action.L.value.perform(2)
    1
    >>> Action.N.value.perform(2)
    2
    """

    R = ActionPrimitive("R", lambda h: h + 1)
    L = ActionPrimitive("L", lambda h: h - 1)
    N = ActionPrimitive("N", lambda h: h)

class State():
    """
    Represents a single state in the Turing Machine.

    Each state defines a set of transitions that determine how the machine
    reacts when reading specific tape symbols. A transition specifies:
        - the next state to move into,
        - the symbol to write on the tape,
        - and the head movement action to perform.

    Parameters
    ----------
    notation : str
        A short label identifying this state (e.g. "q0", "HALT").
    transitions : dict[TapeVar, tuple[State, TapeVar, Action]]
        A mapping from the currently read TapeVar to a tuple of:
        (next_state, symbol_to_write, head_action).

    Methods
    -------
    update(tv, head, implicit_blank_halt)
        Apply a transition based on the current tape symbol and head position.

    Notes
    -----
    If `implicit_blank_halt` is True and no transition is defined for the blank
    symbol, the machine halts when encountering a blank cell.

    Examples
    --------
    >>> zero, one = TapeVar(0), TapeVar(1)
    >>> R = Action.R
    >>> q0 = State("q0", {})
    >>> halt = State("HALT", {})
    >>> q0.transitions = {zero: (halt, one, R)}
    >>> next_state, new_symbol, new_head = q0.update(zero, 0, True)
    """


    def __init__(self, notation: str, transitions: dict[TapeVar, tuple[State, TapeVar, Action]]):
        self.notation = notation
        self.transitions = transitions
    
    def __repr__(self):
        """Return the state's notation label (e.g. 'q0' or 'HALT')."""
        return str(self.notation)
    
    def update(self, tv:TapeVar, head: int, implicit_blank_halt: bool) -> tuple[State | None, TapeVar, int]:
        """
        Determine the next machine configuration given the current tape symbol.

        Parameters
        ----------
        tv : TapeVar
            The symbol currently under the head.
        head : int
            The current head index.
        implicit_blank_halt : bool
            If True, halts when a blank cell is read without a defined transition.

        Returns
        -------
        tuple[State | None, TapeVar, int]
            (next_state, symbol_to_write, new_head_index).
            If no valid transition exists, next_state is None (machine halts).
        """
        assert all(isinstance(k, TapeVar) for k in self.transitions), "Transition keys must be TapeVar"

        if implicit_blank_halt and tv == BLANK and BLANK not in self.transitions:
            return None, tv, head
        
        result = self.transitions.get(tv)
        
        if result is None:
            return None, tv, head
        
        next_state, new_tv, action = result
        
        return next_state, new_tv, action.value.perform(head)
    
class StateMachine():
    """
    Represents a complete Turing Machine executor.

    This class manages the tape, the current head position, and state transitions
    during execution. It supports unbounded left and right tape growth and allows
    arbitrary head movements, not just ±1, enabling the definition of custom
    ActionPrimitives.

    Parameters
    ----------
    start : State
        The initial state from which execution begins.
    input_tape : list[TapeVar]
        The initial tape contents (finite portion of Γ*). The tape can expand
        automatically during execution.
    start_point : int
        The index on the input tape where the head begins. Must satisfy
        0 <= start_point < len(input_tape).
    verbose : bool, default=True
        If True, prints the tape state after each step.
    implicit_blank_halt : bool, default=True
        If True, halts automatically when encountering a blank cell without a
        defined transition.

    Attributes
    ----------
    current : State
        The current active state of the machine.
    head : int
        The logical head position on the infinite tape (coordinate system ℤ).
    tape_begin : int
        The coordinate corresponding to tape[0]. Maintains alignment between
        the mathematical tape and its list representation.

    Notes
    -----
    The mapping between logical coordinates and list indices is:

        index = head - tape_begin

    This allows correct indexing even as the tape grows in either direction.
    The machine halts when no valid transition is found for the current symbol.
    """

    def __init__(self, 
                 start: State, 
                 input_tape: list[TapeVar], 
                 start_point: int, 
                 verbose: bool = True, 
                 implicit_blank_halt: bool = True
    ):
        assert 0 <= start_point < len(input_tape)
        assert isinstance(input_tape[start_point], TapeVar)

        self.tape = input_tape
        self.implicit_blank_halt = implicit_blank_halt
        self.verbose = verbose

        # managed by the TM
        self.current = start
        self.head = start_point
        self.tape_begin = 0

    def __str__(self):
        """Return a short string summarizing the current state, head, and symbol."""
        return f"State={self.current}, Head={self.head}, TapeValue={self.tape[self.head - self.tape_begin]}"

    def step(self):
        """
        Execute a single transition step of the Turing Machine.

        Returns
        -------
        bool
            True if the machine continues execution, False if it halts.
        """

        # Read the current tape symbol
        index = self.head - self.tape_begin
        tape_value = self.tape[index]

        # Apply the transition δ(q, a) → (q', b, D)
        next_state, new_tv, new_head = self.current.update(tape_value, self.head, self.implicit_blank_halt)

        # Halt condition: no valid transition
        if next_state is None:
            if self.verbose:
                print("===== MACHINE HALTED: NO DEFINED TRANSITIONS =====")
                print(self)
            return False

        # Write new symbol b
        self.tape[index] = new_tv

        # Extend tape right if needed
        while new_head - self.tape_begin >= len(self.tape):
            if len(self.tape) > 10**6:
                raise MemoryError("tape length execeed safety limits")
            self.tape.append(BLANK)
        
        # Extend tape left if needed
        while self.tape_begin > new_head:
            if len(self.tape) > 10**6:
                raise MemoryError("tape length execeed safety limits")
            self.tape.insert(0, BLANK)
            self.tape_begin -= 1
        
        # Update head and state
        self.head = new_head
        self.current = next_state

        if self.verbose:
            print(self)

        return True
    
    def run(self, max_steps: int = 1000):
        """
        Run the Turing Machine until halt or until the step limit is reached.

        Parameters
        ----------
        max_steps : int, default=1000
            The maximum number of steps to execute before stopping.

        Returns
        -------
        tuple[list[TapeVar], State]
            The final tape and the last active state.
        """

        for _ in range(max_steps):
            if not self.step():
                break
        print(f"Machine halted after {_ + 1} steps.")
        return self.tape, self.current