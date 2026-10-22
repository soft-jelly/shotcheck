# SPDX-License-Identifier: MIT
"""Local-only ComfyUI adapter for the unchanged screen-motion verifier."""

import hashlib
import json
from pathlib import Path
import time

import cv2
import numpy as np
import torch

from . import motion_verifier as mv


def local_video(video_path):
    if "://" in video_path or video_path.startswith(("\\\\", "//")):
        raise ValueError("video_path must be a local file, not a URL or network share")
    path = Path(video_path).resolve(strict=True)
    if not path.is_file():
        raise ValueError("video_path must name a file")
    return path


class ShotCheckMotionVerifier:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "video_path": ("STRING", {"default": ""}),
            "intended_direction": (list(mv.EXPECTED_SCENE_LABEL),),
        }}

    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("verdict_json", "motion_overlay")
    FUNCTION = "verify"
    CATEGORY = "ShotCheck"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, video_path, intended_direction):
        with local_video(video_path).open("rb") as stream:
            return hashlib.file_digest(stream, "sha256").hexdigest()

    def verify(self, video_path, intended_direction):
        mv.expected_scene_label(intended_direction)
        path = local_video(video_path)
        wall_start, cpu_start = time.perf_counter(), time.process_time()
        report = mv.analyze_video(str(path), rig={"trajectory": intended_direction})

        cap = cv2.VideoCapture(str(path))
        ok, frame = cap.read()
        cap.release()
        if not ok:
            raise IOError(f"cannot read overlay frame: {path}")
        width = 640
        height = round(frame.shape[0] * width / frame.shape[1])
        frame = cv2.resize(frame, (width, height))
        canvas = np.zeros((height + 180, width, 3), dtype=np.uint8)
        canvas[:height] = frame
        comparison = report["rig_comparison"]
        lines = [
            f"{intended_direction} -> expected {comparison['expected_scene_label']}",
            f"{comparison['verdict']} | confidence {report['overall']['confidence']}",
        ]
        for index, segment in enumerate(report["segments"], 1):
            translation = segment.get("translation_px_per_frame", {})
            lines.append(
                f"{index}: {segment['label']} ({segment['rig_status']}) "
                f"dx={translation.get('dx', 'n/a')} dy={translation.get('dy', 'n/a')} "
                f"s={segment.get('scale_per_frame', 'n/a')}"
            )
        for index, line in enumerate(lines):
            cv2.putText(canvas, line, (8, height + 22 + 24 * index),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.43, (240, 240, 240), 1, cv2.LINE_AA)
        overlay = torch.from_numpy(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)).float().div(255)
        report["node_runtime"] = {
            "device": "cpu",
            "wall_seconds": round(time.perf_counter() - wall_start, 6),
            "process_cpu_seconds": round(time.process_time() - cpu_start, 6),
            "includes": "video decode, unchanged verifier, first-frame overlay",
        }
        text = json.dumps(report, ensure_ascii=False, allow_nan=False)
        return {"ui": {"text": [text]}, "result": (text, overlay.unsqueeze(0))}


NODE_CLASS_MAPPINGS = {"ShotCheckMotionVerifier": ShotCheckMotionVerifier}
NODE_DISPLAY_NAME_MAPPINGS = {"ShotCheckMotionVerifier": "ShotCheck Motion Verifier"}
