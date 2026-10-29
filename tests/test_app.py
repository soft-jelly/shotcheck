# SPDX-License-Identifier: MIT
"""Localhost app endpoints. The verifier and its thresholds stay untouched."""

import json
import threading
import unittest
import urllib.error
import urllib.request

import numpy as np

from shotcheck import app
from shotcheck.synthetic import make_base, render, translating, write_clip


def encode(intent, files):
    boundary = "----shotcheckboundary"
    chunks = [
        f'--{boundary}\r\nContent-Disposition: form-data; name="intent"\r\n\r\n{intent}\r\n'.encode()
    ]
    for name, data in files:
        chunks.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="clip"; filename="{name}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n".encode() + data + b"\r\n"
        )
    chunks.append(f"--{boundary}--\r\n".encode())
    body = b"".join(chunks)
    return body, {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }


class AppEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = app.start(port=0)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"
        cls.directory = __import__("tempfile").TemporaryDirectory()
        root = __import__("pathlib").Path(cls.directory.name)
        cls.tilt = root / "tilt_up.avi"
        write_clip(cls.tilt, translating(17, 0, 5))
        cls.flat = root / "flat.avi"
        write_clip(cls.flat, [np.zeros((144, 192), np.uint8) for _ in range(17)])
        cls.static = root / "static.avi"
        write_clip(cls.static, [render(make_base())] * 17)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.directory.cleanup()

    def request(self, method, path, body=None, headers=None):
        req = urllib.request.Request(self.base + path, data=body, headers=headers or {}, method=method)
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()

    def test_page_leads_with_the_job_and_the_limits(self):
        code, body = self.request("GET", "/")
        page = body.decode("utf-8")
        self.assertEqual(code, 200)
        self.assertIn("Did the camera move you asked for actually happen?", page)
        self.assertIn("INCONCLUSIVE means the evidence was weak or mixed and is never counted as a pass.", page)
        self.assertIn("not 3D camera pose", page)
        self.assertIn("real pan and dolly clips returned INCONCLUSIVE", page)
        self.assertIn("Not a general accuracy benchmark.", page)
        self.assertIn("Clean install verified on a fresh Linux VM (Python 3.13.18, 2026-10-26).", page)
        self.assertIn("does not generate video", page)
        self.assertIn("LTX is not a core model", page)
        self.assertIn("recorded checks: inconclusive", page)
        self.assertIn(
            'const RECORDED_INCONCLUSIVE = ["pan_right", "pan_left", "dolly_in", "dolly_out"];',
            page,
        )
        self.assertIn('name + " - recorded checks: inconclusive"', page)

    def test_page_plays_the_chosen_clip_beside_the_verdict(self):
        code, body = self.request("GET", "/")
        page = body.decode("utf-8")
        self.assertEqual(code, 200)
        self.assertIn("video.muted = true", page)
        self.assertIn("video.loop = true", page)
        self.assertIn("createObjectURL", page)
        self.assertIn("function directionMark", page)

    def test_moves_are_the_checker_moves(self):
        code, body = self.request("GET", "/api/moves")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["moves"], list(app.mv.EXPECTED_SCENE_LABEL))

    def test_unknown_route_is_not_found(self):
        code, body = self.request("GET", "/nope")
        self.assertEqual(code, 404)
        self.assertEqual(json.loads(body)["error"], "not found")

    def test_tilt_up_control_matches_and_the_opposite_mismatches(self):
        for intent, verdict in (("tilt_up", "MATCH"), ("tilt_down", "MISMATCH")):
            with self.subTest(intent=intent):
                body, headers = encode(intent, [("tilt_up.avi", self.tilt.read_bytes())])
                code, payload = self.request("POST", "/api/check", body, headers)
                report = json.loads(payload)
                self.assertEqual(code, 200, report)
                self.assertEqual(report["verdict"], verdict)
                self.assertEqual(report["requested"], intent)
                self.assertEqual(report["measured"], "scene_down")
                self.assertEqual(report["expected_scene_label"], app.mv.expected_scene_label(intent))
                self.assertEqual(len(report["windows"]), 4)
                self.assertTrue(all(row["verdict"] == verdict for row in report["windows"]))
                self.assertIn("never counted as a pass", report["note"])

    def test_weak_evidence_is_inconclusive_not_a_pass(self):
        body, headers = encode("static", [("flat.avi", self.flat.read_bytes())])
        code, payload = self.request("POST", "/api/check", body, headers)
        report = json.loads(payload)
        self.assertEqual(code, 200, report)
        self.assertEqual(report["verdict"], "INCONCLUSIVE")
        self.assertEqual(report["counts"]["match"], 0)
        self.assertGreater(report["counts"]["unknown"], 0)

    def test_bad_intent_never_calls_a_verdict(self):
        body, headers = encode("orbit", [("tilt_up.avi", self.tilt.read_bytes())])
        code, payload = self.request("POST", "/api/check", body, headers)
        self.assertEqual(code, 400)
        self.assertIn("unsupported trajectory", json.loads(payload)["error"])
        self.assertNotIn("verdict", json.loads(payload))

    def test_takes_keep_one_requested_move(self):
        body, headers = encode("tilt_up", [
            ("keep.avi", self.tilt.read_bytes()),
            ("static.avi", self.static.read_bytes()),
            ("flat.avi", self.flat.read_bytes()),
        ])
        code, payload = self.request("POST", "/api/takes", body, headers)
        report = json.loads(payload)
        self.assertEqual(code, 200, report)
        self.assertEqual(report["requested"], "tilt_up")
        self.assertEqual([row["verdict"] for row in report["takes"]], ["MATCH", "MISMATCH", "INCONCLUSIVE"])
        self.assertIn("never counted as a pass", report["note"])

    def test_refuses_a_public_bind(self):
        with self.assertRaises(ValueError):
            app.start(host="0.0.0.0", port=0)
