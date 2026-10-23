# USB 默认只充电：已验证的可逆处理

现场 USB 调试一直开启，但每次重启 / 重插都要手动选择文件传输才出现 ADB。不是“USB 调试开关又关闭”。

分析实际 `OppoUsbSelection.apk` 的配套 OAT/VDEX，看到 `UsbService.c(Context)` 在连接时调用 `d(Context)`，后者将 `Settings.System` 中的 `usb_remeber_selection` 重设为 0；充电功能使用 MIDI。它覆盖了先前设置的 AOSP 屏幕解锁默认功能。

先尝试 `svc usb setScreenUnlockedFunctions mtp` 不足以解决；单独停用组件也被系统拒绝。最终以下组合成功：

```powershell
adb shell pm disable-user --user 0 com.coloros.usbselection
adb shell svc usb setScreenUnlockedFunctions mtp
adb shell svc usb setFunctions mtp
```

不需要 Root。停用的是厂商 USB 选择包装应用，Android USB 框架继续工作；`ro.adb.secure=1` 保留，电脑仍需正常 ADB 授权。

重启后不手动选择文件传输，约 24.7 秒自动出现 ADB，`sys.boot_completed=1`，`sys.usb.state=mtp,adb`；后续 Root 重启验证也保持。

恢复厂商 USB 选择应用：

```powershell
adb shell pm enable --user 0 com.coloros.usbselection
```

这恢复包的启用状态；MTP 默认选择是另一个设置，如有需要在手机 USB 页面重新选择自己的模式。

| 本机观测的 USB ID | 实际含义 |
|---|---|
| 22d9:2765 | Android MTP + ADB |
| 22d9:2764 | MTP，无 ADB |
| 22d9:2046 | MIDI，无 ADB |
| 0e8d:201c | Fastboot（灰屏也可出现） |
| 0e8d:20ff | HID；未获得可用 BROM |

这些是这台手机的观测记录，不是所有 OPPO / MTK 设备的通用映射。
