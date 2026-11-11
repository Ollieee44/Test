"""The person for Rob's edits: a side-view body silhouette (facing right, y down, as the journey draws it), head to
mid-thigh, as smooth curves through anatomical landmarks. Keeps the journey's anchors: the lips at (18.6, -44.4), where the
capsule goes in; the neck around x 1.5, where it goes down; the gut inset centred on (0, 25).
profile() -> (filled outline, open edge, arm)"""


def _smooth(pts, closed):
    """Catmull-Rom through the points, as cubic Beziers."""
    n = len(pts); out = [f'M {pts[0][0]:.2f},{pts[0][1]:.2f}']
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f'C {c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}')
    return ' '.join(out) + (' Z' if closed else '')


# traced from the reference outline Rob supplied (facing left, 234 x 643 px), mirrored to face right and scaled so its lips
# land on the journey's (18.6, -44.4); a bald head with a short nose and the lips, a full neck with the Adam's apple, a
# deep chest, a rounded upper back, the waist and the seat; no arm
_S = .33
_MAP = lambda pts: [(18.6 + ((234 - x) - 201) * _S, -44.4 + (y - 115) * _S) for x, y in pts]
FRONT = _MAP([(100, 8), (70, 15), (50, 32), (42, 52), (38, 72), (34, 80), (22, 92), (30, 100), (28, 108), (33, 114), (28, 120),
              (36, 132), (42, 140), (56, 144), (68, 152), (72, 166), (80, 180), (72, 193), (58, 207), (40, 226), (27, 250),
              (22, 266), (19, 300), (16, 350), (20, 400), (25, 440), (31, 480), (36, 520), (44, 560)])
BACK = _MAP([(178, 560), (186, 520), (180, 488), (160, 466), (152, 440), (156, 412), (178, 392), (190, 360), (196, 320),
             (200, 270), (200, 232), (194, 205), (178, 184), (158, 152), (148, 124), (150, 100), (158, 74), (160, 46), (150, 22),
             (126, 8)])
ARM = []


def profile():
    body = FRONT + BACK
    filled = _smooth(body, closed=True)
    edge = _smooth(FRONT, closed=False) + ' ' + _smooth(BACK + [FRONT[0]], closed=False)
    return filled, edge, ''


if __name__ == '__main__':
    for s in profile(): print(s[:120], '...')
