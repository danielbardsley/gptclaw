#!/usr/bin/env python3
"""Bounded synthetic Android binary manifest parsing; no native execution."""
import io
from pathlib import Path
import struct
import sys
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import apk_metadata


def fixture(package='dev.gptclaw.synthetic.development'):
    strings = ['manifest', 'package', package]
    blobs = [bytes([len(s), len(s)]) + s.encode() + b'\0' for s in strings]
    body = b''.join(blobs); body += b'\0' * (-len(body) % 4)
    offsets = [0, len(blobs[0]), len(blobs[0]) + len(blobs[1])]
    pool = struct.pack('<HHIIIIII', 1, 28, 40 + len(body), 3, 0, 256, 40, 0)
    pool += struct.pack('<III', *offsets) + body
    element = struct.pack('<HHIII', 0x102, 16, 56, 1, 0xffffffff)
    element += struct.pack('<IIHHHHHH', 0xffffffff, 0, 20, 20, 1, 0, 0, 0)
    element += struct.pack('<IIIHBBI', 0xffffffff, 1, 2, 8, 0, 3, 2)
    end = struct.pack('<HHIIIII', 0x103, 16, 24, 1, 0xffffffff, 0xffffffff, 0)
    chunks = pool + element + end
    manifest = struct.pack('<HHI', 3, 8, 8 + len(chunks)) + chunks
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr('AndroidManifest.xml', manifest)
        z.writestr('classes.dex', b'Synthetic fixture: never executed')
    return out.getvalue()


class Tests(unittest.TestCase):
    def test_package_from_unsigned_synthetic_apk(self):
        self.assertEqual(apk_metadata.package(fixture()), 'dev.gptclaw.synthetic.development')

    def test_bad_identity_and_missing_zip_refuse(self):
        for data in [fixture('../escape'), b'not a zip']:
            with self.assertRaises((ValueError, zipfile.BadZipFile)):
                apk_metadata.package(data)

    def test_truncated_binary_manifest_and_missing_manifest_refuse(self):
        for manifest in [b'\x03\x00', b'\x03\x00\x08\x00' + b'\xff' * 8]:
            out = io.BytesIO()
            with zipfile.ZipFile(out, 'w') as z: z.writestr('AndroidManifest.xml', manifest)
            with self.assertRaises(ValueError): apk_metadata.package(out.getvalue())
        out = io.BytesIO()
        with zipfile.ZipFile(out, 'w') as z: z.writestr('not-a-manifest', b'')
        with self.assertRaises(ValueError): apk_metadata.package(out.getvalue())


if __name__ == '__main__': unittest.main()
