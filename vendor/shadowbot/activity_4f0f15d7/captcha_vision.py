"""Shared, offline-only rotation matching; no browser or dataset dependencies.

Scores rank visual matches, they are not calibrated probabilities.
"""
import math

import cv2
import numpy as np


def piece_mask(piece):
    if piece is None or piece.ndim != 3 or piece.shape[2] != 4:
        return None
    # Semi-transparent drop shadows are NOT the puzzle silhouette.
    binary = (piece[:, :, 3] >= 250).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
    if count < 2:
        return None
    largest = 1 + stats[1:, cv2.CC_STAT_AREA].argmax()
    if stats[largest, cv2.CC_STAT_AREA] < 100:
        return None
    mask = (labels == largest).astype(np.uint8)
    x, y, w, h = cv2.boundingRect(mask)
    return mask[y:y+h, x:x+w]


def rotate_mask(mask, angle):
    h, w = mask.shape
    size = math.ceil(math.hypot(h, w)) + 4
    matrix = cv2.getRotationMatrix2D(((w-1)/2, (h-1)/2), -float(angle), 1)
    matrix[:, 2] += [(size-w)/2, (size-h)/2]
    rotated = cv2.warpAffine(mask, matrix, (size, size), flags=cv2.INTER_NEAREST)
    x, y, w, h = cv2.boundingRect(rotated)
    return rotated[y:y+h, x:x+w]


def angle_score(gray, gradient, mask, angle, center=None, peaks=1):
    shape = rotate_mask(mask, angle)
    pad = max(2, round(min(mask.shape)*.06))
    shape = cv2.copyMakeBorder(shape, pad, pad, pad, pad, cv2.BORDER_CONSTANT)
    inside = shape.astype(np.float32)
    ring = (cv2.dilate(shape, np.ones((2*pad+1, 2*pad+1), np.uint8)) > shape).astype(np.float32)
    h, w = shape.shape
    x0 = y0 = 0
    if center is not None:
        x0 = max(0, math.ceil(center[0]-w/2-5))
        y0 = max(0, math.ceil(center[1]-h/2-5))
        x1 = min(gray.shape[1], math.floor(center[0]-w/2+5)+w)
        y1 = min(gray.shape[0], math.floor(center[1]-h/2+5)+h)
        gray, gradient = gray[y0:y1, x0:x1], gradient[y0:y1, x0:x1]
    if h > gray.shape[0] or w > gray.shape[1]:
        invalid = (-1., float(angle), (0., 0.))
        return invalid if peaks == 1 else [invalid]
    kernel = ring/ring.sum() - inside/inside.sum()
    contrast = cv2.matchTemplate(gray[:, :, 0].copy(), kernel, cv2.TM_CCOEFF_NORMED)
    chroma = cv2.matchTemplate(gray[:, :, 1].copy(), kernel, cv2.TM_CCOEFF_NORMED)
    boundary = cv2.morphologyEx(shape, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)).astype(np.float32)
    edge = cv2.matchTemplate(gradient[:, :, 2].copy(), boundary, cv2.TM_CCORR_NORMED)
    normals = np.stack([cv2.Sobel(inside, cv2.CV_32F, 1, 0),
                        cv2.Sobel(inside, cv2.CV_32F, 0, 1)], axis=2)
    alignment = cv2.matchTemplate(gradient[:, :, :2].copy(), normals, cv2.TM_CCORR_NORMED)
    # Accept both light and dark cutouts. Soft chroma limits textured scenery's influence.
    score = .4*np.abs(contrast) + .9*chroma + .35*edge + .5*np.abs(alignment)
    score[~np.isfinite(score)] = -1
    found = []
    for _ in range(peaks):
        _, best, _, loc = cv2.minMaxLoc(score)
        # Return the actual local maximum, not the original search-window center.
        found.append((float(best), float(angle), (loc[0]+x0+w/2, loc[1]+y0+h/2)))
        if peaks > 1:
            cv2.circle(score, loc, max(h, w)//3, -1, -1)
    return found[0] if peaks == 1 else found


def detect_angle(bg, piece, angle_min=-75, angle_max=75):
    if not np.isfinite([angle_min, angle_max]).all():
        return []
    lo, hi = max(-75., float(angle_min)), min(75., float(angle_max))
    mask = piece_mask(piece)
    if lo > hi or mask is None or bg is None or bg.ndim != 3 or bg.shape[2] != 3:
        return []
    gray = cv2.GaussianBlur(cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY), (3, 3), 0).astype(np.float32)
    gx, gy = cv2.Sobel(gray, cv2.CV_32F, 1, 0), cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    gradient = np.stack([gx, gy, cv2.magnitude(gx, gy)], axis=2)
    chroma = 255*(1-np.exp(-(bg.max(axis=2).astype(np.float32)-bg.min(axis=2))/20))
    gray = np.stack([gray, cv2.GaussianBlur(chroma, (3, 3), 0)], axis=2)
    small_gray = cv2.resize(gray, None, fx=.5, fy=.5, interpolation=cv2.INTER_AREA)
    small_gradient = cv2.resize(gradient, None, fx=.5, fy=.5, interpolation=cv2.INTER_AREA)
    small_mask = cv2.resize(mask, None, fx=.5, fy=.5, interpolation=cv2.INTER_NEAREST)
    angles = sorted(set([lo, hi] + [float(a) for a in range(-75, 76, 10) if lo <= a <= hi]))
    coarse = [candidate for a in angles
              for candidate in angle_score(small_gray, small_gradient, small_mask, a, peaks=2)]
    seeds = []
    for value, angle, center in sorted(coarse, reverse=True):
        if value <= 0:
            continue
        candidate = (value, angle, (center[0]*2, center[1]*2))
        if all(abs(angle-s[1]) >= 12 or math.hypot(candidate[2][0]-s[2][0], candidate[2][1]-s[2][1]) > 15 for s in seeds):
            seeds.append(candidate)
        if len(seeds) == 8:
            break
    scores = []
    for _, angle, center in seeds:
        # Spend extra local searches only on weak matches, without a second full-image scan.
        if len(scores) >= 4 and max(s[0] for s in scores) >= .8:
            break
        fine = [angle_score(gray, gradient, mask, a, center)
                for a in np.arange(max(lo, angle-7), min(hi, angle+7)+.01, 2) if a <= hi]
        scores.append(max(fine))
    # Several coarse seeds often converge to the same solution. Refine it only once.
    refined = []
    for candidate in sorted(scores, reverse=True):
        value, angle, center = candidate
        if value <= 0 or any(abs(angle-s[1]) <= 4 and math.hypot(center[0]-s[2][0], center[1]-s[2][1]) <= 8 for s in refined):
            continue
        precise = [candidate] + [angle_score(gray, gradient, mask, a, center)
                    for a in np.arange(max(lo, angle-1.5), min(hi, angle+1.5)+.01, .25) if a <= hi]
        refined.append(max(precise))
    # Only local peaks are hypotheses; intermediate sampled angles are not alternatives.
    return sorted(refined, reverse=True)


def select_target(scores, slope, intercept, max_dx):
    """Select strongest reachable *refined* hypothesis, regardless of input order.

    Retain the original 90% ambiguity guard; do not force a low-quality match.
    """
    if not np.isfinite([slope, intercept, max_dx]).all() or abs(slope) < .02:
        return None, 'invalid_calibration'
    valid = [s for s in scores if np.isfinite([s[0], s[1]]).all() and s[0] > 0]
    reachable = [s for s in valid if 1 <= (s[1]-intercept)/slope <= max_dx]
    if not reachable:
        return None, 'no_reachable_candidate'
    best = max(reachable, key=lambda s: s[0])
    if best[0] < max(s[0] for s in valid)*.9:
        return None, 'ambiguous_reachable_candidate'
    return best, 'ok'
