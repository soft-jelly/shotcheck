# SPDX-License-Identifier: MIT
import json
from pathlib import Path
import tempfile
import unittest

from shotcheck.node import ShotCheckMotionVerifier
from shotcheck.synthetic import make_base, render, scaling, translating, write_clip


class SyntheticControls(unittest.TestCase):
    def check_control(self, frames, correct, opposite, measured):
        with tempfile.TemporaryDirectory() as directory:
            path = write_clip(Path(directory) / "control.avi", frames)
            for intended in (correct,) if opposite is None else (correct, opposite):
                with self.subTest(intended=intended):
                    output = ShotCheckMotionVerifier().verify(str(path), intended)
                    report = json.loads(output["result"][0])
                    self.assertEqual(report["overall"]["label"], measured)
                    self.assertGreater(report["overall"]["confidence"], 0.9)
                    expected = ({"match": 4, "mismatch": 0, "unknown": 0}
                                if intended == correct else
                                {"match": 0, "mismatch": 4, "unknown": 0})
                    self.assertEqual(report["rig_comparison"]["segment_counts"], expected)

    def test_pan_right_five_pixels_and_opposite(self):
        self.check_control(translating(17, -5, 0), "pan_right", "pan_left", "scene_left")

    def test_tilt_up_five_pixels_and_opposite(self):
        self.check_control(translating(17, 0, 5), "tilt_up", "tilt_down", "scene_down")

    def test_dolly_in_one_percent_and_opposite(self):
        self.check_control(scaling(17, 1.01), "dolly_in", "dolly_out", "expansion")

    def test_static(self):
        self.check_control([render(make_base())] * 17, "static", None, "static")
