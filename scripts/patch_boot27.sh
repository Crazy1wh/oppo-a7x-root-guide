#!/system/bin/sh
# Case-specific candidate builder. Run only in /data/local/tmp/<workdir>.
# No partition writes, reboot, installation, or root authorization changes.
set -eu
cd "$(dirname "$0")"
case "$(pwd -P)" in
  /data/local/tmp/*) ;;
  *) echo 'Refusing: use a dedicated /data/local/tmp work directory' >&2; exit 1 ;;
esac
EXPECTED=b43915e5c9a4d00a3611a896754958fc900762d60f2225a1814eff0059b48c76
ACTUAL=$(sha256sum boot.img)
[ "${ACTUAL%% *}" = "$EXPECTED" ] || { echo 'Wrong stock boot SHA256' >&2; exit 1; }
grep -qx "MAGISK_VER='27.0'" util_functions.sh
grep -qx 'MAGISK_VER_CODE=27000' util_functions.sh
[ ! -e new-boot.img ] || { echo 'Use a clean directory; output already exists' >&2; exit 1; }
chmod 0755 magiskboot magiskinit magisk64 busybox magiskpolicy
export KEEPVERITY=true KEEPFORCEENCRYPT=true PATCHVBMETAFLAG=false
export RECOVERYMODE=false LEGACYSAR=true PREINITDEVICE=cache BOOTMODE=true
sh ./boot_patch.sh boot.img
[ -s new-boot.img ]
sha256sum new-boot.img
echo 'Candidate only. Pull, inspect and verify before any manual flashing.'
