"""Extract only the verified official v27 ARM64 assets; execute nothing."""
import argparse
import hashlib
from pathlib import Path
import zipfile

SHA256 = 'f511bd33d3242911d05b0939f910a3133ef2ba0e0ff1e098128f9f3cd0c16610'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('apk', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    if hashlib.sha256(a.apk.read_bytes()).hexdigest() != SHA256:
        p.error('APK SHA256 does not match the recorded official Magisk v27.0')
    if a.output.exists():
        p.error('Output must be a new directory')
    names = {f'lib/arm64-v8a/lib{n}.so': n for n in
             ('magisk64', 'magiskboot', 'magiskinit', 'magiskpolicy', 'busybox')}
    names.update({f'assets/{n}': n for n in
                  ('stub.apk', 'util_functions.sh', 'boot_patch.sh', 'addon.d.sh', 'bootctl')})
    names['res/p9.sh'] = 'manager.sh'
    with zipfile.ZipFile(a.apk) as z:
        data = {dst: z.read(src) for src, dst in names.items()}
    a.output.mkdir(parents=True)
    for dst, content in data.items():
        (a.output / dst).write_bytes(content)
    print(f'Extracted {len(data)} files to {a.output}; nothing executed')

if __name__ == '__main__':
    main()
