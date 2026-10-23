# OPPO A7x PBBT00 C.22 Root 实战记录

记录一台已解锁 Bootloader 的 OPPO A7x，在找不到对应刷机包、USB 每次只充电、Recovery Root 失败的情况下，最终通过 **Magisk 27 + 普通 boot 最小 ramdisk + legacy SAR 内核补丁** 获得可重启保持的 Root。

这是单台设备的研究记录，不是 OPPO 全机型通刷包。仓库不提供刷机镜像、设备 NV 备份、破解解锁工具或一键刷写脚本。

## 实测设备与结果

| 项目 | 实测值 |
|---|---|
| 型号 / 平台 | OPPO A7x PBBT00 / MT6771（Helio P60） |
| 系统 | Android 9 / ColorOS 6 |
| 显示版本 | PBBT00_11_C.22 |
| 内核 | 4.4.146+，构建日期 2024-11-25 |
| 布局 | A-only、legacy system-as-root，原 boot ramdisk 为 0 |
| 前提 | Bootloader 已解锁；本项目未执行解锁、重锁或清空用户数据 |
| Root 核心 | Magisk 27.0，`27.0:MAGISK:R` |
| 管理器 | Magisk App 30.7，实测保留；不代表任意跨版本组合兼容 |
| Root 验证 | `su -c id` 返回 UID 0；正常重启后再次通过 |
| USB | 停用厂商 USB 选择服务后，重启可自动恢复 MTP + ADB |
| 来电自启 | Autoboot v2 已写入 boot，正常启动 / Root 通过；关机插电效果尚未实测 |
| 完成日期 | 2026-10-23 |

## 阅读顺序

1. [完整 Root 流程](docs/ROOT_PROCESS.md)：固件来源、匹配验证、boot 修补、刷写与 Root 验证。
2. [工具和上游来源](docs/TOOLS.md)：必需工具与仅用于排查的工具。
3. [问题与失败尝试](docs/TROUBLESHOOTING.md)：灰屏、临时启动无效、Recovery panic、授权拒绝等。
4. [USB 默认只充电修复](docs/USB.md)：原因、已验证命令和回退。
5. [来电自启模块](docs/AUTOBOOT.md)：修改范围、安装问题与未完成测试。
6. [分区备份和恢复原则](docs/BACKUP_RESTORE.md)：保留本机固件、NV、启动链与 GPT。
7. [公开的结果与哈希](evidence/verified-results.json)：明确已验证 / 失败 / 推测 / 待测试。

## 仓库脚本

- `scripts/inspect_boot.py`：离线检查 Android legacy boot 头、镜像 ID、gzip、CPIO 和 Magisk 配置；不连接手机，不修改镜像。
- `scripts/rebuild_recovery.py`：用本机 `recovery-from-boot.p` 和 boot 重建 Recovery，要求给出已核实的手机 Recovery ID；不刷写。
- `scripts/prepare_magisk27.py`：从指定 SHA256 的官方 v27 APK 提取本次用到的 ARM64 文件，不执行二进制。
- `scripts/patch_boot27.sh`：在手机临时工作目录生成本案例的 boot 候选镜像；不会刷写任何分区。

脚本为本次操作整理后的版本。离线检查、Recovery 重建和 APK 提取已在留存样本上验证；修补包装脚本仅做语法和参数保护检查，未重新在手机执行或刷写。不要把文档发布后的脚本整理等同于重新跑过完整 Root。

## 最关键的经验

- Magisk 管理器能打开，不等于核心已安装；以 UID 0 和重启后的结果为准。
- 本机灰屏可以是 Fastboot，必须结合 USB 接口和命令确认。
- `fastboot boot` 返回 OKAY，不等于目标镜像真的运行。
- 本案例原 boot 没有 ramdisk，最终仍从普通 boot 成功 Root；两次 Recovery 路线均失败。
- 已验证的 Root 仅需要写 boot；Recovery 最终恢复原厂，没有刷整包或格式化 userdata。
- 系统包写着 PBBM00，手机是 PBBT00。**只验证了选定 boot / 重建 Recovery 的适配证据，不代表整包可刷。**

新增文档与脚本使用 [MIT License](LICENSE)；第三方软件、官方固件及其权利归各自作者 / 厂商，本仓库仅链接来源，不重新分发。
