# **TuringLib: A Minimal Turing Machine Simulation Library**

**Version:** 0.1.0
**Author:** Saai Sudarsanan
**License:** MIT
**Python:** ≥ 3.11

---

## INSTALLATION

### From PyPI (once published)

```
pip install turinglib
```

### From source (for development or experimentation)

```
git clone https://github.com/0xhunterkiller/turinglib.git
cd turinglib
pip install -e .[dev]
```

### Using uv

```
uv add git+https://github.com/0xhunterkiller/turinglib.git
```

## 1. Overview

`turinglib` is a minimal, mathematically faithful implementation of a **deterministic Turing Machine** in Python.
It is designed for theoretical clarity, educational use, and extensibility — not for high-performance simulation.

At its core, `turinglib` models a Turing Machine as a **7-tuple**:

[
M = (Q, \Gamma, b, \Sigma, \delta, q_0, F)
]

where:

* **Q** – finite set of states
* **Γ** – tape alphabet (symbols that can appear on the tape)
* **b** – blank symbol (`BLANK`)
* **Σ** – input alphabet (subset of Γ not containing b)
* **δ** – transition function: ( Q \times Γ \to Q \times Γ \times D )
* **q₀** – initial state
* **F** – halting state(s)

`turinglib` implements this structure as composable Python classes, retaining 1:1 correspondence with the mathematical formalism.

---

## 2. Conceptual Design

`turinglib`’s internal design emphasizes **transparency and explicitness**.
Every concept in the Turing Machine model maps directly to a class:

| Theoretical Element       | Implementation Class        | Description                                                 |
| ------------------------- | --------------------------- | ----------------------------------------------------------- |
| Tape alphabet symbol (Γ)  | `TapeVar`                   | Represents a single immutable tape cell value.              |
| Blank symbol (⊔)          | `BLANK`                     | Canonical instance of `TapeVar(None)`.                      |
| Head movement actions (D) | `Action`, `ActionPrimitive` | Discrete or arbitrary head movement primitives.             |
| States (Q)                | `State`                     | Encapsulates transitions and behavior of one TM state.      |
| Transition function (δ)   | `State.update()`            | Computes next configuration based on current symbol.        |
| Machine execution         | `StateMachine`              | Orchestrates tape growth, head movement, and state updates. |

This alignment ensures the implementation remains **provably consistent** with the underlying formal model.

---

## 3. Core Components

### 3.1. `TapeVar`

Represents a single symbol on the Turing Machine’s tape.

#### Definition

```python
class TapeVar:
    def __init__(self, notation: Optional[str | int]):
        ...
```

#### Key Properties

* **Immutable** – once constructed, its value cannot be changed.
* **Hashable** – usable as keys in transition dictionaries.
* **Blank Symbol** – represented internally by `None`, rendered as `'_'`.

#### Attributes

| Attribute  | Type   | Description                           |       |                                      |
| ---------- | ------ | ------------------------------------- | ----- | ------------------------------------ |
| `notation` | `str   | int                                   | None` | The symbol stored in this tape cell. |
| `is_blank` | `bool` | True if the symbol is blank (`None`). |       |                                      |

#### Global Constant

```python
BLANK = TapeVar(None)
```

The canonical blank tape symbol (⊔).
Equivalent to `TapeVar(None)`, but shared across the system.

---

### 3.2. `ActionPrimitive`

Encapsulates a single head movement operation on the tape.

#### Definition

```python
class ActionPrimitive:
    def __init__(self, notation: str, op: Callable[[int], int]):
        ...
```

#### Purpose

* Defines how the tape head moves after a transition.
* The `op` function takes the current head coordinate (integer) and returns the new coordinate.

#### Attributes

| Attribute  | Type                   | Description                                        |
| ---------- | ---------------------- | -------------------------------------------------- |
| `notation` | `str`                  | Human-readable label (e.g., `"R"`, `"L"`, `"R2"`). |
| `op`       | `Callable[[int], int]` | Movement function over integer coordinates.        |

#### Methods

| Method                      | Description                                                  |
| --------------------------- | ------------------------------------------------------------ |
| `perform(head: int) -> int` | Applies the movement operation to the given head coordinate. |

`ActionPrimitive` is the fundamental building block for both built-in and custom head actions.

---

### 3.3. `Action` Enum

Defines the canonical head movement set {L, R, N}:

[
D = { L, R, N }
]

#### Definition

```python
class Action(Enum):
    R = ActionPrimitive("R", lambda h: h + 1)
    L = ActionPrimitive("L", lambda h: h - 1)
    N = ActionPrimitive("N", lambda h: h)
```

#### Members

| Member     | Meaning     | Movement |
| ---------- | ----------- | -------- |
| `Action.R` | Move Right  | +1       |
| `Action.L` | Move Left   | −1       |
| `Action.N` | No movement | 0        |

#### Extensibility

Users may define custom `ActionPrimitive`s (e.g., move two steps right, jump to index 10, etc.)
Custom primitives are treated equivalently to `Action` members via type unification.

---

### 3.4. `State`

Represents one state in the machine, including its transition map.

#### Definition

```python
class State:
    def __init__(self, notation: str,
                 transitions: dict[TapeVar, tuple["State", TapeVar, Union[Action, ActionPrimitive]]]):
        ...
```

#### Attributes

| Attribute     | Type   | Description                                  |
| ------------- | ------ | -------------------------------------------- |
| `notation`    | `str`  | Label for the state (e.g. `"q0"`, `"HALT"`). |
| `transitions` | `dict` | Transition mapping per tape symbol.          |

#### Transition Rule

Each entry defines one δ(q, a) → (q′, b, D) rule:

```
current_symbol : (next_state, symbol_to_write, head_action)
```

#### Method

```python
def update(self, tv: TapeVar, head: int, implicit_blank_halt: bool)
        -> tuple[State | None, TapeVar, int]
```

**Behavior:**

* Reads the current symbol (`tv`).
* Looks up a transition rule in `self.transitions`.
* Returns the tuple (next_state, symbol_to_write, new_head).
* If no transition is defined, returns `(None, tv, head)` — indicating a halt.

**Blank Halting Behavior:**
If `implicit_blank_halt=True` and a blank symbol has no defined transition, the machine halts automatically.

---

### 3.5. `StateMachine`

Coordinates the entire machine’s execution — tape, head, and transitions.

#### Definition

```python
class StateMachine:
    def __init__(self,
                 start: State,
                 input_tape: list[TapeVar],
                 start_point: int,
                 verbose: bool = True,
                 implicit_blank_halt: bool = True):
        ...
```

#### Conceptual Model

The `StateMachine` represents the evolving configuration
((q, T, h)) of the machine, where:

* `q` is the current state,
* `T` is the tape (finite view of Γ*),
* `h` is the integer head coordinate.

The mapping between tape indices and logical coordinates is:

[
index = head - tape_begin
]

where `tape_begin` marks the coordinate of `tape[0]`.

This allows unbounded growth both left and right.

#### Attributes

| Attribute    | Type            | Description                                 |
| ------------ | --------------- | ------------------------------------------- |
| `current`    | `State`         | Current active state.                       |
| `head`       | `int`           | Logical head position on the infinite tape. |
| `tape_begin` | `int`           | Coordinate corresponding to `tape[0]`.      |
| `tape`       | `list[TapeVar]` | The mutable portion of the tape.            |

#### Methods

| Method                       | Description                                          |
| ---------------------------- | ---------------------------------------------------- |
| `step() -> bool`             | Executes one δ transition. Returns False if halting. |
| `run(max_steps: int = 1000)` | Repeatedly calls `step()` until halt or step limit.  |

---

## 4. Execution Semantics

The machine operates according to the **standard TM step sequence**:

1. **Read** the symbol under the head.
2. **Look up** δ(q, a) in the transition map.
3. **Write** the new symbol.
4. **Move** the head according to D (ActionPrimitive).
5. **Change** to the next state q′.
6. **Repeat** until no transition exists (halting).

#### Tape Extension

The tape is automatically extended with `BLANK` symbols when:

* The head moves beyond the rightmost known cell (append).
* The head moves left of the leftmost known cell (insert at index 0).

#### Coordinate Invariants

At all times:

[
0 \le (head - tape_begin) < len(tape)
]

ensuring valid tape access even with arbitrary head movements.

---

## 5. Halting Behavior

A machine halts in either of two conditions:

1. **No transition defined** for the current symbol in the current state.
2. **Implicit blank halt** — enabled when `implicit_blank_halt=True` and the machine reads a blank symbol with no defined rule.

Upon halting:

* The current state is set to `None`.
* The tape remains in its final configuration.

---

## 6. Extensibility

`turinglib` deliberately exposes composable primitives to encourage experimentation.

| Extension Type             | Mechanism                                                        |
| -------------------------- | ---------------------------------------------------------------- |
| Custom head movement       | Define new `ActionPrimitive` with arbitrary integer shifts.      |
| Non-binary tape symbols    | Use `TapeVar("A")`, `TapeVar("B")`, etc.                         |
| Multi-tape or NTM variants | Can be built externally using multiple `StateMachine` instances. |
| Custom halt policies       | Override `State.update()` or wrap `step()`.                      |

Because all classes are lightweight and self-contained, `turinglib` can serve as a **foundation for experimental computation theory tools** — from universal machine simulation to symbolic reasoning frameworks.

---

## 7. Design Principles

`turinglib` follows three guiding principles:

1. **Faithful abstraction:**
   Each class maps to a single formal component in the TM model.

2. **Deterministic transparency:**
   No implicit randomness or side effects; every transition is explicit.

3. **Compositional simplicity:**
   The implementation is minimal yet flexible enough to represent any deterministic Turing Machine.

---

## 8. Error Handling & Safety

| Condition                              | Behavior                                                            |
| -------------------------------------- | ------------------------------------------------------------------- |
| Undefined transition                   | Machine halts cleanly.                                              |
| Out-of-bounds head                     | Automatically extends tape.                                         |
| Excessive tape growth (>10⁶ cells)     | Raises `MemoryError`.                                               |
| Mutation of `TapeVar`                  | Raises `AttributeError`.                                            |
| Invalid transition key (non-`TapeVar`) | Undefined behavior — users are expected to follow the API contract. |

---

## 9. Typing & Versioning

* **Typing:** Python 3.11+ structural typing with `|` unions and forward annotations.
* **Static Type Safety:** All functions type-checked via `mypy>=1.10`.
* **Versioning:** Semantic Versioning (MAJOR.MINOR.PATCH).

---

## 10. Philosophical Note

`turinglib` was designed not as a programming toy, but as a **precise and observable embodiment** of the mathematical idea of computation.
Every operation in the system has a formal meaning; nothing “hides” under abstractions.

The library’s simplicity invites reflection on the nature of computation itself:

* What can be known about a system from within the system?
* How does observability constrain prediction?
* What happens when the model itself becomes part of what it models?

These are not engineering questions — they are epistemological ones.
`turinglib` exists at that boundary.

---

### © 2025 Saai Sudarsanan — MIT License

*A minimal library for maximal thought.*

---