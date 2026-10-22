# SPDX-License-Identifier: MIT
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

from shotcheck import motion_verifier as mv
from shotcheck.node import ShotCheckMotionVerifier
from shotcheck.synthetic import make_base, render, translating, write_clip


class NodeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "fixture.avi"
        self.addCleanup(self.directory.cleanup)

    def check_result(self, direction):
        thresholds = dict(mv.DEFAULT_THRESHOLDS)
        with patch.object(mv, "analyze_video", wraps=mv.analyze_video) as analyze:
            result = ShotCheckMotionVerifier().verify(str(self.path), direction)
            analyze.assert_called_once_with(str(self.path.resolve()), rig={"trajectory": direction})
        report = json.loads(result["result"][0])
        self.assertEqual(json.loads(result["ui"]["text"][0]), report)
        overlay = result["result"][1]
        self.assertEqual(overlay.dtype, torch.float32)
        self.assertEqual(overlay.ndim, 4)
        self.assertEqual((overlay.shape[0], overlay.shape[2], overlay.shape[3]), (1, 640, 3))
        self.assertGreaterEqual(float(overlay.min()), 0)
        self.assertLessEqual(float(overlay.max()), 1)
        self.assertEqual(overlay.device.type, "cpu")
        self.assertEqual(mv.DEFAULT_THRESHOLDS, thresholds)
        self.assertGreaterEqual(report["node_runtime"]["process_cpu_seconds"], 0)
        return report

    def test_tilt_up_matches_inverse_screen_flow(self):
        write_clip(self.path, translating(17, 0, 2))
        report = self.check_result("tilt_up")
        self.assertEqual(report["rig_comparison"]["expected_scene_label"], "scene_down")
        self.assertEqual(report["rig_comparison"]["segment_counts"],
                         {"match": 4, "mismatch": 0, "unknown": 0})

    def test_moving_clip_fails_static_gate(self):
        write_clip(self.path, translating(17, 0, 2))
        report = self.check_result("static")
        self.assertEqual(report["rig_comparison"]["verdict"], "has_mismatch")
        self.assertEqual(report["rig_comparison"]["segment_counts"]["mismatch"], 4)

    def test_identical_textured_frames_pass_static_gate(self):
        write_clip(self.path, [render(make_base())] * 17)
        report = self.check_result("static")
        self.assertEqual(report["overall"]["label"], "static")
        self.assertEqual(report["rig_comparison"]["segment_counts"]["match"], 4)

    def test_untextured_clip_remains_inconclusive(self):
        write_clip(self.path, [np.full((144, 192), 90, np.uint8)] * 17)
        report = self.check_result("static")
        self.assertEqual(report["rig_comparison"]["verdict"], "no_known_segments")
        self.assertEqual(report["rig_comparison"]["segment_counts"]["unknown"], 4)

    def test_rejects_remote_input_and_invalid_direction(self):
        with self.assertRaisesRegex(ValueError, "local file"):
            ShotCheckMotionVerifier().verify("https://example.com/video.mp4", "static")
        with self.assertRaisesRegex(ValueError, "unsupported trajectory"):
            ShotCheckMotionVerifier().verify("unused.mp4", "orbit")

    def test_cache_fingerprint_changes_with_clip_bytes(self):
        write_clip(self.path, translating(3, 0, 2))
        before = ShotCheckMotionVerifier.IS_CHANGED(str(self.path), "tilt_up")
        write_clip(self.path, translating(3, 2, 0))
        after = ShotCheckMotionVerifier.IS_CHANGED(str(self.path), "tilt_up")
        self.assertNotEqual(before, after)
