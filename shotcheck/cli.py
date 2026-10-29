# SPDX-License-Identifier: MIT
"""Official SDK client for the local ShotCheck ComfyUI graph."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
from urllib.parse import urlsplit
from urllib.request import urlopen

from comfy_sdk import Comfy

from . import motion_verifier as mv
from .node import local_video


def local_url(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "http" or parsed.hostname != "127.0.0.1"
            or parsed.username is not None or parsed.password is not None
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise ValueError("Use an HTTP loopback service URL, such as http://127.0.0.1:8188")
    return value.rstrip("/")


def run(args):
    clip = local_video(args.clip)
    comfy_url, proxy_url = local_url(args.comfy_url), local_url(args.proxy_url)
    if args.out:
        folder = Path(args.out).resolve()
        folder.mkdir(parents=True, exist_ok=False)
    else:
        folder = Path(tempfile.mkdtemp(prefix="shotcheck_output_", dir=Path.cwd())).resolve()
    graph = {
        "1": {"class_type": "ShotCheckMotionVerifier", "inputs": {
            "video_path": str(clip), "intended_direction": args.intent,
        }},
        "2": {"class_type": "SaveImage", "inputs": {
            "images": ["1", 1], "filename_prefix": "shotcheck",
        }},
    }
    os.environ.pop("COMFY_API_KEY", None)
    os.environ["COMFY_BASE_URL"] = proxy_url
    print(f"Running CPU ShotCheck graph through Comfy SDK: {args.intent}", flush=True)
    with Comfy(timeout=1200) as client:
        job = client.run(client.workflows.from_json(graph), timeout=1200)
        if job.status != "succeeded":
            raise RuntimeError(f"SDK job did not succeed: {job.status}")
        outputs = job.get_outputs("2")
        if len(outputs) != 1:
            raise RuntimeError(f"Expected one overlay, received {len(outputs)}")
        outputs[0].to_file(str(folder / "overlay.png"))
        with urlopen(comfy_url + "/history/" + job.id, timeout=1200) as response:
            history = json.load(response)[job.id]
        if history["status"]["completed"] is not True:
            raise RuntimeError("ComfyUI history does not confirm a completed graph")
        report = json.loads(history["outputs"]["1"]["text"][0])
        report["_execution"] = {
            "platform": "Comfy SDK via local comfy-api-proxy",
            "job_id": job.id, "comfy_url": comfy_url, "proxy_url": proxy_url,
            "workflow": graph, "utc": datetime.now(timezone.utc).isoformat(),
            "api_key_used": False,
        }
    (folder / "verdict.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8",
    )
    print("Abstention is a feature: INCONCLUSIVE means ambiguous/insufficient evidence, never a pass.")
    print("Screen-flow label agreement only; not physical 3D camera pose.")
    print(f"{'SEGMENT':<9} {'FRAMES':<12} {'RESULT':<14} {'CONFIDENCE':<12} MOTION")
    labels = {"match": "MATCH", "mismatch": "MISMATCH", "unknown": "INCONCLUSIVE"}
    for index, segment in enumerate(report["segments"], 1):
        frames = f"{segment['frame_start']}-{segment['frame_end']}"
        print(f"{index:<9} {frames:<12} {labels[segment['rig_status']]:<14} "
              f"{segment['confidence']:<12.4f} {segment['label']}")
    counts = report["rig_comparison"]["segment_counts"]
    print(f"Summary: {counts['match']} match, {counts['mismatch']} mismatch, "
          f"{counts['unknown']} inconclusive")
    print(f"Overlay: {folder / 'overlay.png'}")
    print(f"JSON: {folder / 'verdict.json'}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="ShotCheck: CPU screen-motion evidence through Comfy SDK")
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("run", help="Run the verifier inside local ComfyUI via the official SDK")
    command.add_argument("clip", help="Local clip path visible to both CLI and ComfyUI")
    command.add_argument("--intent", required=True, choices=list(mv.EXPECTED_SCENE_LABEL))
    command.add_argument("--comfy-url", default="http://127.0.0.1:8188")
    command.add_argument("--proxy-url", default="http://127.0.0.1:8000")
    command.add_argument("--out", help="New output directory; existing directories are never overwritten")
    app_command = commands.add_parser(
        "app", help="Serve a localhost page that checks clips with the same verifier as the node",
    )
    app_command.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    if args.command == "app":
        try:
            from .app import serve
            serve(port=args.port)
            return 0
        except Exception as exc:
            print(f"ShotCheck error ({type(exc).__name__}): {exc}", file=sys.stderr)
            print("The app listens on 127.0.0.1 only and needs no ComfyUI, key, or GPU.", file=sys.stderr)
            return 2
    try:
        return run(args)
    except Exception as exc:
        print(f"ShotCheck error ({type(exc).__name__}): {exc}", file=sys.stderr)
        print("Start CPU ComfyUI with the ShotCheck node and the local comfy-api-proxy; no key is needed.",
              file=sys.stderr)
        return 2
