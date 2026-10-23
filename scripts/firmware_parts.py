"""Verify/split or merge the recorded C.22 firmware. Never executes firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.parse
import urllib.request

MANIFEST = Path(__file__).resolve().parents[1] / 'downloads/firmware-c22.json'

def verify(path, item):
    if path.stat().st_size != item['bytes']:
        raise ValueError('Wrong size: ' + path.name)
    with path.open('rb') as f:
        digest = hashlib.sha256()
        for block in iter(lambda: f.read(8*1024*1024), b''):
            digest.update(block)
        value = digest.hexdigest()
    if value != item['sha256']:
        raise ValueError('SHA256 mismatch: ' + path.name)

def download(url, path):
    if path.exists():
        raise ValueError('Refusing to overwrite ' + str(path))
    with urllib.request.urlopen(url, timeout=120) as r, path.open('xb') as out:
        shutil.copyfileobj(r, out, 8*1024*1024)

def split(source, out, meta):
    verify(source, meta)
    out.mkdir(parents=True, exist_ok=True)
    if any((out/p['name']).exists() for p in meta['parts']):
        raise ValueError('Parts already exist; use an empty directory')
    with source.open('rb') as f:
        for part in meta['parts']:
            dest, remaining = out/part['name'], part['bytes']
            with dest.open('xb') as w:
                while remaining:
                    b = f.read(min(8*1024*1024, remaining))
                    if not b:
                        raise ValueError('Source truncated')
                    w.write(b)
                    remaining -= len(b)
            verify(dest, part)
            print('Verified', dest.name, flush=True)
    shutil.copyfile(MANIFEST, out/'firmware-c22.json')

def merge(folder, output, meta):
    if output.exists():
        raise ValueError('Refusing to overwrite ' + str(output))
    for part in meta['parts']:
        verify(folder/part['name'], part)
    temp = output.with_name(output.name + '.assembling')
    with temp.open('xb') as w:
        for part in meta['parts']:
            with (folder/part['name']).open('rb') as f:
                shutil.copyfileobj(f, w, 8*1024*1024)
    verify(temp, meta)
    # Hard link gives atomic no-overwrite behavior on common local filesystems.
    # On unsupported filesystems retain .assembling rather than risking overwrite.
    output.hardlink_to(temp)
    temp.unlink()
    print('Verified complete firmware:', output, flush=True)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('split')
    s.add_argument('source', type=Path)
    s.add_argument('directory', type=Path)
    s = sub.add_parser('mirror-official')
    s.add_argument('directory', type=Path)
    s = sub.add_parser('merge')
    s.add_argument('directory', type=Path)
    s.add_argument('output', type=Path)
    s.add_argument('--download', action='store_true', help='Download missing Release parts first')
    a = p.parse_args()
    meta = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if a.command == 'split':
        split(a.source, a.directory, meta)
    elif a.command == 'mirror-official':
        a.directory.mkdir(parents=True, exist_ok=True)
        source = a.directory/meta['filename']
        if source.exists():
            raise ValueError('Use a fresh directory; firmware download already exists')
        for url in meta['official_urls']:
            try:
                download(url, source)
                verify(source, meta)
                break
            except Exception as e:
                print('Official download failed:', e, flush=True)
                if source.exists():
                    source.unlink()  # Only this command's private download file.
        else:
            raise RuntimeError('All official mirrors failed; use the existing verified local copy')
        split(source, a.directory, meta)
    else:
        if a.download:
            a.directory.mkdir(parents=True, exist_ok=True)
            for part in meta['parts']:
                dest = a.directory/part['name']
                if not dest.exists():
                    download(meta['release_download_base'] + urllib.parse.quote(part['name']), dest)
        merge(a.directory, a.output, meta)

if __name__ == '__main__':
    main()
