"""A drawn oyster valve seen from above: an irregular teardrop, narrow at the umbo (the hinge end), with a
frilled edge and inset growth layers (the lamellae that make an oyster read as an oyster rather than a clam).
Coordinates in a 0-100 box, umbo at the top. Everything returns point lists or SVG path data."""
import math
import numpy as np

UMBO = np.array([44.0, 8.0])

def _bez(p0, p1, p2, p3, n=40):
    t = np.linspace(0, 1, n, endpoint=False)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3

# The base outline: umbo at the top, a long irregular body leaning right, broad and lopsided at the bottom.
_C = [((44, 8), (34, 10), (22, 24), (20, 42)), ((20, 42), (18, 62), (24, 86), (46, 92)),
      ((46, 92), (66, 97), (84, 84), (82, 62)), ((82, 62), (81, 44), (66, 30), (56, 18)),
      ((56, 18), (52, 13), (49, 7), (44, 8))]
BASE = np.concatenate([_bez(*map(np.array, c)) for c in _C])

def _normals(p):
    d = np.roll(p, -1, 0) - np.roll(p, 1, 0); n = np.stack([d[:, 1], -d[:, 0]], 1)
    return n / np.linalg.norm(n, axis=1, keepdims=True)

def outline(frill=1.8, waves=11, seed=0.0, base=BASE):
    """The edge pushed in and out along its normal: a few irregular lobes, quieter near the umbo."""
    p = base.copy(); n = _normals(p); k = len(p)
    t = np.arange(k) / k * 2 * math.pi
    dist = np.linalg.norm(p - UMBO, axis=1); fade = np.clip(dist / 30, 0, 1)
    wob = np.sin(waves * t + seed) + .45 * np.sin(2.3 * waves * t + 1.7 + seed) + .3 * np.sin(.5 * waves * t + .4)
    return p + n * (frill * fade * wob)[:, None]

def layer(p, s, toward=None):
    """An inset growth layer: the outline scaled by s toward a point near the umbo."""
    c = np.array(toward if toward is not None else UMBO + [0, 6])
    return c + (p - c) * s

def d(p, close=True):
    return 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in p) + (' Z' if close else '')

def transform(p, rot=0.0, about=UMBO, scale=(1, 1), move=(0, 0)):
    a = math.radians(rot); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    q = (p - about) * np.array(scale)
    return q @ R.T + about + np.array(move)
