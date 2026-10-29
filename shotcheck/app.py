# SPDX-License-Identifier: MIT
"""Localhost page over the unchanged screen-motion verifier.

CPU only. No GPU, model weights, API key, or socket beyond 127.0.0.1.
Analysis is motion_verifier.analyze_video, the same call the ComfyUI node makes.
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile

from . import motion_verifier as mv

MAX_BYTES = 80 * 1024 * 1024
LOOPBACK = "127.0.0.1"
VERDICT = {"match": "MATCH", "mismatch": "MISMATCH", "unknown": "INCONCLUSIVE"}
INCONCLUSIVE_LINE = (
    "INCONCLUSIVE means the evidence was weak or mixed and is never counted as a pass."
)

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ShotCheck</title>
<style>
:root {
  --paper: #f6f6f2;
  --ink: #222b29;
  --muted: #616963;
  --line: #d2dbd5;
  --card: #fffcf7;
  --green: #0d6f54;
  --green-bg: #e5f4ee;
  --red: #a63a42;
  --red-bg: #fdecee;
  --amber: #8a5a00;
  --amber-bg: #fff4d6;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font: 17px/1.45 "Segoe UI", sans-serif;
}
.wrap { max-width: 1080px; margin: 0 auto; padding: 28px 32px 56px; }
.brand { display: flex; justify-content: space-between; gap: 16px; color: var(--muted); font-size: 14px; letter-spacing: 0.04em; text-transform: uppercase; }
h1 { font-size: 40px; line-height: 1.12; letter-spacing: -0.03em; margin: 10px 0 8px; max-width: 18ch; }
.lead { margin: 0 0 18px; color: var(--muted); max-width: 62ch; }
.legend { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 0 0 18px; }
.legend div { border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; background: var(--card); }
.legend b { display: block; font-size: 15px; letter-spacing: 0.04em; }
.legend .match b { color: var(--green); }
.legend .mismatch b { color: var(--red); }
.legend .inconclusive b { color: var(--amber); }
.legend span { color: var(--muted); font-size: 14px; }
form, .result, .limits { background: var(--card); border: 1px solid var(--line); border-radius: 14px; }
form { padding: 16px; }
.row { display: flex; gap: 12px; align-items: end; flex-wrap: wrap; }
label { display: block; font-size: 13px; color: var(--muted); margin-bottom: 4px; }
select, button, input[type=file] { font: inherit; }
select { min-width: 360px; max-width: 100%; padding: 8px 10px; border-radius: 8px; border: 1px solid var(--line); background: white; color: var(--ink); }
.modes { display: flex; gap: 16px; margin-bottom: 12px; }
.drop {
  flex: 1;
  min-width: 240px;
  position: relative;
  border: 1.5px dashed var(--line);
  border-radius: 10px;
  padding: 16px;
  background: #fbfbf8;
}
.filebtn {
  display: inline-block;
  margin-top: 8px;
  font-size: 14px;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: white;
  cursor: pointer;
}
.sr {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
.drop.hot { border-color: var(--green); background: var(--green-bg); }
.drop strong { display: block; }
.drop p { margin: 4px 0 0; color: var(--muted); font-size: 14px; }
button {
  background: var(--ink);
  color: white;
  border: 0;
  border-radius: 999px;
  padding: 10px 18px;
  cursor: pointer;
}
button:disabled { opacity: 0.55; cursor: wait; }
.hidden { display: none; }
.result { margin-top: 14px; padding: 16px 18px 18px; }
.verdict { font-size: 64px; line-height: 0.95; letter-spacing: -0.04em; margin: 0; }
.verdict.match { color: var(--green); }
.verdict.mismatch { color: var(--red); }
.verdict.inconclusive { color: var(--amber); }
.pair { margin: 8px 0 12px; font-size: 18px; }
.note { margin: 10px 0 0; }
.strip { display: flex; gap: 8px; }
.win { flex: 1; border-radius: 10px; padding: 8px; min-width: 0; }
.win b { display: block; font-size: 13px; }
.win.match { background: var(--green-bg); color: var(--green); }
.win.mismatch { background: var(--red-bg); color: var(--red); }
.win.inconclusive { background: var(--amber-bg); color: var(--amber); }
.win small { display: block; color: var(--ink); font-size: 13px; }
.stage { display: grid; grid-template-columns: minmax(240px, 42%) 1fr; gap: 16px; align-items: start; }
.player { width: 100%; max-height: 320px; background: #1c1915; border-radius: 10px; object-fit: contain; }
.take { display: grid; grid-template-columns: 140px 1.1fr 0.7fr 1fr; gap: 8px; align-items: center; padding: 10px 0; border-top: 1px solid var(--line); }
.take .player { max-height: 78px; }
.dir { display: inline-block; width: 0; height: 0; margin-right: 4px; vertical-align: middle; }
.dir.scene_down { border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 8px solid currentColor; }
.dir.scene_up { border-left: 5px solid transparent; border-right: 5px solid transparent; border-bottom: 8px solid currentColor; }
.dir.scene_left { border-top: 5px solid transparent; border-bottom: 5px solid transparent; border-right: 8px solid currentColor; }
.dir.scene_right { border-top: 5px solid transparent; border-bottom: 5px solid transparent; border-left: 8px solid currentColor; }
.dir.expansion, .dir.contraction, .dir.static, .dir.unknown, .dir.varied { width: auto; height: auto; border: 0; font-size: 14px; }
.take b { font-size: 22px; letter-spacing: 0.03em; }
.take .match { color: var(--green); }
.take .mismatch { color: var(--red); }
.take .inconclusive { color: var(--amber); }
.error { color: var(--red); margin: 10px 0 0; }
.limits { margin-top: 14px; padding: 12px 16px; color: var(--muted); font-size: 14px; }
.limits ul { margin: 6px 0 0; padding-left: 18px; }
@media (max-width: 800px) {
  h1 { font-size: 32px; }
  .legend, .take, .stage { grid-template-columns: 1fr; }
  .verdict { font-size: 48px; }
}
</style>
</head>
<body>
<div class="wrap">
  <div class="brand"><span>ShotCheck</span><span>Local CPU check · nothing is uploaded</span></div>
  <h1>Did the camera move you asked for actually happen?</h1>
  <p class="lead">Drop a clip, pick the move, and read the verdict. ShotCheck does not generate video. Abstaining is a feature.</p>
  <div class="legend">
    <div class="match"><b>MATCH</b><span>Measured screen motion agrees with the move.</span></div>
    <div class="mismatch"><b>MISMATCH</b><span>A measured label contradicts the move.</span></div>
    <div class="inconclusive"><b>INCONCLUSIVE</b><span>Weak or mixed evidence. Never a pass.</span></div>
  </div>
  <form id="check">
    <div class="modes">
      <label><input type="radio" name="mode" value="one" checked> One clip</label>
      <label><input type="radio" name="mode" value="takes"> Compare takes</label>
    </div>
    <div class="row">
      <div>
        <label for="intent">Requested camera move</label>
        <select id="intent" name="intent"></select>
      </div>
      <div class="drop" id="drop">
        <strong id="drop-title">Drop a clip here</strong>
        <p id="drop-detail">or choose a file. Compared takes use one requested move.</p>
        <label id="pick" class="filebtn" for="clip">Choose a clip</label>
        <input id="clip" class="sr" type="file" accept="video/*,.mp4,.mov,.avi,.mkv,.webm,.m4v">
        <input id="takes" class="sr" type="file" accept="video/*,.mp4,.mov,.avi,.mkv,.webm,.m4v" multiple>
      </div>
      <button id="go" type="submit">Check</button>
    </div>
    <p id="error" class="error hidden"></p>
  </form>
  <div id="result" class="result hidden"></div>
  <section class="limits">
    <b>Limits, in the same breath as the verdict</b>
    <ul>
      <li>This measures screen motion, not 3D camera pose.</li>
      <li>In our recorded checks, real pan and dolly clips returned INCONCLUSIVE.</li>
      <li>Not a general accuracy benchmark.</li>
      <li>Clean install verified on a fresh Linux VM (Python 3.13.18, 2026-10-26).</li>
      <li>LTX is not a core model of this app, and this page does not generate video or host a public service.</li>
      <li>INCONCLUSIVE means the evidence was weak or mixed and is never counted as a pass.</li>
    </ul>
  </section>
</div>
<script>
const intent = document.getElementById("intent");
const clip = document.getElementById("clip");
const takes = document.getElementById("takes");
const result = document.getElementById("result");
const error = document.getElementById("error");
const go = document.getElementById("go");
const drop = document.getElementById("drop");

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}
function mode() {
  return document.querySelector("input[name=mode]:checked").value;
}
function files() {
  return mode() === "takes" ? takes.files : clip.files;
}
function showNames() {
  const chosen = files();
  const title = document.getElementById("drop-title");
  title.textContent = chosen.length ? Array.from(chosen).map(file => file.name).join(", ") : (mode() === "takes" ? "Drop several takes" : "Drop a clip here");
}
function setError(message) {
  error.textContent = message || "";
  error.classList.toggle("hidden", !message);
}
const MARK = {expansion: "+", contraction: "-", static: "=", unknown: "?", varied: "~"};
function directionMark(label) {
  const mark = el("span", "dir " + (label || "unknown"));
  if (MARK[label]) mark.textContent = MARK[label];
  return mark;
}
function playerFor(file) {
  const video = document.createElement("video");
  video.className = "player";
  video.muted = true;
  video.loop = true;
  video.autoplay = true;
  video.playsInline = true;
  if (file) video.src = URL.createObjectURL(file);
  return video;
}
function windowCard(row) {
  const card = el("div", "win " + row.verdict.toLowerCase());
  card.append(el("b", "", "Window " + row.index + " · " + row.verdict));
  const detail = el("small", "");
  detail.append(directionMark(row.measured));
  detail.append(document.createTextNode(" " + row.confidence.toFixed(4) + " · " + row.measured));
  card.append(detail);
  return card;
}
function renderOne(payload, root, file) {
  const stage = el("div", "stage");
  stage.append(playerFor(file));
  const readout = el("div", "readout");
  readout.append(el("p", "verdict " + payload.verdict.toLowerCase(), payload.verdict));
  readout.append(el("p", "pair", "Requested " + payload.requested + " (expects " + payload.expected_scene_label + "). Measured " + payload.measured + "."));
  const strip = el("div", "strip");
  payload.windows.forEach(row => strip.append(windowCard(row)));
  readout.append(strip);
  const counts = payload.counts;
  readout.append(el("p", "note", counts.match + " match, " + counts.mismatch + " mismatch, " + counts.unknown + " inconclusive."));
  readout.append(el("p", "note", payload.note));
  stage.append(readout);
  root.append(stage);
}
function fileFor(name, index) {
  const chosen = Array.from(files());
  return chosen.find(file => file.name === name) || chosen[index] || null;
}
function render(payload) {
  result.replaceChildren();
  result.classList.remove("hidden");
  if (payload.takes) {
    result.append(el("p", "pair", "Requested " + payload.requested + " (expects " + payload.expected_scene_label + ")."));
    payload.takes.forEach((take, index) => {
      const row = el("div", "take");
      row.append(playerFor(fileFor(take.filename, index)));
      row.append(el("span", "", take.filename || "clip"));
      if (take.error) {
        row.append(el("b", "mismatch", "ERROR"));
        row.append(el("span", "", take.error));
      } else {
        row.append(el("b", take.verdict.toLowerCase(), take.verdict));
        const measured = el("span", "");
        measured.append(directionMark(take.measured));
        measured.append(document.createTextNode("Measured " + take.measured));
        row.append(measured);
      }
      result.append(row);
    });
    result.append(el("p", "note", payload.note));
    return;
  }
  renderOne(payload, result, fileFor(payload.filename, 0));
}
document.querySelectorAll("input[name=mode]").forEach(input => input.addEventListener("change", () => {
  const several = mode() === "takes";
  const pick = document.getElementById("pick");
  pick.htmlFor = several ? "takes" : "clip";
  pick.textContent = several ? "Choose takes" : "Choose a clip";
  showNames();
}));
clip.addEventListener("change", showNames);
takes.addEventListener("change", showNames);
["dragover", "dragleave", "drop"].forEach(name => drop.addEventListener(name, event => {
  event.preventDefault();
  drop.classList.toggle("hot", name === "dragover");
  if (name === "drop" && event.dataTransfer.files.length) {
    const target = mode() === "takes" ? takes : clip;
    target.files = event.dataTransfer.files;
    showNames();
  }
}));
document.getElementById("check").addEventListener("submit", async event => {
  event.preventDefault();
  setError("");
  if (!files().length) {
    setError("Choose a clip first.");
    return;
  }
  const body = new FormData();
  body.append("intent", intent.value);
  const path = mode() === "takes" ? "/api/takes" : "/api/check";
  Array.from(files()).forEach(file => body.append("clip", file));
  go.disabled = true;
  go.textContent = "Checking";
  try {
    const response = await fetch(path, {method: "POST", body});
    const payload = await response.json();
    if (!response.ok) {
      setError(payload.error || "Check failed.");
      return;
    }
    render(payload);
  } catch (exc) {
    setError("Check failed.");
  } finally {
    go.disabled = false;
    go.textContent = "Check";
  }
});
const RECORDED_INCONCLUSIVE = ["pan_right", "pan_left", "dolly_in", "dolly_out"];
fetch("/api/moves").then(response => response.json()).then(payload => {
  payload.moves.forEach(name => {
    const label = RECORDED_INCONCLUSIVE.includes(name) ? name + " - recorded checks: inconclusive" : name;
    const option = el("option", "", label);
    option.value = name;
    intent.append(option);
  });
});
</script>
</body>
</html>
"""


def headline(counts, n_segments):
    """Present the checker's own segment statuses. No new threshold."""
    if counts["mismatch"]:
        return "MISMATCH"
    if counts["unknown"] or counts["match"] != n_segments or n_segments == 0:
        return "INCONCLUSIVE"
    return "MATCH"


def present(report, filename=""):
    comparison = report["rig_comparison"]
    counts = comparison["segment_counts"]
    windows = []
    for index, segment in enumerate(report["segments"], 1):
        windows.append({
            "index": index,
            "frames": [segment["frame_start"], segment["frame_end"]],
            "verdict": VERDICT[segment["rig_status"]],
            "confidence": segment["confidence"],
            "measured": segment["label"],
            "reasons": list(segment.get("unknown_reasons") or []),
        })
    safe_name = Path(filename).name if filename else ""
    return {
        "filename": safe_name,
        "verdict": headline(counts, len(report["segments"])),
        "requested": comparison["trajectory"],
        "expected_scene_label": comparison["expected_scene_label"],
        "measured": report["overall"]["label"],
        "counts": counts,
        "checker_verdict": comparison["verdict"],
        "windows": windows,
        "note": INCONCLUSIVE_LINE,
    }


def _param(header, key):
    token = key + "="
    at = header.lower().find(token)
    if at < 0:
        return None
    rest = header[at + len(token):].strip()
    if rest.startswith('"'):
        end = rest.find('"', 1)
        return rest[1:end] if end > 0 else rest[1:]
    return rest.split(";", 1)[0].strip()


def parse_form(content_type, body):
    if not content_type or "multipart/form-data" not in content_type.lower():
        raise ValueError("expected a multipart form")
    marker = "boundary="
    at = content_type.lower().find(marker)
    if at < 0:
        raise ValueError("missing multipart boundary")
    boundary = content_type[at + len(marker):].split(";", 1)[0].strip().strip('"')
    if not boundary:
        raise ValueError("missing multipart boundary")
    fields, files = {}, []
    for part in body.split(b"--" + boundary.encode("latin-1")):
        if part.startswith(b"\r\n"):
            part = part[2:]
        if part.endswith(b"\r\n"):
            part = part[:-2]
        if not part or part == b"--":
            continue
        header_blob, sep, data = part.partition(b"\r\n\r\n")
        if not sep:
            continue
        disposition = ""
        for line in header_blob.decode("latin-1", "replace").split("\r\n"):
            if line.lower().startswith("content-disposition:"):
                disposition = line.split(":", 1)[1]
        name = _param(disposition, "name")
        filename = _param(disposition, "filename")
        if not name:
            continue
        if filename is not None and filename != "":
            files.append({"field": name, "filename": Path(filename).name, "data": data})
        else:
            fields.setdefault(name, []).append(data.decode("utf-8", "replace").strip())
    return fields, files


def _intent(fields):
    values = fields.get("intent") or []
    if len(values) != 1:
        raise ValueError("choose one requested camera move")
    try:
        mv.expected_scene_label(values[0])
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
    return values[0]


def check_bytes(data, filename, intent):
    suffix = Path(filename).suffix.lower()
    if suffix not in {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}:
        suffix = ".mp4"
    if not data:
        raise ValueError("the clip was empty")
    temporary = tempfile.NamedTemporaryFile(prefix="shotcheck_", suffix=suffix, delete=False)
    path = temporary.name
    try:
        temporary.write(data)
        temporary.close()
        report = mv.analyze_video(path, rig={"trajectory": intent})
    except (OSError, ValueError) as exc:
        raise ValueError("could not read that clip") from exc
    finally:
        temporary.close()
        Path(path).unlink(missing_ok=True)
    return present(report, filename)


class Handler(BaseHTTPRequestHandler):
    server_version = "ShotCheck"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        return

    def _send(self, code, content_type, payload):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, code, payload):
        self._send(code, "application/json; charset=utf-8", json.dumps(payload, allow_nan=False).encode("utf-8"))

    def _body(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0 or length > MAX_BYTES:
            raise ValueError("clip payload is missing or too large")
        return self.rfile.read(length)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            self._send(200, "text/html; charset=utf-8", PAGE.encode("utf-8"))
            return
        if path == "/api/moves":
            self._json(200, {"moves": list(mv.EXPECTED_SCENE_LABEL)})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        try:
            fields, files = parse_form(self.headers.get("Content-Type"), self._body())
            intent = _intent(fields)
            clips = [item for item in files if item["field"] == "clip"]
            if path == "/api/check":
                if len(clips) != 1:
                    raise ValueError("choose one clip")
                self._json(200, check_bytes(clips[0]["data"], clips[0]["filename"], intent))
                return
            if path == "/api/takes":
                if not clips:
                    raise ValueError("choose at least one clip")
                rows = []
                for item in clips:
                    try:
                        rows.append(check_bytes(item["data"], item["filename"], intent))
                    except ValueError as exc:
                        rows.append({"filename": item["filename"], "error": str(exc)})
                self._json(200, {
                    "requested": intent,
                    "expected_scene_label": mv.expected_scene_label(intent),
                    "note": INCONCLUSIVE_LINE,
                    "takes": rows,
                })
                return
            self._json(404, {"error": "not found"})
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
        except (KeyError, json.JSONDecodeError):
            self._json(400, {"error": "could not read that request"})


def start(host=LOOPBACK, port=8765):
    if host != LOOPBACK:
        raise ValueError("ShotCheck app listens on 127.0.0.1 only")
    httpd = ThreadingHTTPServer((host, port), Handler)
    bound = httpd.server_address[1]
    print(f"ShotCheck app: http://{LOOPBACK}:{bound}/", flush=True)
    print("CPU only. No GPU, model weights, or API key. Requests stay on this machine.", flush=True)
    print(INCONCLUSIVE_LINE, flush=True)
    return httpd


def serve(host=LOOPBACK, port=8765):
    httpd = start(host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
