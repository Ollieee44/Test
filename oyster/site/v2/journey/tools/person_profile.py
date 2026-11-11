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


# down the front from the crown, then up the back; the head is scaled a touch about the lips so it reads adult
_HEAD = lambda pts: [(18.6 + (x - 18.6) * .9, -44.4 + (y + 44.4) * .9) for x, y in pts]
FRONT = _HEAD([(-1, -80.5), (8.5, -78), (14.5, -71), (17.2, -63), (17.6, -58.6), (19.2, -55.2), (21.6, -51.4), (20.6, -49.8),
               (18.7, -49.3), (19.6, -47), (18.6, -44.4), (19.5, -42.6), (18.6, -39.6), (16.6, -36.3), (12.5, -34.8)]) + [
         (9.6, -33), (9.4, -27.5), (11.5, -22.5), (16.5, -18.5), (20.6, -12), (21.8, -4), (21.6, 5), (22.4, 13), (23.6, 22),
         (23.4, 32), (21.8, 41), (21, 51), (21.6, 63), (20.8, 77), (19.8, 90)]
BACK = [(-21.5, 90), (-23, 76), (-25.4, 62), (-25, 51), (-21.4, 41), (-18.8, 31), (-19.2, 19), (-21.6, 6), (-22.2, -6),
        (-19.6, -17), (-14.2, -25.5)] + _HEAD([(-12.6, -31), (-14.4, -37), (-18.2, -43.5), (-20.4, -54), (-19, -66), (-12.6, -76.5)])
ARM = [(-11, -18), (-3, -23.5), (6.2, -20.5), (9.4, -11), (9, 4), (7.4, 19), (7, 30), (9, 44), (8.8, 56), (9.8, 66),
       (7.6, 73.5), (3, 71), (1, 62), (-2.2, 50), (-4.6, 36), (-6.8, 24), (-9.4, 10), (-11.4, -4)]


def profile():
    body = FRONT + BACK
    filled = _smooth(body, closed=True)
    edge = _smooth(FRONT, closed=False) + ' ' + _smooth(BACK + [FRONT[0]], closed=False)
    return filled, edge, _smooth(ARM, closed=True)


if __name__ == '__main__':
    for s in profile(): print(s[:120], '...')
