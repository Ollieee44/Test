"""The person for Rob's edits: a side-view body silhouette (facing right, y down, as the journey draws it), head to
mid-thigh, as smooth curves through anatomical landmarks. Keeps the journey's anchors: the lips at (18.6, -44.4), where the
capsule goes in; the neck around x 1.5, where it goes down; the gut inset centred on (0, 25).
profile() -> (filled outline, open edge, '' (no arm))"""


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


# the outline of the reference Rob supplied (a side-view body, facing left, 234 x 643 px), traced from the image's own
# pixels (the drawn line filled to a body and contoured, simplified to 0.9 px), open along the bottom; mirrored to face
# right and scaled so its mouth (29.5, 112) lands on the journey's lips (18.6, -44.4)
REF = [(43.5, 591.0), (44.5, 590.0), (44.5, 573.0), (46.5, 557.0), (36.5, 529.0), (23.5, 475.0), (23.5, 462.0), (27.5, 433.0), (21.5, 392.0), (19.5, 367.0), (14.5, 346.0), (13.5, 336.0), (15.5, 310.0), (19.5, 293.0), (24.5, 281.0), (24.5, 275.0), (21.5, 268.0), (21.5, 261.0), (27.5, 248.0), (39.5, 229.0), (62.5, 202.0), (65.5, 194.0), (75.5, 187.0), (78.5, 182.0), (78.5, 179.0), (68.5, 165.0), (65.5, 158.0), (65.5, 153.0), (60.0, 146.5), (43.0, 146.5), (38.0, 144.5), (33.5, 140.0), (31.5, 135.0), (32.5, 123.0), (29.5, 120.0), (28.5, 111.0), (30.5, 103.0), (22.5, 99.0), (21.5, 91.0), (34.5, 71.0), (32.5, 65.0), (35.5, 47.0), (44.5, 29.0), (56.0, 17.5), (63.0, 12.5), (73.0, 7.5), (93.0, 2.5), (112.0, 2.5), (133.0, 7.5), (145.0, 14.5), (153.5, 23.0), (159.5, 33.0), (163.5, 50.0), (162.5, 69.0), (157.5, 88.0), (146.5, 107.0), (147.5, 122.0), (154.5, 146.0), (162.5, 163.0), (180.5, 180.0), (190.5, 194.0), (197.5, 208.0), (205.5, 231.0), (204.5, 257.0), (203.5, 258.0), (204.5, 281.0), (201.5, 297.0), (195.5, 315.0), (194.5, 327.0), (190.5, 344.0), (187.5, 354.0), (178.5, 374.0), (168.5, 390.0), (156.5, 404.0), (154.5, 415.0), (154.5, 457.0), (170.5, 480.0), (186.5, 510.0), (192.5, 530.0), (194.5, 542.0), (193.5, 560.0), (188.5, 578.0), (178.5, 598.0), (171.5, 608.0)]
_S = .33
_MAP = lambda pts: [(18.6 + (29.5 - x) * _S, -44.4 + (y - 112) * _S) for x, y in pts]


def profile():
    pts = _MAP(REF)
    return _smooth(pts, closed=True), _smooth(pts, closed=False), ''
