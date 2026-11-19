"""Shared number formats (wiki text uses U+2212 minus)."""
M = '\u2212'
def _s(t): return t.replace('-', M)
def I(v): return _s(f"{round(v):,}")
def SI(v): return _s(f"{round(v):+,}")
def F1(v): return _s(f"{v:.1f}")
def F2(v): return _s(f"{v:.2f}")
def F3(v): return _s(f"{v:.3f}")
def SF1(v): return _s(f"{v:+.1f}")
def SF2(v): return _s(f"{v:+.2f}")
def P1(v): return _s(f"{v:.1f}%")
def P2(v): return _s(f"{v:.2f}%")
def SP1(v): return _s(f"{v:+.1f}%")
def N(v): return f"{int(v)}"
FMTS = dict(I=I, SI=SI, F1=F1, F2=F2, F3=F3, SF1=SF1, SF2=SF2, P1=P1, P2=P2, SP1=SP1, N=N)
