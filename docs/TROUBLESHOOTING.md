# 遇到的问题、结果与证据边界

| 现象 / 尝试 | 结果 | 处理与结论 |
|---|---|---|
| 下键进入灰屏，电脑反复提示驱动连接 | `0e8d:201c` 可响应 Fastboot | 灰屏不等于关机或 BROM；先查接口和 Fastboot |
| `0e8d:20ff` | HID，未成功完成 BROM 握手 | 未证明能用它读取分区；停止把该 PID 当成可用下载模式 |
| `fastboot fetch` / 分区读取命令 | 本机不支持；曾产生空输出文件 | 空文件不是备份；改走官方固件提取，Root 后原始读回 |
| `recovery-from-boot.p` | BSDIFF40 补丁 | 必须结合对应 boot 重建；不能直接刷入 |
| Magisk App 能打开、出现安装界面 | 核心仍可能未安装 | 用 magisk 版本、su UID 0 与重启保持验证 |
| Magisk 30.7 Recovery 路线 | 直接启动后 kernel_panic，回到普通 Android，无 Root | 回刷匹配的原厂 Recovery；不是最终方案 |
| Magisk 27 Recovery 路线 | 同样 kernel_panic，无 Root | 再次恢复原厂 Recovery，转向普通 boot |
| 修改 Recovery 后进入普通系统再尝试 Recovery | Recovery ID 回到原厂值 | 确认发生恢复；具体执行恢复的进程未直接观测 |
| `fastboot reboot recovery` | 未可靠进入目标 Recovery | 精确版本 LK 暴露 `oem reboot-recovery`；直接 OEM 命令有效，但修补 Recovery 仍 panic |
| `fastboot boot` 返回 OKAY | 正常系统启动但无 Root，也无探针属性 | 不视为镜像实际运行成功；最终持久写 boot 才验证成功 |
| 原 boot ramdisk=0 | 普通 boot 最小 ramdisk 路线成功 | 本机不必坚持 Recovery 路线 |
| 每次重启只充电，ADB 消失 | USB 调试已开启，但厂商服务重设 USB mode | 停用 com.coloros.usbselection 并设置 MTP；重启验证通过 |
| `su` 超时 / 拒绝 | Shell 授权超时后记为拒绝 | 管理器超级用户页打开 Shell 开关；不反复刷 boot |
| App 30.7 提示环境问题 / 核心 27 | `/data/adb/magisk` 为空 | 保留稳定核心，使用 v27 同版资源修复，env_check=0 |
| v27 管理器覆盖安装 | OPPO 提示版本过高或等待确认 | 最终没强行降级；现有管理器可授权 |
| `fastboot oem off-mode-charge 0` | `not support on security` | 读回仍为 1；未配置成功，不能声称已启用插电开机 |
| Autoboot 在管理器显示已安装 | boot 读回仍旧，脚本缺失 | 模块注册不是修改成功；构建审查后通过 Fastboot 写入 boot |
| ADB exec-out 二进制流备份 | 现场输出长度异常，多出字节 | 标记无效；改为手机 dd 到文件、pull、双端 SHA256 |

## 尚未证实的解释

- 临时 `fastboot boot` 失效：精确 LK 反汇编与 MTK 参考代码支持“64 位内核架构状态未按普通存储启动路径初始化”的可能性，但未完成全部因果证明。已确认的只是临时启动没有获得 Root。
- Recovery panic：不能仅凭版本、OPPO Root 检查开关或内核字符串改动断言根因；没有取得匹配该次 panic 的完整致命调用栈。
- Autoboot App 安装未写入 boot：已证实读回未改变，具体写失败原因未知；不能直接断言是写保护。

## KernelSU 为什么没选

本机是 4.4 非 GKI 内核，无法套用面向 GKI 的预编译安装路线。替代方案需要适配该机内核、源码 / 配置 / 驱动和构建验证；这次未找到并验证可直接使用的 PBBT00 内核项目。没有据此断言所有 4.4 都不能 KernelSU。Magisk 普通 boot 已成功，因此没有继续扩大到重编内核。

## 有效验证顺序

USB 接口 → ADB/Fastboot 能否响应 → boot_completed → 核心版本 → su UID 0 → 重启后重复。每一步分别留证据，避免把“传输成功”“App 已安装”“手机进桌面”混同为 Root 成功。
