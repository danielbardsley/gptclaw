"""Bounded binary AndroidManifest package parser. Signature verification is separate."""
import io
import re
import struct
import zipfile


def package(apk):
    with zipfile.ZipFile(io.BytesIO(apk)) as archive:
        entries = [x for x in archive.infolist() if x.filename == 'AndroidManifest.xml']
        if len(entries) != 1 or entries[0].file_size > 1024 * 1024:
            raise ValueError('Invalid Android manifest')
        data = archive.read(entries[0])
    def u16(pos): return struct.unpack_from('<H', data, pos)[0]
    def u32(pos): return struct.unpack_from('<I', data, pos)[0]
    if len(data) < 8 or u16(0) != 3 or u32(4) != len(data):
        raise ValueError('Invalid binary manifest')
    strings = []
    offset = u16(2)
    while offset + 8 <= len(data):
        kind, header, size = struct.unpack_from('<HHI', data, offset)
        if size < header or header < 8 or offset + size > len(data):
            raise ValueError('Invalid manifest chunk')
        if kind == 1:
            if header < 28:
                raise ValueError('Invalid string pool')
            count, flags, start = u32(offset + 8), u32(offset + 16), u32(offset + 20)
            if count > 65536 or header + count * 4 > size:
                raise ValueError('String pool limit')
            strings = []
            for n in range(count):
                p = offset + start + u32(offset + header + n * 4)
                if not offset <= p < offset + size:
                    raise ValueError('String pool escape')
                if flags & 0x100:
                    # UTF-8 has character count followed by byte count, both variable length.
                    first = data[p]; p += 2 if first & 0x80 else 1
                    length = data[p]; p += 1
                    if length & 0x80: length = ((length & 0x7f) << 8) | data[p]; p += 1
                    end = p + length
                    if end >= offset + size or data[end] != 0:
                        raise ValueError('Invalid UTF-8 pool')
                    strings.append(data[p:end].decode('utf-8'))
                else:
                    length = u16(p); p += 2
                    if length & 0x8000: length = ((length & 0x7fff) << 16) | u16(p); p += 2
                    end = p + length * 2
                    if end + 2 > offset + size or u16(end) != 0:
                        raise ValueError('Invalid UTF-16 pool')
                    strings.append(data[p:end].decode('utf-16-le'))
        elif kind == 0x102:
            if header < 16 or header + 20 > size:
                raise ValueError('Invalid element')
            ext = offset + header
            name, attr_start, attr_size, count = u32(ext + 4), u16(ext + 8), u16(ext + 10), u16(ext + 12)
            if name >= len(strings): raise ValueError('Invalid element name')
            if strings[name] == 'manifest':
                if attr_size < 20 or attr_start + count * attr_size > size - header:
                    raise ValueError('Invalid attributes')
                packages = []
                for n in range(count):
                    a = ext + attr_start + n * attr_size
                    attr_name, raw, typed = u32(a + 4), u32(a + 8), u32(a + 16)
                    if attr_name >= len(strings): raise ValueError('Invalid attribute name')
                    if strings[attr_name] == 'package':
                        if u32(a) != 0xffffffff: raise ValueError('Invalid package namespace')
                        index = raw if raw != 0xffffffff else typed if data[a + 15] == 3 else 0xffffffff
                        if index >= len(strings): raise ValueError('Invalid package value')
                        packages.append(strings[index])
                if len(packages) != 1 or not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)+', packages[0]):
                    raise ValueError('Invalid package')
                return packages[0]
        offset += size
    raise ValueError('Manifest package missing')
