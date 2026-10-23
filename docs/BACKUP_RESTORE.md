# 分区备份与恢复原则

本案例 Root 后完成 46 个镜像 / 原始区域备份，6300860416 bytes（约 5.87 GiB），逐项检查大小与设备临时文件 / 电脑 SHA256。GPT 主头与条目、备份头 CRC 通过。镜像和完整私有清单均未上传。

| 优先级 | 本机分区 | 目的 |
|---|---|---|
| 最高 | boot、recovery、odmdtbo | 启动、Root / 模块回退、恢复环境 |
| 最高 | nvram、nvdata、nvcfg、persist、protect1/2、proinfo、oppo_custom | 本机 NV、校准、设备 / 厂商信息；具体字段依厂商实现 |
| 高 | preloader_a/b、lk/lk2、tee1/2、gz1/2、seccfg | 启动链、安全配置与可信环境 |
| 高 | system、vendor、odm、md1img | 当前可用的本机系统与基带版本 |
| 补充 | boot_para、para、metadata、sec1、frp、otp、reserve*、协处理器固件 | 保留其余小分区 / 厂商状态 |
| 补充 | eMMC 首尾 1 MiB | 保存 GPT 所在原始区域，供解析参考 |

本机 preloader_a/b 分别映射 `/dev/block/mmcblk0boot0` 和 `mmcblk0boot1`。名称中的 a/b 不代表 Android 系统为 A/B 布局。各设备映射应自己读取，禁止套用别人的 p 编号。

## 正确的读取方式

先确认 `su -c id`，枚举实际 by-name 映射和分区大小，检查手机临时空间与电脑剩余容量。对每个选定分区：

1. Root 下 `dd if=<已核实的块设备> of=<独立临时普通文件>`；绝不把块设备放在 `of=`。
2. 记录临时文件大小与 SHA256。
3. 将临时文件权限调整为可由 shell 拉取，`adb pull` 到电脑。
4. 核对电脑端大小 / SHA256，与手机临时文件一致后删除临时文件。
5. 保存分区名、真实路径、大小、哈希、采集时间与在线快照标记。

本次 exec-out 二进制流输出发生长度异常，因此不采用“重定向到 img 就当作备份”。也不要在公开 Issue 上传 NV / OTP / 设备信息镜像、完整 bugreport 或未脱敏 ADB 输出。

## 限制

开机状态下依次读取不是同一时刻的离线一致性快照。nvdata / nvcfg / persist 等可写文件系统可能同时变化；哈希一致仅证明传输完整，不证明可恢复性。此次没有为测试而刷回所有分区。

未包含 userdata（约 110 GiB）、cache、expdb、flashinfo、RPMB。照片、应用和登录数据另行备份；metadata 单独保存不能保证解密 / 恢复 userdata。

## 遇到无法开机

若问题发生于 boot / 模块修改之后且 Fastboot 可用，优先恢复同机同版本已验证的 boot：

```powershell
fastboot devices
fastboot getvar unlocked
fastboot flash boot ./your-verified-rollback-boot.img
# 确认 Writing OKAY 后再重启。
fastboot reboot
```

本案例分别保留原厂 boot、仅 Root 的已验证 boot、带 Autoboot 的当前 boot 和原厂 Recovery。恢复时根据故障选择，不要把所有分区一次刷回。

preloader、lk、seccfg 和 GPT 仅在确认损坏与救援通道后处理；首尾 1 MiB 原始文件不是可直接 `fastboot flash` 的标准分区镜像。即使保存了镜像，严重损坏后仍可能没有可用 / 获准的写入通道。本次没有验证 BROM 救砖。

将完整私有备份至少另存到独立硬盘。本机 NV / 设备信息只用于本机恢复。
