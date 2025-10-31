# turinglib

`turinglib` is a lightweight Python library for building, simulating, and experimenting with **Turing Machines** — the foundational model of computation.

It provides an object-oriented interface for defining tape symbols, actions, states, and state machines, allowing you to express theoretical computation models in a clear and testable way.

---

## Features

* Deterministic single-tape Turing Machine simulation
* Explicit classes for `TapeVar`, `Action`, `State`, and `StateMachine`
* Supports symbol rewriting, head movement, and transition definitions
* Built-in halting for tape overflow and undefined transitions
* Minimal design, intended for experimentation and research

---

## Installation

```bash
pip install turinglib
```

Or from source:

```bash
git clone https://github.com/0xhunterkiller/turinglib.git
cd turinglib
pip install -e .
```

---

## Example: Flip a Bit

A minimal machine that reads a single cell and:

* If the cell contains `0`, writes `1` and moves right.
* If the cell contains `1`, halts.

```python
from turinglib.core import TapeVar, Action, State, StateMachine

zero = TapeVar(0)
one = TapeVar(1)

R = Action("R", lambda x: x + 1)
N = Action("N", lambda x: x)

q0 = State("q0", {})
halt = State("HALT", {})

q0.transitions = {
    zero: (halt, one, R),
    one: (halt, one, N)
}

tape = [TapeVar(0)]
tm = StateMachine(start=q0, inputTape=tape, startPoint=0)

tm.step()
print("Final tape:", [cell.notation for cell in tm.tape])
```

Output:

```
State=HALT, Head=1, TapeValue=0
Final tape: [1]
```

---

## API Overview

### TapeVar

Represents a single symbol on the tape.

```python
TapeVar(0)
TapeVar(1)
```

Symbols are comparable and hashable, making them usable as dictionary keys.

---

### Action

Encapsulates a movement operation for the machine head.

```python
Action("R", lambda x: x + 1)  # move right
Action("L", lambda x: x - 1)  # move left
Action("N", lambda x: x)      # no movement
```

---

### State

Represents a machine state and its transitions.

```python
transitions = {
    TapeVar(0): (next_state, TapeVar(1), R)
}
State("q0", transitions)
```

Each transition maps:

```
δ(current_state, tape_symbol) → (next_state, new_symbol, action)
```

---

### StateMachine

Controls execution and manages the tape.

```python
machine = StateMachine(start_state, input_tape, start_point)
machine.step()  # one step
machine.run()   # run until halt
```

Halts when:

* The head moves outside the tape boundary, or
* No transition is defined for the current symbol.

---

## Example: Invert all Bits

```python
from turinglib.core import TapeVar, Action, State, StateMachine

zero, one = TapeVar(0), TapeVar(1)
R = Action("R", lambda x: x + 1)
N = Action("N", lambda x: x)

q0 = State("q0", {})
halt = State("HALT", {})

q0.transitions = {
    zero: (q0, one, R),
    one: (q0, zero, R)
}

tape = [TapeVar(0), TapeVar(1), TapeVar(1), TapeVar(0)]
tm = StateMachine(q0, tape, 0)

tm.run()
print("Final tape:", [t.notation for t in tm.tape])
```

Output:

```
State=HALT, Head=4, TapeValue=0
Final tape: [1, 0, 0, 1]
```

---

## Directory Structure

```
turinglib/
├── __init__.py
├── core.py
├── actions.py
├── examples/
│   ├── flip_bit.py
│   └── invert_all.py
└── tests/
    └── test_core.py
```

---

## Future Extensions

* Multi-tape and multi-head machines
* Nondeterministic transitions
* Step-by-step debugger or visualizer
* JSON or DOT format for exporting transition graphs
* Integration with formal language or automata simulators

---

## Reference

    The Turing Machine is not a computer — it’s the idea of computation.

    — Alan Turing (1936)
