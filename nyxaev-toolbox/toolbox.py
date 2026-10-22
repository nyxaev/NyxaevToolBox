"""NYXAEV Toolbox: a local web panel built with the standard library only.

Author: NYXAEV
Dependencies: none (http.server, json, secrets, uuid, argparse).

Run `python toolbox.py` and the panel opens in your default browser. The
server only listens on 127.0.0.1, so nothing is exposed to your network.
"""

import argparse
import json
import math
import secrets
import string
import sys
import threading
import uuid
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, List, Optional, Sequence

SIGNATURE: str = "NYXAEV"
HOST: str = "127.0.0.1"
DEFAULT_PORT: int = 8765
PORT_ATTEMPTS: int = 10
MAX_BODY_BYTES: int = 1_000_000
AMBIGUOUS_CHARS: str = "Il1O0o"
SYMBOL_CHARS: str = "!@#$%^&*()-_=+[]{};:,.?/"

UUID_NAMESPACES: Dict[str, uuid.UUID] = {
    "dns": uuid.NAMESPACE_DNS,
    "url": uuid.NAMESPACE_URL,
    "oid": uuid.NAMESPACE_OID,
    "x500": uuid.NAMESPACE_X500,
}

Payload = Dict[str, Any]

HTML_PAGE: str = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NYXAEV Toolbox</title>
<style>
:root {
  --bg: #0d1117;
  --panel: #161b22;
  --panel-soft: #1c232d;
  --line: #2a313c;
  --text: #e6edf3;
  --muted: #8b949e;
  --accent: #7c5cff;
  --accent-soft: #22d3ee;
  --ok: #3fb950;
  --err: #f85149;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 28px 20px 40px;
  background: radial-gradient(1200px 600px at 10% -10%, #1b1442 0%, transparent 60%), var(--bg);
  color: var(--text);
  font: 15px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
header {
  max-width: 1180px;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
h1 { margin: 0; font-size: 26px; letter-spacing: 0.4px; }
header p { margin: 4px 0 0; color: var(--muted); }
.badge {
  padding: 6px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--accent-soft);
  font-weight: 600;
  letter-spacing: 1.5px;
  background: var(--panel);
}
main {
  max-width: 1180px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 18px;
}
.card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.card.wide { grid-column: 1 / -1; }
h2 { margin: 0; font-size: 17px; }
h2 span { color: var(--accent-soft); }
.hint { margin: -6px 0 0; color: var(--muted); font-size: 13px; }
.row { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
.field { display: flex; flex-direction: column; gap: 6px; flex: 1 1 140px; }
.field label, .checks label { color: var(--muted); font-size: 13px; }
.checks { display: flex; flex-wrap: wrap; gap: 8px 16px; }
.checks label { display: flex; align-items: center; gap: 6px; cursor: pointer; }
input[type="number"], input[type="text"], select, textarea {
  width: 100%;
  background: var(--panel-soft);
  color: var(--text);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 9px 10px;
  font: inherit;
}
input:focus, select:focus, textarea:focus { outline: 2px solid var(--accent); outline-offset: 0; }
input[type="range"] { width: 100%; accent-color: var(--accent); }
input[type="checkbox"] { accent-color: var(--accent); }
textarea {
  min-height: 260px;
  resize: vertical;
  font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
button {
  border: 0;
  border-radius: 8px;
  padding: 9px 16px;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  color: #fff;
  background: linear-gradient(135deg, var(--accent), #5b8cff);
}
button:hover { filter: brightness(1.1); }
button.ghost {
  background: transparent;
  color: var(--accent-soft);
  border: 1px solid var(--line);
  padding: 5px 10px;
  font-size: 12px;
}
.results { display: flex; flex-direction: column; gap: 6px; }
.result {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  background: var(--panel-soft);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 6px 8px 6px 10px;
}
.result code {
  font: 13px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  word-break: break-all;
}
.status { min-height: 20px; color: var(--muted); font-size: 13px; }
.status.ok { color: var(--ok); }
.status.err { color: var(--err); }
.split { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px; }
.hidden { display: none; }
footer { max-width: 1180px; margin: 24px auto 0; color: var(--muted); font-size: 13px; text-align: center; }
</style>
</head>
<body>
<header>
  <div>
    <h1>__SIGNATURE__ Toolbox</h1>
    <p>Small utilities running on your own machine. Nothing leaves it.</p>
  </div>
  <span class="badge">by __SIGNATURE__</span>
</header>

<main>
  <section class="card">
    <h2><span>01</span> Password generator</h2>
    <p class="hint">Built with the secrets module, a cryptographically secure source.</p>
    <div class="field">
      <label for="pw-length">Length: <strong id="pw-length-value">20</strong></label>
      <input id="pw-length" type="range" min="8" max="128" value="20">
    </div>
    <div class="checks">
      <label><input id="pw-lower" type="checkbox" checked> a-z</label>
      <label><input id="pw-upper" type="checkbox" checked> A-Z</label>
      <label><input id="pw-digits" type="checkbox" checked> 0-9</label>
      <label><input id="pw-symbols" type="checkbox" checked> Symbols</label>
      <label><input id="pw-ambiguous" type="checkbox"> Avoid look-alikes</label>
    </div>
    <div class="row">
      <div class="field" style="flex: 0 0 90px;">
        <label for="pw-count">How many</label>
        <input id="pw-count" type="number" min="1" max="20" value="3">
      </div>
      <button id="pw-generate" type="button">Generate</button>
    </div>
    <div id="pw-results" class="results"></div>
    <div id="pw-meta" class="status"></div>
  </section>

  <section class="card">
    <h2><span>02</span> UUID generator</h2>
    <p class="hint">Random (v4), time-based (v1) or name-based (v3, v5) identifiers.</p>
    <div class="row">
      <div class="field">
        <label for="uuid-version">Version</label>
        <select id="uuid-version">
          <option value="4">v4 - random</option>
          <option value="1">v1 - time based</option>
          <option value="5">v5 - name based (SHA-1)</option>
          <option value="3">v3 - name based (MD5)</option>
        </select>
      </div>
      <div class="field" style="flex: 0 0 90px;">
        <label for="uuid-count">How many</label>
        <input id="uuid-count" type="number" min="1" max="100" value="5">
      </div>
    </div>
    <div id="uuid-named" class="row hidden">
      <div class="field">
        <label for="uuid-namespace">Namespace</label>
        <select id="uuid-namespace">
          <option value="dns">DNS</option>
          <option value="url">URL</option>
          <option value="oid">OID</option>
          <option value="x500">X.500</option>
        </select>
      </div>
      <div class="field">
        <label for="uuid-name">Name</label>
        <input id="uuid-name" type="text" placeholder="example.com">
      </div>
    </div>
    <div class="checks">
      <label><input id="uuid-upper" type="checkbox"> Uppercase</label>
      <label><input id="uuid-hyphens" type="checkbox" checked> Hyphens</label>
    </div>
    <div class="row">
      <button id="uuid-generate" type="button">Generate</button>
      <button id="uuid-copy-all" class="ghost" type="button">Copy all</button>
    </div>
    <div id="uuid-results" class="results"></div>
    <div id="uuid-meta" class="status"></div>
  </section>

  <section class="card wide">
    <h2><span>03</span> JSON workbench</h2>
    <p class="hint">Format, minify or validate. Errors point to the exact line and column.</p>
    <div class="row">
      <div class="field">
        <label for="json-action">Action</label>
        <select id="json-action">
          <option value="format">Format</option>
          <option value="minify">Minify</option>
          <option value="validate">Validate only</option>
        </select>
      </div>
      <div class="field">
        <label for="json-indent">Indent</label>
        <select id="json-indent">
          <option value="2">2 spaces</option>
          <option value="4">4 spaces</option>
          <option value="8">8 spaces</option>
          <option value="tab">Tab</option>
        </select>
      </div>
      <div class="checks" style="flex: 1 1 140px;">
        <label><input id="json-sort" type="checkbox"> Sort keys</label>
      </div>
      <button id="json-run" type="button">Run</button>
      <button id="json-copy" class="ghost" type="button">Copy output</button>
    </div>
    <div class="split">
      <textarea id="json-input" spellcheck="false" placeholder='Paste JSON here, e.g. {"name": "NYXAEV", "tools": [1, 2, 3]}'></textarea>
      <textarea id="json-output" spellcheck="false" readonly placeholder="Result appears here"></textarea>
    </div>
    <div id="json-meta" class="status"></div>
  </section>
</main>

<footer>Made by __SIGNATURE__ - running locally on 127.0.0.1</footer>

<script>
const $ = (id) => document.getElementById(id);

async function callApi(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

function setStatus(element, message, kind) {
  element.textContent = message;
  element.className = "status" + (kind ? " " + kind : "");
}

async function copyText(text, button) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (error) {
    const helper = document.createElement("textarea");
    helper.value = text;
    document.body.append(helper);
    helper.select();
    document.execCommand("copy");
    helper.remove();
  }
  if (button) {
    const original = button.textContent;
    button.textContent = "Copied";
    setTimeout(() => { button.textContent = original; }, 1100);
  }
}

function renderList(container, items) {
  container.replaceChildren();
  items.forEach((value) => {
    const row = document.createElement("div");
    row.className = "result";
    const code = document.createElement("code");
    code.textContent = value;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "ghost";
    button.textContent = "Copy";
    button.addEventListener("click", () => copyText(value, button));
    row.append(code, button);
    container.append(row);
  });
}

let lastUuids = [];

async function generatePasswords() {
  try {
    const data = await callApi("/api/password", {
      length: Number($("pw-length").value),
      count: Number($("pw-count").value),
      lowercase: $("pw-lower").checked,
      uppercase: $("pw-upper").checked,
      digits: $("pw-digits").checked,
      symbols: $("pw-symbols").checked,
      avoid_ambiguous: $("pw-ambiguous").checked
    });
    renderList($("pw-results"), data.passwords);
    setStatus($("pw-meta"), data.entropy_bits + " bits of entropy - " + data.strength, "ok");
  } catch (error) {
    $("pw-results").replaceChildren();
    setStatus($("pw-meta"), error.message, "err");
  }
}

async function generateUuids() {
  try {
    const data = await callApi("/api/uuid", {
      version: $("uuid-version").value,
      count: Number($("uuid-count").value),
      uppercase: $("uuid-upper").checked,
      hyphens: $("uuid-hyphens").checked,
      namespace: $("uuid-namespace").value,
      name: $("uuid-name").value
    });
    lastUuids = data.uuids;
    renderList($("uuid-results"), data.uuids);
    setStatus($("uuid-meta"), data.note || data.uuids.length + " generated", "ok");
  } catch (error) {
    lastUuids = [];
    $("uuid-results").replaceChildren();
    setStatus($("uuid-meta"), error.message, "err");
  }
}

async function runJson() {
  const meta = $("json-meta");
  try {
    const data = await callApi("/api/json", {
      text: $("json-input").value,
      action: $("json-action").value,
      indent: $("json-indent").value,
      sort_keys: $("json-sort").checked
    });
    if (!data.ok) {
      setStatus(meta, data.error + " (line " + data.line + ", column " + data.column + ")", "err");
      return;
    }
    if (data.output !== null) {
      $("json-output").value = data.output;
    }
    setStatus(meta, data.summary, "ok");
  } catch (error) {
    setStatus(meta, error.message, "err");
  }
}

$("pw-length").addEventListener("input", () => {
  $("pw-length-value").textContent = $("pw-length").value;
});
$("pw-generate").addEventListener("click", generatePasswords);

$("uuid-version").addEventListener("change", () => {
  const named = ["3", "5"].includes($("uuid-version").value);
  $("uuid-named").classList.toggle("hidden", !named);
});
$("uuid-generate").addEventListener("click", generateUuids);
$("uuid-copy-all").addEventListener("click", (event) => {
  if (lastUuids.length) {
    copyText(lastUuids.join("\n"), event.currentTarget);
  }
});

$("json-run").addEventListener("click", runJson);
$("json-copy").addEventListener("click", (event) => {
  const text = $("json-output").value;
  if (text) {
    copyText(text, event.currentTarget);
  }
});

generatePasswords();
generateUuids();
</script>
</body>
</html>
"""


class ApiError(Exception):
    """Raised when a request payload is invalid and should return HTTP 400."""


def read_int(payload: Payload, key: str, default: int, low: int, high: int) -> int:
    """Read a bounded integer from a payload.

    Args:
        payload: Decoded JSON body.
        key: Name of the field to read.
        default: Value used when the field is missing.
        low: Smallest accepted value.
        high: Largest accepted value.

    Returns:
        The validated integer.

    Raises:
        ApiError: If the value is not an integer or is out of range.
    """
    raw = payload.get(key, default)
    if isinstance(raw, bool):
        raise ApiError(f"'{key}' must be a number.")
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ApiError(f"'{key}' must be a number.") from None
    if not low <= value <= high:
        raise ApiError(f"'{key}' must be between {low} and {high}.")
    return value


def describe_strength(entropy_bits: float) -> str:
    """Translate an entropy value into a human-friendly label.

    Args:
        entropy_bits: Estimated entropy in bits.

    Returns:
        A short strength label.
    """
    if entropy_bits < 40:
        return "weak"
    if entropy_bits < 60:
        return "fair"
    if entropy_bits < 80:
        return "strong"
    if entropy_bits < 110:
        return "very strong"
    return "excellent"


def generate_passwords(payload: Payload) -> Payload:
    """Generate secure passwords that use every selected character set.

    Args:
        payload: Options: length, count, lowercase, uppercase, digits,
            symbols and avoid_ambiguous.

    Returns:
        A dict with the passwords, their entropy in bits and a strength label.

    Raises:
        ApiError: If the options are invalid or no character set is selected.
    """
    length = read_int(payload, "length", 20, 8, 128)
    count = read_int(payload, "count", 3, 1, 20)
    selected = (
        (payload.get("lowercase", True), string.ascii_lowercase),
        (payload.get("uppercase", True), string.ascii_uppercase),
        (payload.get("digits", True), string.digits),
        (payload.get("symbols", True), SYMBOL_CHARS),
    )
    pools: List[str] = [chars for enabled, chars in selected if enabled]
    if not pools:
        raise ApiError("Select at least one character set.")
    if payload.get("avoid_ambiguous", False):
        pools = ["".join(c for c in pool if c not in AMBIGUOUS_CHARS) for pool in pools]

    alphabet = "".join(pools)
    shuffler = secrets.SystemRandom()
    passwords: List[str] = []
    for _ in range(count):
        chars = [secrets.choice(pool) for pool in pools]
        chars += [secrets.choice(alphabet) for _ in range(length - len(chars))]
        shuffler.shuffle(chars)
        passwords.append("".join(chars))

    entropy = length * math.log2(len(alphabet))
    return {
        "passwords": passwords,
        "entropy_bits": round(entropy),
        "strength": describe_strength(entropy),
    }


def format_uuid(value: uuid.UUID, uppercase: bool, hyphens: bool) -> str:
    """Render a UUID according to the chosen display options.

    Args:
        value: The UUID to render.
        uppercase: Whether to use uppercase hex digits.
        hyphens: Whether to keep the hyphens.

    Returns:
        The formatted UUID string.
    """
    text = str(value) if hyphens else value.hex
    return text.upper() if uppercase else text


def generate_uuids(payload: Payload) -> Payload:
    """Generate UUIDs of the requested version.

    Args:
        payload: Options: version, count, uppercase, hyphens, namespace
            and name (the last two only for versions 3 and 5).

    Returns:
        A dict with the UUID strings and an optional note.

    Raises:
        ApiError: If the options are invalid.
    """
    version = str(payload.get("version", "4"))
    count = read_int(payload, "count", 5, 1, 100)
    note = ""
    values: List[uuid.UUID]

    if version == "4":
        values = [uuid.uuid4() for _ in range(count)]
    elif version == "1":
        values = [uuid.uuid1() for _ in range(count)]
    elif version in {"3", "5"}:
        name = str(payload.get("name", "")).strip()
        if not name:
            raise ApiError("A name is required for UUID v3 and v5.")
        namespace = UUID_NAMESPACES.get(str(payload.get("namespace", "dns")))
        if namespace is None:
            raise ApiError("Unknown namespace.")
        builder = uuid.uuid3 if version == "3" else uuid.uuid5
        values = [builder(namespace, name)]
        note = "Name-based UUIDs are deterministic, so only one is returned."
    else:
        raise ApiError("Unsupported UUID version.")

    uppercase = bool(payload.get("uppercase", False))
    hyphens = bool(payload.get("hyphens", True))
    return {
        "uuids": [format_uuid(value, uppercase, hyphens) for value in values],
        "note": note,
    }


def describe_json(data: Any, size: int) -> str:
    """Summarize a parsed JSON document in one line.

    Args:
        data: The parsed JSON value.
        size: Size of the source text in bytes.

    Returns:
        A short human-readable summary.
    """
    if isinstance(data, dict):
        kind = f"object with {len(data)} keys"
    elif isinstance(data, list):
        kind = f"array with {len(data)} items"
    else:
        kind = type(data).__name__
    return f"Valid JSON - {kind} - {size} bytes"


def process_json(payload: Payload) -> Payload:
    """Format, minify or validate a JSON document.

    Args:
        payload: Options: text, action (format, minify or validate),
            indent (2, 4, 8 or tab) and sort_keys.

    Returns:
        A dict with ok=True, the output text and a summary, or ok=False with
        the parser error and its line and column.

    Raises:
        ApiError: If the options are invalid.
    """
    text = payload.get("text", "")
    if not isinstance(text, str) or not text.strip():
        raise ApiError("Paste some JSON first.")
    action = str(payload.get("action", "format"))
    if action not in {"format", "minify", "validate"}:
        raise ApiError("Unknown action.")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        return {"ok": False, "error": error.msg, "line": error.lineno, "column": error.colno}

    sort_keys = bool(payload.get("sort_keys", False))
    output: Optional[str]
    if action == "validate":
        output = None
    elif action == "minify":
        output = json.dumps(data, separators=(",", ":"), ensure_ascii=False, sort_keys=sort_keys)
    else:
        indent_raw = str(payload.get("indent", "2"))
        indent: Any = "\t" if indent_raw == "tab" else read_int({"indent": indent_raw}, "indent", 2, 1, 8)
        output = json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=sort_keys)

    return {
        "ok": True,
        "output": output,
        "summary": describe_json(data, len(text.encode("utf-8"))),
    }


ROUTES: Dict[str, Callable[[Payload], Payload]] = {
    "/api/password": generate_passwords,
    "/api/uuid": generate_uuids,
    "/api/json": process_json,
}


class ToolboxHandler(BaseHTTPRequestHandler):
    """Serve the embedded page and the small JSON API behind it."""

    server_version = "NYXAEVToolbox/1.0"
    sys_version = ""

    def do_GET(self) -> None:
        """Handle GET requests: the page itself and a health check."""
        if not self._host_is_allowed():
            return
        if self.path in {"/", "/index.html"}:
            page = HTML_PAGE.replace("__SIGNATURE__", SIGNATURE)
            self._send(HTTPStatus.OK, page.encode("utf-8"), "text/html; charset=utf-8")
        elif self.path == "/health":
            self._send_json(HTTPStatus.OK, {"status": "ok", "author": SIGNATURE})
        else:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

    def do_POST(self) -> None:
        """Handle POST requests for the API routes."""
        if not self._host_is_allowed():
            return
        route = ROUTES.get(self.path)
        if route is None:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
            return
        if not self.headers.get("Content-Type", "").startswith("application/json"):
            self._send_json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "Use application/json."})
            return
        try:
            payload = self._read_payload()
            self._send_json(HTTPStatus.OK, route(payload))
        except ApiError as error:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})

    def log_message(self, format: str, *args: Any) -> None:
        """Print a compact request log line.

        Args:
            format: printf-style message format.
            *args: Values for the format string.
        """
        print(f"[{SIGNATURE}] {self.address_string()} - {format % args}")

    def _host_is_allowed(self) -> bool:
        """Reject requests whose Host header is not local.

        Returns:
            True when the request may continue.
        """
        allowed = getattr(self.server, "allowed_hosts", set())
        if self.headers.get("Host", "") in allowed:
            return True
        self._send_json(HTTPStatus.FORBIDDEN, {"error": "Forbidden host."})
        return False

    def _read_payload(self) -> Payload:
        """Read and decode the JSON request body.

        Returns:
            The decoded JSON object.

        Raises:
            ApiError: If the body is missing, too large or not a JSON object.
        """
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ApiError("Invalid Content-Length.") from None
        if length <= 0:
            raise ApiError("Empty request body.")
        if length > MAX_BODY_BYTES:
            raise ApiError("Request body is too large.")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ApiError("Request body is not valid JSON.") from None
        if not isinstance(payload, dict):
            raise ApiError("Request body must be a JSON object.")
        return payload

    def _send_json(self, status: HTTPStatus, data: Payload) -> None:
        """Send a JSON response.

        Args:
            status: HTTP status to return.
            data: Object to serialize.
        """
        self._send(status, json.dumps(data).encode("utf-8"), "application/json; charset=utf-8")

    def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        """Send a complete response with safe default headers.

        Args:
            status: HTTP status to return.
            body: Raw response body.
            content_type: Value for the Content-Type header.
        """
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'",
        )
        self.end_headers()
        self.wfile.write(body)


class ToolboxServer(ThreadingHTTPServer):
    """Threaded HTTP server bound to the loopback interface only."""

    daemon_threads = True

    def __init__(self, port: int) -> None:
        """Bind the server.

        Args:
            port: TCP port to listen on.
        """
        super().__init__((HOST, port), ToolboxHandler)
        self.allowed_hosts = {f"{HOST}:{port}", f"localhost:{port}"}


def start_server(first_port: int) -> Optional[ToolboxServer]:
    """Bind the server, trying the next ports when one is busy.

    Args:
        first_port: Preferred TCP port.

    Returns:
        A bound server, or None if every attempt failed.
    """
    for port in range(first_port, first_port + PORT_ATTEMPTS):
        try:
            return ToolboxServer(port)
        except OSError:
            print(f"[{SIGNATURE}] Port {port} is busy, trying the next one...")
    return None


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list; defaults to sys.argv.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description=f"{SIGNATURE} Toolbox - local web utilities.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="preferred port")
    parser.add_argument("--no-browser", action="store_true", help="do not open the browser")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Start the toolbox and serve until interrupted.

    Args:
        argv: Optional argument list for testing.

    Returns:
        Process exit code.
    """
    args = parse_args(argv)
    server = start_server(args.port)
    if server is None:
        print(f"[{SIGNATURE}] Could not find a free port. Try --port with another value.")
        return 1

    url = f"http://{HOST}:{server.server_address[1]}"
    print(f"[{SIGNATURE}] Toolbox running at {url}")
    print(f"[{SIGNATURE}] Press Ctrl+C to stop")
    if not args.no_browser:
        threading.Timer(0.6, webbrowser.open, args=(url,)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n[{SIGNATURE}] Shutting down. Goodbye!")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
