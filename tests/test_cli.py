# SPDX-License-Identifier: MIT
"""Network-free SDK smoke tests: fake transport, never fake node/control tests."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import cv2
import numpy as np

from shotcheck import cli


class CliSmokeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.clip = self.root / "local.avi"
        self.clip.write_bytes(b"fake transport fixture; not decoded by CLI")
        self.out = self.root / "result"

    def invoke(self, status="match", **extra):
        counts = {key: 4 if key == status else 0 for key in ("match", "mismatch", "unknown")}
        report = {
            "segments": [{"frame_start": i * 4, "frame_end": (i + 1) * 4,
                          "rig_status": status, "confidence": 0.0 if status == "unknown" else 1.0,
                          "label": "unknown" if status == "unknown" else "scene_down"}
                         for i in range(4)],
            "rig_comparison": {"segment_counts": counts},
        }
        client = MagicMock()
        client.__enter__.return_value = client
        job = client.run.return_value
        job.id, job.status = "local-test-job", "succeeded"
        output = MagicMock()
        job.get_outputs.return_value = [output]
        png = cv2.imencode(".png", np.zeros((2, 2, 3), np.uint8))[1].tobytes()
        output.to_file.side_effect = lambda path: Path(path).write_bytes(png)
        history = {"local-test-job": {
            "status": {"completed": True}, "outputs": {"1": {"text": [json.dumps(report)]}},
        }}
        stream = io.BytesIO(json.dumps(history).encode("utf-8"))
        stdout, stderr = io.StringIO(), io.StringIO()
        args = ["run", str(self.clip), "--intent", "tilt_up", "--out", str(self.out)]
        for flag, value in extra.items():
            args += ["--" + flag.replace("_", "-"), value]
        with patch.object(cli, "Comfy", return_value=client) as factory, \
                patch.object(cli, "urlopen", return_value=stream) as history_get, \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = cli.main(args)
        return code, stdout.getvalue(), stderr.getvalue(), client, factory, history_get

    def test_sdk_graph_download_and_saved_json(self):
        code, text, error, client, factory, history_get = self.invoke()
        self.assertEqual(code, 0, error)
        factory.assert_called_once_with(timeout=1200)
        graph = client.workflows.from_json.call_args.args[0]
        self.assertEqual(graph["1"]["class_type"], "ShotCheckMotionVerifier")
        self.assertEqual(graph["1"]["inputs"]["video_path"], str(self.clip.resolve()))
        self.assertEqual(graph["1"]["inputs"]["intended_direction"], "tilt_up")
        self.assertEqual(graph["2"]["inputs"]["images"], ["1", 1])
        self.assertEqual(client.run.call_args.kwargs, {"timeout": 1200})
        self.assertIn("4 match, 0 mismatch, 0 inconclusive", text)
        self.assertTrue((self.out / "overlay.png").is_file())
        saved = json.loads((self.out / "verdict.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["_execution"]["job_id"], "local-test-job")
        self.assertFalse(saved["_execution"]["api_key_used"])
        history_get.assert_called_once_with(
            "http://127.0.0.1:8188/history/local-test-job", timeout=1200,
        )

    def test_inconclusive_is_explicitly_not_a_pass(self):
        code, text, error, *_ = self.invoke("unknown")
        self.assertEqual(code, 0, error)
        self.assertIn("0 match, 0 mismatch, 4 inconclusive", text)
        self.assertIn("Abstention is a feature", text)
        self.assertIn("never a pass", text)

    def test_mismatch_is_printed(self):
        code, text, error, *_ = self.invoke("mismatch")
        self.assertEqual(code, 0, error)
        self.assertIn("0 match, 4 mismatch, 0 inconclusive", text)

    def test_refuses_nonlocal_proxy_before_sdk_call(self):
        code, _, error, _, factory, _ = self.invoke(proxy_url="https://api.comfy.org")
        self.assertEqual(code, 2)
        self.assertIn("loopback", error)
        factory.assert_not_called()

    def test_existing_output_is_not_overwritten(self):
        self.out.mkdir()
        sentinel = self.out / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        code, _, _, _, factory, _ = self.invoke()
        self.assertEqual(code, 2)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        factory.assert_not_called()
