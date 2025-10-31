# turinglib/__init__.py

"""
turinglib — a minimal Turing Machine simulation library.

Exports:
    - TapeVar, BLANK: Tape symbol primitives
    - Action, ActionPrimitive: Head movement actions
    - State: State transition definition
    - StateMachine: Machine execution engine
"""

from .core import TapeVar, State, StateMachine, Action, ActionPrimitive, BLANK

__all__ = [
    "TapeVar",
    "State",
    "StateMachine",
    "Action",
    "ActionPrimitive",
    "BLANK",
]