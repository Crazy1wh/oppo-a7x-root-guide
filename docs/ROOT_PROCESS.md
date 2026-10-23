# 完整流程：最终成功的普通 boot 路线

以下命令中的设备选择、路径和镜像均需使用读者自己验证的值。命令假设只连接一台目标手机；多设备请自行添加 `-s`。项目不提供预修补镜像；官方原包见 [下载入口](../downloads/README.md)，禁止用未知来源或其他版本镜像替代。

## 1. 确认条件并记录原始状态

本案例开始时已经解锁 BL，USB 调试与电脑授权可用。最初尚无 Root，因此不能用 `su` 直接读取原始 boot。

```powershell
adb devices -l
adb shell getprop ro.product.model
adb shell getprop ro.build.display.id
adb shell getprop ro.build.fingerprint
adb shell uname -a
adb shell getprop ro.recovery_id
adb shell ls -l /dev/block/platform/bootdevice/by-name
adb reboot bootloader
fastboot getvar unlocked
fastboot getvar secure
fastboot getvar partition-size:boot
fastboot getvar partition-size:recovery
fastboot reboot
```

本机：`unlocked: yes`、`secure: no`；boot 32 MiB，Recovery 64 MiB。这两个 Fastboot 标志不代表全部 OEM 命令可用。

在任何写入前应已有可信原厂 boot 和恢复路径。此次原始 raw boot 在获得 Root 前不可读，使用官方包提取的 boot 作为回退；这不是“Root 前原分区完整备份”。成功 Root 后才补做 raw 备份，见备份文档。

## 2. 找到 C.22 固件并交叉验证

从手机实际 OTA 应用分析更新协议，向官方服务查询到 C.22 包。公开仓库不包含 OTA 会话、设备标识、协议密钥或原始响应。

| 项目 | 值 |
|---|---|
| OTA 版本 | PBBM00_11.C.22_1220_202411251524 |
| 文件名 | PBBM00_11_OTA_1220_all_cUKUfmx0zcSQ.ozip |
| 包大小 | 2827947458 bytes |
| 官方元数据 MD5 | `467d47e11b96fbea9dc83217439ec109` |

[官方 CDN 下载地址](https://gauss-otacostauto-cn.allawnfs.com/remove-206f1bce6bbe35ec5fae7162ae9a0675/ota/24/12/09/2d6aa9ac-6f5a-454a-a025-2adcc943b7c4.ozip)。链接可能失效；包名与 MD5 是这次采集记录，不是其他固件的通用校验值。

先校验整个 OZIP，再通过 [oppo_ozip_decrypt](https://github.com/bkerler/oppo_ozip_decrypt) 等上游工具解密 / 提取。不要仅改扩展名当 ZIP 使用。提取 boot 后用 `inspect_boot.py` 检查。

```powershell
Get-FileHash ./firmware.ozip -Algorithm MD5
adb pull /system/recovery-from-boot.p ./recovery-from-boot.p
python scripts/inspect_boot.py ./stock/boot.img
```

本次 boot：11182960 bytes；SHA256 为 `b43915e5c9a4d00a3611a896754958fc900762d60f2225a1814eff0059b48c76`。头版本 1，page 2048，ramdisk 0，kernel gzip，带附加 DTB。

`recovery-from-boot.p` 是 BSDIFF40 补丁，不是可刷镜像。用 boot 与该补丁重建 Recovery，独立重算 boot / Recovery 镜像 ID，并将重建结果与手机 `ro.recovery_id` 对照。本次匹配的是 `b7b1bc11a07e7acc63e6a7039e4c1a0ab86b93e1`。`ro.expect.recovery_id` 是另一个旧值，不能替代。

```powershell
python scripts/rebuild_recovery.py ./stock/boot.img ./recovery-from-boot.p ./stock/recovery.img --expected-id <本机ro.recovery_id>
```

不同型号标识依然存在：PBBM00 包的整包断言不等于 PBBT00 可刷。这里的证据支持选定镜像的案例验证，不支持整包刷写、其他版本或其他手机。

## 3. 从官方 Magisk 27 提取修补工具

使用 [Magisk v27.0 官方发布](https://github.com/topjohnwu/Magisk/releases/tag/v27.0)，APK SHA256：

`f511bd33d3242911d05b0939f910a3133ef2ba0e0ff1e098128f9f3cd0c16610`

```powershell
python scripts/prepare_magisk27.py ./Magisk-v27.0.apk ./work-magisk27
Copy-Item ./stock/boot.img ./work-magisk27/boot.img
Copy-Item ./scripts/patch_boot27.sh ./work-magisk27/patch_boot27.sh
adb push ./work-magisk27 /data/local/tmp/
adb shell sh /data/local/tmp/work-magisk27/patch_boot27.sh
adb pull /data/local/tmp/work-magisk27/new-boot.img ./magisk27-boot.img
python scripts/inspect_boot.py ./magisk27-boot.img
```

包装脚本限制为这次已验证的 stock boot SHA256 和 v27 资源，防止误用于其他固件；不会替用户刷写。它设置：

```sh
KEEPVERITY=true
KEEPFORCEENCRYPT=true
PATCHVBMETAFLAG=false
RECOVERYMODE=false
LEGACYSAR=true
PREINITDEVICE=cache
```

关键点是 `RECOVERYMODE=false` 和 `LEGACYSAR=true`。v27 原始脚本为普通 boot 创建最小 ramdisk，并在解压内核中将 `skip_initramfs` 改成 `want_initramfs`，使 legacy SAR 内核加载新 ramdisk。本次差异分析只发现该字符串的四字节修改；附加 DTB 一致。不是手工修改若干随机内核地址。

本次成功候选：12004650 bytes、ramdisk 825172 bytes、镜像 ID `ca8673f59845b3e6be29e0807ad0ca9f878f0edc`，SHA256：

`151802e94f07aa810d5138933e8f2e4ac7e442dba488e7081c59047cc1e8ed01`

候选生成后需核对原始 boot、CPIO 配置、镜像 ID、kernel gzip 完整性和设备 / 电脑哈希。整理后的脚本如果生成不同哈希，应先分析差异，不能假设“工具退出 0 就安全”。

## 4. 写入 boot 并验证

这是实际更改启动分区的步骤，应先有本机回退镜像。临时 `fastboot boot` 在本案例没有验证成功，不能用返回 OKAY 代替实际启动确认。

```powershell
adb reboot bootloader
fastboot getvar unlocked
fastboot flash boot ./magisk27-boot.img
# 必须观察 Sending / Writing 均成功；失败时不要继续盲目重启或扩大刷写范围。
fastboot reboot
```

成功普通开机后：

```powershell
adb shell getprop sys.boot_completed
adb shell /sbin/magisk -v
adb shell su -c id
```

实际返回 `1`、`27.0:MAGISK:R`、`uid=0(root) ... context=u:r:magisk:s0`。管理器里对 Shell / ADB shell 授权后，再验证一次。此次无需改写 system、vendor、Recovery 或格式化 userdata。

## 5. 管理器与环境补齐

现场管理器是 30.7，核心是 27。降级安装管理器被 OPPO 拦截 / 超时，最终保留现有 App；在超级用户页打开 Shell 权限后 UID 0 正常。

曾出现 `/data/adb/magisk` 为空，导致环境不完整。使用 v27 APK 自带文件和该 APK 内部管理器脚本的 `fix_env` 初始化，随后 `env_check 27.0 27000` 返回 0。该版本内部脚本在 APK 的 `res/p9.sh`，不是固定上游通用路径；不能从其他版本随意替换。

`fix_env` 会清理并重建 `$MAGISKBIN`，因此没有提供通用自动执行脚本。若需重做：先确定核心是 27、备份 `/data/adb/magisk`，核实 `NVBASE=/data/adb`、`MAGISKBIN=/data/adb/magisk`、`MAGISKTMP=/sbin`，仅向独立 staging 目录放 v27 文件，再由同版管理器脚本执行 `fix_env` / `env_check`。不要把 App 30.7 的“修复环境”当作安装 v27 的等价步骤，也不要混用任意版本文件。

## 6. 重启保持与后续备份

```powershell
adb reboot
# 等待正常启动，不要用无限等待掩盖启动失败。
adb devices
adb shell getprop sys.boot_completed
adb shell /sbin/magisk -v
adb shell su -c id
```

本次约 26.7 秒 ADB 自动返回，boot_completed=1、USB=mtp,adb、核心 27.0、UID 0 均再次通过。随后完成分区备份；来电自启为单独后续实验，不是 Root 必需步骤。
