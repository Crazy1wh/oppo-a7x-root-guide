"""Reconstruct BSDIFF40 recovery offline, require exact known phone image ID."""
import argparse
import bz2
import hashlib
from pathlib import Path
import re
from inspect_boot import inspect

def number(b):
    if len(b) != 8:
        raise ValueError('Truncated BSDIFF number')
    n = int.from_bytes(b, 'little')
    return -(n & ((1 << 63)-1)) if n >> 63 else n

def rebuild(old, patch):
    if patch[:8] != b'BSDIFF40':
        raise ValueError('Not BSDIFF40')
    cl, dl, size = [number(patch[i:i+8]) for i in (8, 16, 24)]
    if min(cl, dl, size) < 0 or size > 128*1024*1024 or 32+cl+dl > len(patch):
        raise ValueError('Invalid patch lengths')
    control = bz2.decompress(patch[32:32+cl])
    diff = bz2.decompress(patch[32+cl:32+cl+dl])
    extra = bz2.decompress(patch[32+cl+dl:])
    if len(control) % 24:
        raise ValueError('Truncated control stream')
    out, oldpos, di, ei = bytearray(), 0, 0, 0
    for i in range(0, len(control), 24):
        x, y, z = [number(control[k:k+8]) for k in (i, i+8, i+16)]
        if min(x, y) < 0 or len(out)+x+y > size or di+x > len(diff) or ei+y > len(extra):
            raise ValueError('Invalid patch controls')
        out.extend((diff[di+j] + (old[oldpos+j] if 0 <= oldpos+j < len(old) else 0)) & 255 for j in range(x))
        di += x
        oldpos += x
        out.extend(extra[ei:ei+y])
        ei += y
        oldpos += z
    if len(out) != size:
        raise ValueError('Incomplete recovery')
    return bytes(out)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('boot', 'patch', 'output'):
        p.add_argument(name, type=Path)
    p.add_argument('--expected-id', required=True)
    a = p.parse_args()
    value = a.expected_id.lower().removeprefix('0x')
    if not re.fullmatch('[0-9a-f]{40}(?:0{24})?', value):
        p.error('Expected 40 hex image ID, optionally with 0x prefix / zero tail')
    if a.output.exists():
        p.error('Output exists; refusing overwrite')
    old = a.boot.read_bytes()
    if not inspect(old)['id_matches']:
        raise ValueError('Source boot image ID mismatch')
    result = rebuild(old, a.patch.read_bytes())
    info = inspect(result)
    if not info['id_matches'] or info['calculated_id'] != value[:40]:
        raise ValueError('Recovery does not match the supplied phone ID')
    a.output.write_bytes(result)
    print('Verified recovery:', len(result), 'bytes; SHA256', hashlib.sha256(result).hexdigest())

if __name__ == '__main__':
    main()
