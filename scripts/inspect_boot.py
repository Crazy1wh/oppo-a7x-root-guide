"""Read-only Android legacy boot v0/v1/v2 inspection. Python standard library."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import zlib

def inspect(data):
    if len(data) < 1632 or data[:8] != b'ANDROID!':
        raise ValueError('Not a complete legacy Android boot image')
    ks, _, rs, _, ss, _, _, page, version = struct.unpack_from('<9I', data, 8)
    if version > 2 or page < 2048 or page & (page - 1):
        raise ValueError('Only legacy v0/v1/v2 with a valid page size is supported')
    align = lambda n: (n + page - 1) // page * page
    h, parts, pos = hashlib.sha1(), [], page
    for n in (ks, rs, ss):
        chunk = data[pos:pos+n]
        if len(chunk) != n:
            raise ValueError('Truncated component')
        parts.append(chunk)
        h.update(chunk)
        h.update(struct.pack('<I', n))
        pos += align(n)
    if version >= 1:
        if len(data) < 1648:
            raise ValueError('Truncated v1 header')
        n, offset = struct.unpack_from('<IQ', data, 1632)
        chunk = data[offset:offset+n] if n else b''
        if len(chunk) != n:
            raise ValueError('Truncated recovery DTBO')
        h.update(chunk)
        h.update(struct.pack('<I', n))
        if n:
            pos = offset + align(n)
    if version == 2:
        if len(data) < 1660:
            raise ValueError('Truncated v2 header')
        n = struct.unpack_from('<I', data, 1648)[0]
        chunk = data[pos:pos+n]
        if len(chunk) != n:
            raise ValueError('Truncated DTB')
        h.update(chunk)
        h.update(struct.pack('<I', n))
    report = dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                  header_version=version, page_size=page, kernel_bytes=ks,
                  ramdisk_bytes=rs, stored_id=data[576:596].hex(),
                  calculated_id=h.hexdigest(), id_matches=h.digest() == data[576:596])
    if parts[0].startswith(b'\x1f\x8b'):
        z = zlib.decompressobj(31)
        kernel = z.decompress(parts[0]) + z.flush()
        if not z.eof:
            raise ValueError('Truncated kernel gzip')
        report.update(kernel_gzip_valid=True, kernel_uncompressed_bytes=len(kernel),
                      appended_kernel_bytes=len(z.unused_data))
    if rs:
        cpio = gzip.decompress(parts[1]) if parts[1].startswith(b'\x1f\x8b') else parts[1]
        if not cpio.startswith(b'070701'):
            raise ValueError('Only newc raw/gzip ramdisks supported')
        names, pos, trailer = [], 0, False
        while pos + 110 <= len(cpio):
            if cpio[pos:pos+6] != b'070701':
                raise ValueError('Bad CPIO header')
            f = [int(cpio[pos+6+i*8:pos+14+i*8], 16) for i in range(13)]
            size, ns = f[6], f[11]
            name_end = pos + 110 + ns
            off = (name_end + 3) // 4 * 4
            if ns < 1 or name_end > len(cpio) or off + size > len(cpio):
                raise ValueError('Truncated CPIO entry')
            name = cpio[pos+110:name_end-1].decode('utf-8', errors='replace')
            if cpio[name_end-1] != 0:
                raise ValueError('CPIO name missing null terminator')
            names.append(name)
            if name == '.backup/.magisk':
                report['magisk_config'] = cpio[off:off+size].decode('utf-8')
            pos = (off + size + 3) // 4 * 4
            if name == 'TRAILER!!!':
                trailer = True
                break
        if not trailer:
            raise ValueError('CPIO trailer missing')
        report['ramdisk_files'] = names
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    a = p.parse_args()
    report = inspect(a.image.read_bytes())
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report['id_matches']:
        raise SystemExit('Legacy image ID mismatch; inspect before using')

if __name__ == '__main__':
    main()
