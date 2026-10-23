# 工具与上游来源

| 工具 | 本次用途 | 是否最终 Root 必需 |
|---|---|---|
| [Android Platform Tools](https://developer.android.com/tools/releases/platform-tools) | ADB、Fastboot、属性与 USB 检查、传输、boot 刷写 | 是；使用官方版本，现场精确版本未单独留存 |
| [Magisk v27.0](https://github.com/topjohnwu/Magisk/releases/tag/v27.0) | 核心与 magiskboot / magiskinit / 官方修补脚本 | 是，成功版本 |
| [Magisk v30.7](https://github.com/topjohnwu/Magisk/releases/tag/v30.7) | 现场管理器；Recovery 路线也曾测试该版本 | 管理器保留；v30.7 Recovery 尝试失败 |
| [oppo_ozip_decrypt](https://github.com/bkerler/oppo_ozip_decrypt) / [oppo_decrypt](https://github.com/bkerler/oppo_decrypt) | 检查 OPPO 固件格式和解密 / 提取路径 | 按固件格式选择，不打包本仓库 |
| Python | 镜像解析、BSDIFF40 重建、哈希、二进制差异分析 | 仓库离线脚本用 Python 3.10+ 标准库；现场 Python 3.14 |
| [JADX](https://github.com/skylot/jadx) | 分析 OTA App、USB 选择 App、管理器资源 | 排查用途 |
| 设备内 oatdump | APK 中 dex 不完整时分析实际 OAT / VDEX 代码 | USB 排查用途 |
| [Capstone](https://github.com/capstone-engine/capstone) 5.0.9 | 分析精确版本 LK 命令分派与临时启动路径 | 排查用途 |
| [mtkclient](https://github.com/bkerler/mtkclient) | 尝试识别 MTK USB 接口；未获得可用 BROM 读回 | 不是成功 Root 路线的依赖 |
| UsbDk / USB 枚举工具 | 观察连接、断开、VID/PID 和接口类型 | 排查用途 |
| [ImageFactory](https://github.com/tohateam/ImageFactory) | 最初讨论的候选提取工具 | 未作为本次成功提取 boot 的来源 |
| [Magisk Autoboot](https://github.com/anasfanani/magisk-autoboot) v2.0.0 | 后续加入 charger init 规则 | 可选；实际插电效果未测 |

不要将“曾使用 / 曾研究”理解成“必须全部安装”。最终启动链是官方 v27 工具生成的普通 boot 镜像，经 Fastboot 写入；未通过 mtkclient 解锁或格式化。

## 固定校验值

| 文件 | SHA256 |
|---|---|
| Magisk v27.0 APK | `f511bd33d3242911d05b0939f910a3133ef2ba0e0ff1e098128f9f3cd0c16610` |
| 用户提供的 Autoboot v2 ZIP | `e0a08598fa124423ad99e8bb4b0f6d3f928780127f9650648a81a6b1c11c4a48` |

哈希仅对应现场实际文件。仓库不包含工具二进制、厂商 APK/OAT、完整 bugreport、官方固件或设备分区镜像。下载应从各自上游发布入口进行，并遵守各项目许可。

Magisk 原理参考：[官方安装说明](https://topjohnwu.github.io/Magisk/install.html)、[v27 boot_patch.sh](https://github.com/topjohnwu/Magisk/blob/v27.0/scripts/boot_patch.sh)。本案例对官方通用流程作了设备特定验证，不能用本案例覆盖其他设备的安装要求。
