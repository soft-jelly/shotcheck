# SPDX-License-Identifier: MIT
"""Procedural CC0 texture/control pixels; generator code is MIT."""

from pathlib import Path

import cv2
import numpy as np

W, H = 192, 144


def make_base(seed=7, scale=3):
    rng = np.random.RandomState(seed)
    noise = rng.randint(0, 256, (H * scale, W * scale)).astype(np.float32)
    tex = cv2.GaussianBlur(noise, (0, 0), 1.6)
    tex = (tex - tex.min()) / (tex.max() - tex.min()) * 255.0
    return tex.astype(np.uint8)


def render(base, shift=(0.0, 0.0), scale=1.0):
    bh, bw = base.shape
    cb = np.array([(bw - 1) / 2.0, (bh - 1) / 2.0])
    cf = np.array([(W - 1) / 2.0, (H - 1) / 2.0])
    m = np.array([[scale, 0, cf[0] - scale * cb[0] + shift[0]],
                  [0, scale, cf[1] - scale * cb[1] + shift[1]]], dtype=np.float64)
    return cv2.warpAffine(base, m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def translating(n, vx, vy, base=None):
    base = make_base() if base is None else base
    return [render(base, (vx * i, vy * i)) for i in range(n)]


def scaling(n, s, base=None):
    base = make_base() if base is None else base
    return [render(base, scale=s ** i) for i in range(n)]


def write_clip(path, frames):
    path = Path(path)
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 24.0, (W, H), False)
    if not writer.isOpened():
        raise IOError("MJPG encoder unavailable")
    try:
        for frame in frames:
            writer.write(frame)
    finally:
        writer.release()
    return path
