# turinglib/actions.py
from .core import Action

R = Action("R", lambda h: h + 1)
L = Action("L", lambda h: h - 1)
N = Action("N", lambda h: h)
