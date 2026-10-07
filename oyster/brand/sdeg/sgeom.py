"""Geometry of the wordmark's s (Newsreader 500, as outlined in oyster-logotype-nacre.svg): its outline as a
polygon, a distance field and the spine's centreline. Glyph units, y up, as in the export's path."""
import os, re, math
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)) + '/'
LOGO = D + '../oyster-logotype-nacre.svg'

def s_path():
    h = open(LOGO).read()
    return re.findall(r'<path d="([^"]*)" transform="translate\([^)]*\) scale\(0\.5000 -0\.5000\)"', h)[1]

def polygon(d, n=10):
    toks = re.findall(r'[MLQHVZ]|-?\d+\.?\d*', d); i = 0; cmd = None; pts = []; cur = (0, 0)
    while i < len(toks):
        t = toks[i]
        if t in 'MLQHVZ': cmd = t; i += 1
        if cmd == 'Z': continue
        f = lambda k: float(toks[i + k])
        if cmd in 'ML': cur = (f(0), f(1)); pts.append(cur); i += 2
        elif cmd == 'H': cur = (f(0), cur[1]); pts.append(cur); i += 1
        elif cmd == 'V': cur = (cur[0], f(0)); pts.append(cur); i += 1
        elif cmd == 'Q':
            a, b = (f(0), f(1)), (f(2), f(3)); p0 = cur
            for k in range(1, n + 1):
                t_ = k / n; u = 1 - t_
                pts.append((u*u*p0[0] + 2*u*t_*a[0] + t_*t_*b[0], u*u*p0[1] + 2*u*t_*a[1] + t_*t_*b[1]))
            cur = b; i += 4
    pts = np.array(pts); keep = np.r_[True, np.abs(np.diff(pts, axis=0)).sum(1) > 1e-6]
    pts = pts[keep]
    return pts[:-1] if np.abs(pts[0] - pts[-1]).sum() < 1e-6 else pts

P = polygon(s_path())

def seg_dist(q):
    """Distance from points q (N,2) to the outline."""
    a = P; b = np.roll(P, -1, 0); ab = b - a
    t = np.clip(((q[:, None, :] - a[None]) * ab[None]).sum(-1) / (ab * ab).sum(-1)[None], 0, 1)
    c = a[None] + t[..., None] * ab[None]
    return np.sqrt(((q[:, None, :] - c) ** 2).sum(-1)).min(1)

def inside(q):
    a = P; b = np.roll(P, -1, 0); x, y = q[:, 0:1], q[:, 1:2]
    cond = (a[None, :, 1] > y) != (b[None, :, 1] > y)
    xi = a[None, :, 0] + (y - a[None, :, 1]) * (b[None, :, 0] - a[None, :, 0]) / (b[None, :, 1] - a[None, :, 1] + 1e-12)
    return ((cond & (x < xi)).sum(1) % 2) == 1

def field(step=6):
    xs = np.arange(-30, 1010, step); ys = np.arange(20, 1060, step)
    X, Y = np.meshgrid(xs, ys); q = np.stack([X.ravel(), Y.ravel()], 1).astype(float)
    ins = inside(q); d = np.zeros(len(q)); d[ins] = seg_dist(q[ins])
    return xs, ys, d.reshape(X.shape)

def ridge(step=6):
    xs, ys, d = field(step); pts = []
    for j in range(1, d.shape[0] - 1):
        for i in range(1, d.shape[1] - 1):
            v = d[j, i]
            if v < 10: continue
            for dj, di in ((0, 1), (1, 0), (1, 1), (1, -1)):
                if v >= d[j + dj, i + di] and v >= d[j - dj, i - di] and (v > d[j + dj, i + di] or v > d[j - dj, i - di]):
                    pts.append((xs[i], ys[j], v)); break
    return np.array(pts)

def spine(start=(734, 740), heading=(0.05, 1), step=10, reach=60):
    """Trace the stroke's centreline from the upper terminal round to the lower one: step forward, then slide
    sideways to the point furthest from the outline. Returns points (N,2) and half-widths (N,)."""
    p = np.array(start, float); h = np.array(heading, float); h /= np.linalg.norm(h)
    pts, ws = [p.copy()], [seg_dist(p[None])[0]]
    for _ in range(400):
        q = p + step * h; n = np.array([-h[1], h[0]])
        cand = q[None] + np.linspace(-reach, reach, 61)[:, None] * n[None]
        ins = inside(cand)
        if not ins.any(): break
        dd = np.where(ins, seg_dist(cand), -1); k = dd.argmax()
        if dd[k] < 6: break
        new = cand[k]; nh = new - p; nh /= np.linalg.norm(nh); h = .6 * h + .4 * nh; h /= np.linalg.norm(h)
        p = new; pts.append(p.copy()); ws.append(dd[k])
    return np.array(pts), np.array(ws)
