# ShotCheck

## App

Which take to keep. Drop a clip, pick the move, and read MATCH, MISMATCH, or INCONCLUSIVE.

![Compare takes for tilt up: the tilt-up clip is MATCH, pan and dolly are INCONCLUSIVE, and the labeled CC0 control is MISMATCH](docs/compare_takes.jpg)

Check a clip in the browser without starting ComfyUI. From this repository:

```text
python -m shotcheck app
```

After `pip install`, the same server is `shotcheck app` (optional `--port 8765`).
It prints `http://127.0.0.1:8765/` and listens on that host only. CPU only: no GPU,
model weights, API key, or network beyond localhost.

Drop a clip, or several takes of one shot. The demo's keep decision is a tilt
decision: `tilt_up` or `tilt_down`, plus `static`. `pan_right`, `pan_left`,
`dolly_in`, and `dolly_out` stay selectable, and the dropdown labels each one
"recorded checks: inconclusive", because the recorded real pan and dolly clips
returned INCONCLUSIVE. Thresholds are not retuned. The page calls `analyze_video`
with that trajectory, the same function and thresholds as the `ShotCheckMotionVerifier`
node. It does not start a ComfyUI graph; `shotcheck run` remains the SDK path.

The page shows a large MATCH, MISMATCH, or INCONCLUSIVE verdict, the chosen
clip playing muted and looping beside that verdict, a per-window strip with
each window's verdict, confidence, and measured-label direction, and the
measured screen-motion label next to the requested move. INCONCLUSIVE means the evidence was weak or
mixed and is never counted as a pass. Compare takes lists every clip against one
requested move so a creator can keep the take that matches.

Limits, also printed on the page:

- It measures screen motion, not 3D camera pose.
- In our recorded checks, real pan and dolly clips returned INCONCLUSIVE.
- Not a general accuracy benchmark.
- Clean install verified on a fresh Linux VM (Python 3.13.18, 2026-10-26).
- This page does not generate video, host a public service, or use LTX as a core model.

## Node and CLI

Check whether a clip's measured screen motion agrees with an intended camera move.
Run a CPU-only ComfyUI graph through the official Comfy SDK and local API proxy.
Get per-segment match, mismatch or **inconclusive** evidence, JSON and an overlay.

**Abstaining is a feature:** inconclusive means insufficient or mixed evidence,
never a pass. Optical flow is not physical 3D camera pose; scene movement can
mimic a pan/tilt, and a zoom can mimic a dolly. This tool does not generate video.

## Clean Windows setup (PowerShell)

Prerequisites: Python **3.13** from python.org and Git. Place this repository at
`C:\shotcheck-work\shotcheck` before the commands below. Internet is needed only
to download free source/packages; no Comfy account, API key, model weights,
credits, card or GPU is needed. Keep the workspace path accessible to both
processes on the same machine.

```powershell
Set-Location C:\shotcheck-work
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
git clone https://github.com/Comfy-Org/ComfyUI.git
git -C .\ComfyUI checkout 87ed5a066d9c4660ef42100fd01a888da6994856
.\.venv\Scripts\python.exe -m pip install -r .\ComfyUI\requirements.txt
.\.venv\Scripts\python.exe -m pip install .\shotcheck
Copy-Item .\shotcheck .\ComfyUI\custom_nodes\shotcheck -Recurse
.\.venv\Scripts\python.exe .\ComfyUI\main.py --cpu --offline --disable-auto-launch --listen 127.0.0.1 --port 8188
```

Wait for ComfyUI to announce that its server is running. First startup on a
slow CPU may take **up to 20 minutes**. The graph needs no model weights.
In a **second terminal**, start the official local API proxy:

```powershell
C:\shotcheck-work\.venv\Scripts\comfy-api-proxy.exe --comfyui http://127.0.0.1:8188 --port 8000
```

In a **third terminal**, run the bundled CC0 example:

```powershell
C:\shotcheck-work\.venv\Scripts\shotcheck.exe run C:\shotcheck-work\shotcheck\examples\synthetic_tilt_up.avi --intent tilt_up --out C:\shotcheck-work\example-result
```

Expected: four `MATCH` rows; summary `4 match, 0 mismatch, 0 inconclusive`.
The new output folder contains `overlay.png` and `verdict.json`. Existing
output directories are never overwritten; omit `--out` for a unique folder.
Stop ComfyUI and the proxy with Ctrl+C when finished.

## Clean Linux setup

Prerequisites: Git, Python **3.13** and its venv support. Place this repository
in a `shotcheck-work/shotcheck/` workspace. From `shotcheck-work/`:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
git clone https://github.com/Comfy-Org/ComfyUI.git
git -C ComfyUI checkout 87ed5a066d9c4660ef42100fd01a888da6994856
.venv/bin/python -m pip install -r ComfyUI/requirements.txt
.venv/bin/python -m pip install ./shotcheck
cp -R shotcheck ComfyUI/custom_nodes/shotcheck
.venv/bin/python ComfyUI/main.py --cpu --offline --disable-auto-launch --listen 127.0.0.1 --port 8188
```

In separate terminals, also from `shotcheck-work/`:

```bash
.venv/bin/comfy-api-proxy --comfyui http://127.0.0.1:8188 --port 8000
.venv/bin/shotcheck run shotcheck/examples/synthetic_tilt_up.avi --intent tilt_up --out example-result
```

The app path was verified on a fresh Linux VM on 2026-10-26, Python 3.13.18.
A new virtual environment followed the commands in this section, with this
repository copied in place of a clone. From this repository, `python -m shotcheck app`
printed a localhost URL. That page returned HTTP 200. The bundled
`examples/synthetic_tilt_up.avi`, checked as tilt up, returned MATCH, measured
scene_down, 4 of 4, confidence 1.0, the same verdict as on the development
machine. The ComfyUI server, the proxy, and `shotcheck run` were not part of
that recorded check.
ComfyUI upstream setup: https://github.com/Comfy-Org/ComfyUI#manual-install-windows-linux.
The tested upstream revision is `87ed5a066d9c4660ef42100fd01a888da6994856`
(ComfyUI 0.42.0); future upstream revisions may need separate validation.

## Existing ComfyUI installation / node package

Copy the entire repository directory into `ComfyUI/custom_nodes/shotcheck/`.
Install this project with that ComfyUI's Python (`python -m pip install
<copied-directory>`), then restart ComfyUI with `--cpu --offline`.
The root `__init__.py` registers `ShotCheckMotionVerifier`. Its required inputs
are a local video path and intended direction; outputs are JSON text and a CPU
RGB overlay, which connects to `SaveImage`. Do not enable duplicate older
copies of the same node.

CLI graph: `ShotCheckMotionVerifier → SaveImage`. Both CLI and ComfyUI access
the same absolute local video path. The overlay is downloaded through the SDK;
verdict JSON comes from the executed node's native local ComfyUI history,
not a separate verifier call in the CLI. Only HTTP `127.0.0.1` service URLs
are accepted. `COMFY_API_KEY` is ignored/unset for this local run.

```text
shotcheck run CLIP --intent pan_right|pan_left|tilt_up|tilt_down|dolly_in|dolly_out|static
    [--comfy-url http://127.0.0.1:8188]
    [--proxy-url http://127.0.0.1:8000]
    [--out NEW_DIRECTORY]
```

Exit 0 means a report was produced, including mismatch/inconclusive reports.
Exit 2 means execution failed. Each request/job allows 20 minutes. The
verifier's fixed thresholds are not tuned for the supplied clip. JSON retains
the raw `unknown` label; the CLI presents it as **INCONCLUSIVE**, alongside
confidence, measured component values and reasons in the saved report.

## Platform parts used: Comfy SDK and Comfy API v2 (self-hosted ComfyUI via the official comfy-api-proxy)

Real application execution calls `comfy_sdk.Comfy.run()` on the local node
graph, then downloads its `SaveImage` output through the SDK. Uses official
`comfy-sdk==0.5.0` and `comfy-api-proxy==0.1.6`. No Router credits, hosted
deployment, partner API nodes or inference service are involved.

- SDK: https://github.com/Comfy-Org/comfy-python-sdk
- Local proxy ("The Comfy API v2, in front of your own ComfyUI"):
  https://github.com/Comfy-Org/comfy-api-proxy
- ComfyUI: https://github.com/Comfy-Org/ComfyUI (separate GPL-3.0 dependency,
  not vendored here). Our node/CLI are MIT. Organizer acceptance remains the
  organizer's decision; platform use is not a promise of contest eligibility.

## Other tools: LTX-2.5 HF Space clips used only as test inputs (LTX Community License, not redistributed)

Earlier real LTX clips from https://huggingface.co/spaces/Lightricks/LTX-2.5
were external integration-test inputs only. They and their derived overlays
are **not bundled in this repository**. Applicable LTX Community License:
https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x.
No Grok Imagine media is included.

The only bundled video is `examples/synthetic_tilt_up.avi`, our procedural
CC0 control (see `examples/LICENSE.txt`). It is not LTX-generated footage.

## Tests

**Verified environments:** Windows, CPU, Python 3.13.4, existing clean venv: 24/24 tests and real local SDK CLI tilt 4/4. Clean Ubuntu package/unit-test acceptance is covered by `.github/workflows/test.yml` (`ubuntu-latest`, Python 3.12). CI uses a fake SDK transport for CLI tests and does not validate the full ComfyUI/proxy/CLI setup.

From this repository's root, with its environment's Python:

```text
python -m unittest discover -s tests -v
```

Node/control tests execute the real fixed-threshold verifier on generated
OpenCV fixtures. CLI smoke tests use a clearly fake SDK transport, so no
running ComfyUI, key or network is needed. They test match, mismatch,
inconclusive wording, loopback-only routing and no-overwrite behavior.
`TEST_RESULT.json` records fresh-copy commands/results and the separate
real SDK/CLI integration check; fake transport is not passed off as that proof.
