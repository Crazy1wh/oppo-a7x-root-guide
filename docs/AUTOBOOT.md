# 可选：Magisk Autoboot v2.0.0

上游：[anasfanani/magisk-autoboot](https://github.com/anasfanani/magisk-autoboot)，[v2.0.0 发布页](https://github.com/anasfanani/magisk-autoboot/releases/tag/v2.0.0)。这是 Root 成功后的附加实验。

## 当前结果

- 模块脚本已写入 boot。
- 正常启动与 UID 0 已验证。
- `/sbin/autoboot.sh` 存在，1042 bytes。
- **关机后插充电器自动开机尚未实测**。截至 2026-10-23 测试被推迟，不能把“脚本在”写成“功能成功”。

## 审查到的改动

它直接修改 boot ramdisk，不只是放一个开机后挂载的普通模块文件：

```text
overlay.d/init.autoboot.rc
overlay.d/sbin/autoboot.sh
```

init 规则覆盖 charger 事件、`ro.bootmode=charger` 和 `sys.boot_from_charger_mode=1`，调用脚本尝试正常重启。与工作中的 Root boot 对比：内核、已有 CPIO 内容 / 模式及 Magisk 配置一致，仅新增以上两项。

脚本阈值是 5%，最多检查 6 次、间隔 10 秒；最后一次即使低于阈值也会继续重启。因此不能将其描述为“一定等到电量超过 5% 才开机”。本次未调整上游阈值。

## 为什么没有仅靠 App 安装完成

用户在 Magisk 模块页安装并重启后，模块列表和 `backup_boot.img` 均存在；其备份与安装前已验证的 32 MiB Root boot 原始备份 SHA256 一致。但 boot 读回仍是旧镜像 ID，且 `/sbin/autoboot.sh` 缺失。

之后在工作副本上用模块自己的修补脚本和现有 v27 magiskboot 生成候选，审查差异后通过 Fastboot 写 boot，正常开机和 Root 通过。确切的 App 写入失败原因未知。

本次候选为完整 32 MiB 分区大小，SHA256 `67f4b836836eba3afd1fcd5147fc21aea482ec8feaa3f6bf0c1a763d8ec73f49`，镜像 ID `818f758876c9c8e5bb9c7df9b7a756011c799d48`。这里只公开哈希，不分发镜像。

## 回退

关闭模块开关不能保证移除已经写进 boot 的规则。上游卸载脚本尝试恢复备份，但这台手机应读回确认结果。可用的明确回退是通过 Fastboot 写回安装模块前已经验证的“仅 Root”boot；不要用其他手机的 boot。

## 后续测试方法

人在现场、可操作手机时：拔数据线 → 正常关机 → 插充电器 → 不按电源键，观察是否进入桌面，记录是否只显示充电图标、重启循环及实际电量。不要在无人可处理的情况下远程关机试验。
