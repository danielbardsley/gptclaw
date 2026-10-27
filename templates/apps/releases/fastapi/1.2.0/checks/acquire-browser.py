"""Acquire only the exact public browser-check artifact with verified integrity."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

source = Path(__file__).resolve().parent
config = json.loads((source / "browser.json").read_text())
with urllib.request.urlopen(config["artifact"]["url"], timeout=30) as response:
    data = response.read(16 * 1024 * 1024 + 1)
if len(data) > 16 * 1024 * 1024:
    raise ValueError("Browser artifact exceeds bound")
expected = config["artifact"]["integrity"].removeprefix("sha512-")
if base64.b64encode(hashlib.sha512(data).digest()).decode() != expected:
    raise ValueError("Browser artifact integrity mismatch")
destination = Path(sys.argv[1])
destination.mkdir()
(destination / "playwright.tgz").write_bytes(data)
(destination / "Containerfile").write_bytes((source / "Browser.Containerfile").read_bytes())

(destination / "axe.min.js").write_bytes((source / "axe.min.js").read_bytes())
