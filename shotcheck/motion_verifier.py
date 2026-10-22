#!/usr/bin/env python3
"""Offline screen-space motion verifier (Phase 2A, no inference).

Measures the dominant 2D translation and the affine (similarity) scale of
image content between frames of a local video, per time segment, and reports
how much evidence supports each measurement.

WHAT THIS IS NOT
- It does NOT recover 3D camera pose.
- Optical flow of the scene cannot distinguish a camera pan/tilt from the
  opposite scene movement, so a measurement of "scene_left" is equally
  explained by a camera pan right or by the scene sliding left.
- Scale > 1 means zoom-like (expanding) flow. It is not proof of a physical
  dolly (a lens zoom produces the same flow).
- There is deliberately no score claiming physical fidelity. A rig comparison
  only states whether measured screen motion label equals the label the rig
  trajectory would predict.

SIGN CONVENTION (independent of any source/rig/engine)
- Image coordinates: x grows to the right, y grows downward, in pixels.
- Everything describes the motion of IMAGE CONTENT from frame i to frame j:
    dx > 0  content moves right  (label "scene_right")
    dx < 0  content moves left   (label "scene_left")
    dy > 0  content moves down   (label "scene_down")
    dy < 0  content moves up     (label "scene_up")
    scale > 1 content expands about the image center ("expansion")
    scale < 1 content contracts about the image center ("contraction")
- Translation is the displacement of the image-center point under the fitted
  similarity transform, per frame, so it is separable from scale.

RIG TRAJECTORY -> EXPECTED MEASURED LABEL
    pan_right -> scene_left     pan_left  -> scene_right
    tilt_up   -> scene_down     tilt_down -> scene_up
    dolly_in  -> expansion      dolly_out -> contraction
    static    -> static

CLI
    python studio/motion_verifier.py VIDEO [--rig RIG.json] [--segments N]
        [--stride K] [--max-frames N] [--max-dim PX] [--out FILE.json]
    Prints a JSON report on stdout (or FILE). Exit code 0 on a produced
    report (even if labels are "unknown"), 2 on unusable input
    (unreadable video, bad rig JSON).

API
    analyze_frames(frames, fps=None, segments=4, stride=1, rig=None,
                   thresholds=None, max_dim=640) -> dict
    analyze_video(path, ...) -> dict
    expected_scene_label(trajectory) -> str

Labels: static, scene_left, scene_right, scene_up, scene_down, expansion,
contraction, unknown. "unknown" always comes with machine-readable reasons.
"""

import argparse
import json
import math
import sys
from typing import Any, Dict, Iterable, List, Optional

import cv2
import numpy as np

EXPECTED_SCENE_LABEL = {
    "pan_right": "scene_left",
    "pan_left": "scene_right",
    "tilt_up": "scene_down",
    "tilt_down": "scene_up",
    "dolly_in": "expansion",
    "dolly_out": "contraction",
    "static": "static",
}

DEFAULT_THRESHOLDS: Dict[str, float] = {
    # Translation rate (fraction of frame width/height per frame) above which
    # content is considered moving.
    "translation_rate": 0.002,
    # |ln(scale)| per frame above which content is considered scaling.
    "scale_rate": 0.002,
    # Rotation (deg/frame) above which motion is ambiguous (not pan/zoom).
    "rotation_deg": 0.5,
    # A dominant component must exceed the other (in threshold units) by this.
    "component_dominance": 3.0,
    # Within translation, dominant axis must exceed the other by this factor.
    "axis_dominance": 2.0,
    # Pair-level estimate validity.
    "min_gray_std": 2.0,
    "min_tracks": 20,
    "min_inliers": 12,
    "min_inlier_ratio": 0.6,
    "max_fb_error_px": 1.0,
    "ransac_px": 1.5,
    # Segment-level validity.
    "min_valid_pair_fraction": 0.5,
    "min_pair_agreement": 0.6,
}

DISCLAIMERS = [
    "Screen-space measurement only; no 3D camera pose is inferred.",
    "Optical flow cannot distinguish camera pan/tilt from opposite scene movement.",
    "Scale is zoom-like flow, not proof of a physical dolly.",
    "No physical-fidelity score is computed.",
]


def expected_scene_label(trajectory: str) -> str:
    """Measured-label a rig trajectory predicts (see module docstring)."""
    if trajectory not in EXPECTED_SCENE_LABEL:
        raise ValueError(
            f"unsupported trajectory {trajectory!r}; expected one of "
            f"{sorted(EXPECTED_SCENE_LABEL)}"
        )
    return EXPECTED_SCENE_LABEL[trajectory]


def classify_motion(
    tx_norm: float, ty_norm: float, log_scale: float, rotation_deg: float,
    th: Dict[str, float],
) -> Dict[str, Any]:
    """Map per-frame measurements to a label; ambiguity yields 'unknown'."""
    mt = max(abs(tx_norm), abs(ty_norm)) / th["translation_rate"]
    ms = abs(log_scale) / th["scale_rate"]
    dom = th["component_dominance"]
    if abs(rotation_deg) >= th["rotation_deg"]:
        return {"label": "unknown", "reasons": ["ambiguous_rotation"]}
    if mt < 1.0 and ms < 1.0:
        return {"label": "static", "reasons": []}
    if mt >= 1.0 and ms >= 1.0:
        if ms >= dom * mt:
            mt = 0.0
        elif mt >= dom * ms:
            ms = 0.0
        else:
            return {"label": "unknown", "reasons": ["ambiguous_translation_and_scale"]}
    if ms >= 1.0 and mt < 1.0:
        return {"label": "expansion" if log_scale > 0 else "contraction", "reasons": []}
    ax, ay = abs(tx_norm), abs(ty_norm)
    k = th["axis_dominance"]
    if ax >= k * ay:
        return {"label": "scene_right" if tx_norm > 0 else "scene_left", "reasons": []}
    if ay >= k * ax:
        return {"label": "scene_down" if ty_norm > 0 else "scene_up", "reasons": []}
    return {"label": "unknown", "reasons": ["ambiguous_diagonal_translation"]}


def _to_gray_u8(frame: np.ndarray, max_dim: int) -> np.ndarray:
    a = np.asarray(frame)
    if a.dtype != np.uint8:
        a = np.clip(a, 0, 255).astype(np.uint8)  # values assumed on a 0..255 scale
    if a.ndim == 3:
        a = cv2.cvtColor(a, cv2.COLOR_BGRA2GRAY if a.shape[2] == 4 else cv2.COLOR_BGR2GRAY)
    elif a.ndim != 2:
        raise ValueError("frames must be HxW or HxWxC arrays")
    h, w = a.shape
    big = max(h, w)
    if max_dim and big > max_dim:
        f = max_dim / float(big)
        a = cv2.resize(a, (max(1, round(w * f)), max(1, round(h * f))), interpolation=cv2.INTER_AREA)
    return a


def _failed(reason: str, tracks: int = 0) -> Dict[str, Any]:
    return {"valid": False, "reason": reason, "tracks": tracks}


def _estimate_pair(g0: np.ndarray, g1: np.ndarray, th: Dict[str, float]) -> Dict[str, Any]:
    """Similarity (scale+rotation+translation) fit of content motion g0 -> g1."""
    if float(g0.std()) < th["min_gray_std"] or float(g1.std()) < th["min_gray_std"]:
        return _failed("insufficient_texture")
    pts = cv2.goodFeaturesToTrack(g0, maxCorners=400, qualityLevel=0.01, minDistance=8, blockSize=7)
    if pts is None or len(pts) < th["min_tracks"]:
        return _failed("insufficient_texture", 0 if pts is None else len(pts))
    lk = dict(winSize=(21, 21), maxLevel=3,
              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
    p1, st, _ = cv2.calcOpticalFlowPyrLK(g0, g1, pts, None, **lk)
    pb, stb, _ = cv2.calcOpticalFlowPyrLK(g1, g0, p1, None, **lk)
    fb = np.linalg.norm((pts - pb).reshape(-1, 2), axis=1)
    ok = (st.ravel() == 1) & (stb.ravel() == 1) & (fb < th["max_fb_error_px"])
    n_ok = int(ok.sum())
    if n_ok < th["min_tracks"]:
        return _failed("tracking_failed", n_ok)
    a = pts.reshape(-1, 2)[ok]
    b = p1.reshape(-1, 2)[ok]
    m, inl = cv2.estimateAffinePartial2D(
        a, b, method=cv2.RANSAC, ransacReprojThreshold=th["ransac_px"])
    if m is None or inl is None:
        return _failed("affine_fit_failed", n_ok)
    n_inl = int(inl.sum())
    ratio = n_inl / float(n_ok)
    if n_inl < th["min_inliers"] or ratio < th["min_inlier_ratio"]:
        return _failed("inconsistent_motion_field", n_ok)
    h, w = g0.shape
    c = np.array([(w - 1) / 2.0, (h - 1) / 2.0])
    lin = m[:, :2]
    disp = lin @ c + m[:, 2] - c
    det = float(np.linalg.det(lin))
    if det <= 0:
        return _failed("affine_fit_failed", n_ok)
    return {
        "valid": True, "tracks": n_ok, "inliers": n_inl, "inlier_ratio": ratio,
        "dx_px": float(disp[0]), "dy_px": float(disp[1]),
        "scale": math.sqrt(det),
        "rotation_deg": math.degrees(math.atan2(m[1, 0], m[0, 0])),
        "confidence": ratio * min(1.0, n_inl / 50.0),
    }


def _segment(pairs: List[Dict[str, Any]], start: int, end: int, size, stride: int,
             fps: Optional[float], th: Dict[str, float]) -> Dict[str, Any]:
    h, w = size
    valid = [p for p in pairs if p["valid"]]
    seg: Dict[str, Any] = {
        "frame_start": start, "frame_end": end,
        "n_pairs": len(pairs), "n_valid_pairs": len(valid),
    }
    if fps:
        seg["time_start_sec"] = round(start / fps, 4)
        seg["time_end_sec"] = round(end / fps, 4)
    reasons: List[str] = []
    if len(valid) < max(1.0, th["min_valid_pair_fraction"] * len(pairs)):
        counts: Dict[str, int] = {}
        for p in pairs:
            if not p["valid"]:
                counts[p["reason"]] = counts.get(p["reason"], 0) + 1
        reasons = [max(counts, key=counts.get)] if counts else ["no_pairs"]
        seg.update(label="unknown", confidence=0.0, unknown_reasons=reasons,
                   failure_counts=counts)
        return seg
    dx = float(np.median([p["dx_px"] for p in valid])) / stride
    dy = float(np.median([p["dy_px"] for p in valid])) / stride
    sc = float(np.median([p["scale"] for p in valid]))
    lsc = math.log(sc) / stride
    rot = float(np.median([p["rotation_deg"] for p in valid])) / stride
    cls = classify_motion(dx / w, dy / h, lsc, rot, th)
    pair_labels = [
        classify_motion(p["dx_px"] / stride / w, p["dy_px"] / stride / h,
                        math.log(p["scale"]) / stride, p["rotation_deg"] / stride, th)["label"]
        for p in valid
    ]
    agreement = pair_labels.count(cls["label"]) / float(len(valid))
    qual = float(np.median([p["confidence"] for p in valid]))
    conf = qual * (len(valid) / float(len(pairs))) * agreement
    label, reasons = cls["label"], list(cls["reasons"])
    if label != "unknown" and agreement < th["min_pair_agreement"]:
        label, reasons = "unknown", ["inconsistent_pairs"]
    seg.update({
        "label": label,
        "confidence": round(conf, 4) if label != "unknown" else 0.0,
        "unknown_reasons": reasons,
        "translation_px_per_frame": {"dx": round(dx, 4), "dy": round(dy, 4)},
        "translation_norm_per_frame": {"dx": round(dx / w, 6), "dy": round(dy / h, 6)},
        "scale_per_frame": round(math.exp(lsc), 6),
        "rotation_deg_per_frame": round(rot, 4),
        "pair_agreement": round(agreement, 4),
        "estimate_quality": round(qual, 4),
        "median_tracks": int(np.median([p["tracks"] for p in valid])),
    })
    return seg


def analyze_frames(
    frames: Iterable[np.ndarray],
    fps: Optional[float] = None,
    segments: int = 4,
    stride: int = 1,
    rig: Optional[Dict[str, Any]] = None,
    thresholds: Optional[Dict[str, float]] = None,
    max_dim: int = 640,
) -> Dict[str, Any]:
    """Measure screen-space motion over a sequence of frames.

    frames: iterable of uint8 (or 0..255 numeric) gray/BGR/BGRA arrays of equal size.
    rig: optional dict with a "trajectory" key; adds a "rig_comparison" block.
    Returns a JSON-serializable dict; see module docstring for conventions.
    """
    if segments < 1 or stride < 1:
        raise ValueError("segments and stride must be >= 1")
    th = dict(DEFAULT_THRESHOLDS)
    th.update(thresholds or {})
    grays = [_to_gray_u8(f, max_dim) for f in frames]
    if any(g.shape != grays[0].shape for g in grays):
        raise ValueError("all frames must have the same size")
    n = len(grays)
    result: Dict[str, Any] = {
        "convention": {
            "axes": "x right, y down, pixels; values describe motion of image content",
            "labels": sorted(set(EXPECTED_SCENE_LABEL.values()) | {"unknown"}),
            "scale": "similarity scale about image center; >1 expansion (zoom-like)",
        },
        "n_frames": n, "fps": fps, "stride": stride,
        "analysis_size": {"width": grays[0].shape[1], "height": grays[0].shape[0]} if n else None,
        "disclaimers": DISCLAIMERS,
        "segments": [],
    }
    idx = list(range(0, n - stride, stride)) if n > stride else []
    if not idx:
        result["overall"] = {"label": "unknown", "unknown_reasons": ["fewer_frames_than_needed"],
                             "confidence": 0.0}
    else:
        pairs = [_estimate_pair(grays[i], grays[i + stride], th) for i in idx]
        k = min(segments, len(idx))
        for chunk in np.array_split(np.arange(len(idx)), k):
            ps = [pairs[j] for j in chunk]
            start, end = idx[chunk[0]], idx[chunk[-1]] + stride
            result["segments"].append(_segment(ps, start, end, grays[0].shape, stride, fps, th))
        result["overall"] = _overall(result["segments"])
    if rig is not None:
        result["rig_comparison"] = compare_to_rig(result, rig)
    return result


def _overall(segs: List[Dict[str, Any]]) -> Dict[str, Any]:
    known = [s for s in segs if s["label"] != "unknown"]
    labels = sorted({s["label"] for s in known})
    if len(known) < math.ceil(len(segs) / 2.0):
        return {"label": "unknown", "confidence": 0.0,
                "unknown_reasons": ["too_few_known_segments"],
                "n_known_segments": len(known), "n_segments": len(segs)}
    out = {"n_known_segments": len(known), "n_segments": len(segs), "unknown_reasons": []}
    if len(labels) == 1:
        out.update(label=labels[0], confidence=round(min(s["confidence"] for s in known), 4))
    else:
        out.update(label="varied", labels_seen=labels,
                   confidence=round(min(s["confidence"] for s in known), 4))
    return out


def compare_to_rig(result: Dict[str, Any], rig: Dict[str, Any]) -> Dict[str, Any]:
    """Per-segment label agreement with the rig's trajectory (not a fidelity score)."""
    traj = rig.get("trajectory") if isinstance(rig, dict) else None
    if not isinstance(traj, str):
        raise ValueError('rig must be a JSON object with a string "trajectory"')
    expected = expected_scene_label(traj)
    statuses = []
    for s in result["segments"]:
        if s["label"] == "unknown":
            st = "unknown"
        else:
            st = "match" if s["label"] == expected else "mismatch"
        s["rig_status"] = st
        statuses.append(st)
    counts = {k: statuses.count(k) for k in ("match", "mismatch", "unknown")}
    if counts["match"] + counts["mismatch"] == 0:
        verdict = "no_known_segments"
    elif counts["mismatch"]:
        verdict = "has_mismatch"
    else:
        verdict = "all_known_segments_match"
    return {
        "trajectory": traj,
        "expected_scene_label": expected,
        "segment_counts": counts,
        "verdict": verdict,
        "note": "Label agreement only; pan/tilt vs opposite scene motion and dolly vs zoom are indistinguishable.",
    }


def load_rig(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        rig = json.load(fh)
    if not isinstance(rig, dict) or not isinstance(rig.get("trajectory"), str):
        raise ValueError('rig must be a JSON object with a string "trajectory"')
    expected_scene_label(rig["trajectory"])
    return rig


def analyze_video(path: str, max_frames: int = 0, **kwargs: Any) -> Dict[str, Any]:
    """Read a local video with OpenCV and run analyze_frames on it."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise IOError(f"cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or None
    frames = []
    while not max_frames or len(frames) < max_frames:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    cap.release()
    if not frames:
        raise IOError(f"no frames decoded from: {path}")
    kwargs.setdefault("fps", fps)
    return analyze_frames(frames, **kwargs)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Offline screen-space motion verifier (translation + zoom-like scale).")
    ap.add_argument("video", help="local video file")
    ap.add_argument("--rig", help="rig JSON with a 'trajectory' key (e.g. camera_rig.json)")
    ap.add_argument("--segments", type=int, default=4)
    ap.add_argument("--stride", type=int, default=1, help="frame gap per measurement")
    ap.add_argument("--max-frames", type=int, default=0, help="0 = all frames")
    ap.add_argument("--max-dim", type=int, default=640, help="downscale longest side to this")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    a = ap.parse_args(argv)
    try:
        rig = load_rig(a.rig) if a.rig else None
        res = analyze_video(a.video, max_frames=a.max_frames, segments=a.segments,
                            stride=a.stride, rig=rig, max_dim=a.max_dim)
    except (IOError, OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(res, indent=2)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
