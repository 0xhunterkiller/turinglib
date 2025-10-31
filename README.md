# turinglib

`turinglib` is a lightweight Python library for constructing and simulating **Turing Machines** — the foundational model of computation.

It provides an object-oriented framework for defining tape symbols, actions, states, and transition systems, enabling experimentation with the mechanics of formal computation.

---

## Overview

A Turing Machine is an abstract computational model consisting of:

* A **tape** divided into cells that can hold symbols.
* A **head** that reads and writes symbols and moves left or right.
* A **finite set of states**, each with defined **transitions** determining how the machine evolves.

`turinglib` models these components explicitly, allowing you to define deterministic single-tape machines with clear semantics.

---

## Features

* Deterministic single-tape simulation
* Dynamic, unbounded tape growth
* Explicit modeling of `TapeVar`, `Action`, `State`, and `StateMachine`
* Symbol rewriting and head movement primitives
* Automatic halting when no valid transition exists
* Configurable verbosity for tracing execution

---

## Core Concepts

### TapeVar

Represents a single symbol on the tape.
Symbols are comparable, hashable, and suitable as dictionary keys in transition maps.

### ActionPrimitive

Encapsulates a **low-level movement operation** for the tape head.
Each `ActionPrimitive` stores both its symbolic name and the function used to update the head position.

```python
ActionPrimitive(notation: str, op: Callable[[int], int])
```

**Attributes**

* `notation` — the label for the action (e.g., `"R"`, `"L"`, `"N"`)
* `op` — a callable defining how the head index changes

Each member’s `.value` is an `ActionPrimitive`.

**Methods**

* `perform(head: int) -> int` — applies the operation and returns the new head position

`ActionPrimitive` instances are wrapped by the `Action` enum for common movement patterns.

### Action

Encapsulates primitive head movements:

* `Action.R` — move right
* `Action.L` — move left
* `Action.N` — no movement

Each member’s .value is an `ActionPrimitive`.
Each action modifies the head index when executed.

### State

Represents a named machine state and its transition table.
A transition maps the pair `(state, symbol)` to `(next_state, new_symbol, action)`.

If no transition is defined for a given symbol, the machine halts.

### StateMachine

Coordinates the execution of the Turing Machine.
It maintains the tape, current state, head position, and provides the control loop (`step()` and `run()`).

The tape expands dynamically to both directions when the head moves beyond current bounds.
A safety limit prevents unbounded memory usage during runaway execution.

---

## Design Philosophy

`turinglib` emphasizes **clarity, explicitness, and theoretical correctness**.
It does not automatically inject halting conditions or blank symbols.
All state transitions, including halting behavior, must be explicitly defined by the user.

This approach allows:

* Full control over machine behavior, including blank-aware transitions.
* Faithfulness to the formal Turing Machine model.
* Flexibility to build higher-level abstractions or educational tools on top.

---

## Directory Structure

```
turinglib/
├── __init__.py
├── core.py          # main implementation
├── examples/        # usage demonstrations
│   ├── flip_bit.py
│   └── invert_all.py
└── tests/           # pytest-based validation
    └── test_core.py
```

---

## Future Work

* Multi-tape and multi-head machine support
* Nondeterministic transition modeling
* Integration with automata and formal language simulators
* Visual step-through debugger
* Export of transition graphs (DOT / JSON)

---

## Reference

    The Turing Machine is not a computer — it is the idea of computation.
    - Alan Turing (1936)
