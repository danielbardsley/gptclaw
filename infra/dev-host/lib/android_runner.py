#!/usr/bin/env python3
"""Install pinned emulator fixtures as forge; never format or mount project data."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import urllib.request
import zipfile


def unpack(archive, destination, prefix):
    """Validate the complete ZIP inventory before writing any files."""
    with zipfile.ZipFile(archive) as source:
        members = []
        for entry in source.infolist():
            path = PurePosixPath(entry.filename)
            if (path.is_absolute() or ".." in path.parts or "\\" in entry.filename
                    or not path.parts or path.parts[0] != prefix
                    or stat.S_ISLNK(entry.external_attr >> 16)):
                raise ValueError("unsafe archive member")
            relative = Path(*path.parts[1:])
            if relative == Path("."):
                if not entry.is_dir():
                    raise ValueError("invalid archive root")
                continue
            members.append((entry, relative))
        for entry, relative in members:
            target = destination / relative
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.open(entry) as src, target.open("xb") as dst:
                    shutil.copyfileobj(src, dst)
                target.chmod((entry.external_attr >> 16) & 0o777 or 0o644)


def install(base, artifact):
    destination = base / artifact["destination"]
    marker = destination / ".gptclaw-sha256"
    if destination.exists():
        if marker.is_file() and marker.read_text().strip() == artifact["sha256"]:
            return
        raise ValueError("existing SDK destination differs; preserve and inspect")
    cache = base / "downloads"
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / (artifact["sha256"] + ".zip")
    if not archive.exists():
        partial = archive.with_suffix(".partial")
        digest, count = hashlib.sha256(), 0
        try:
            with urllib.request.urlopen(artifact["url"], timeout=120) as src, partial.open("wb") as dst:
                while block := src.read(1024 * 1024):
                    count += len(block)
                    if count > artifact["bytes"]:
                        raise ValueError("artifact exceeds expected size")
                    digest.update(block)
                    dst.write(block)
            if count != artifact["bytes"] or digest.hexdigest() != artifact["sha256"]:
                raise ValueError("artifact checksum/size mismatch")
            partial.rename(archive)
        finally:
            partial.unlink(missing_ok=True)
    with archive.open("rb") as stream:
        if (archive.stat().st_size != artifact["bytes"]
                or hashlib.file_digest(stream, "sha256").hexdigest() != artifact["sha256"]):
            raise ValueError("cached artifact checksum/size mismatch")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".sdk-", dir=destination.parent) as temporary:
        staged = Path(temporary) / "package"
        staged.mkdir()
        unpack(archive, staged, artifact["prefix"])
        (staged / ".gptclaw-sha256").write_text(artifact["sha256"] + "\n")
        staged.rename(destination)


def setup(base, pins):
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    for artifact in pins.values():
        install(base, artifact)
    avd = base / "avd" / "dogstats.avd"
    avd.mkdir(parents=True, exist_ok=True)
    index = base / "avd" / "dogstats.ini"
    index.write_text(f"avd.ini.encoding=UTF-8\npath={avd}\ntarget=android-36\n")
    config = avd / "config.ini"
    if not config.exists():
        config.write_text("\n".join([
            "avd.ini.encoding=UTF-8", "AvdId=dogstats", "abi.type=x86_64",
            "hw.cpu.arch=x86_64", "hw.cpu.ncore=2", "hw.ramSize=3072",
            "hw.lcd.width=1080", "hw.lcd.height=2340", "hw.lcd.density=440",
            "hw.keyboard=yes", "hw.gps=yes", "hw.gpu.enabled=yes",
            "hw.gpu.mode=swiftshader", "hw.audioInput=no", "hw.audioOutput=no",
            "hw.camera.back=none", "hw.camera.front=none", "showDeviceFrame=no",
            "disk.dataPartition.size=4G", "tag.id=google_apis",
            "image.sysdir.1=system-images/android-36/google_apis/x86_64/", "",
        ]))


if __name__ == "__main__":
    if os.geteuid() == 0:
        raise SystemExit("Run Android setup as forge, never root")
    os.umask(0o077)
    setup(Path.home() / "android", json.loads(Path("/etc/gptclaw/android-artifacts.json").read_text()))
    print("Android fixture installed; license acceptance and live boot checks remain required")
