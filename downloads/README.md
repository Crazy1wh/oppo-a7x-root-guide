# 固件下载入口

## GitHub 备用存档

[C.22 固件 Release 下载页](https://github.com/Crazy1wh/oppo-a7x-root-guide/releases/tag/firmware-c22-1220)。下载下面三个分卷，缺一不可：

| 文件 | 大小 | 下载 |
|---|---|---|
| `.ozip.part001` | 1 GiB | [分卷 1](https://github.com/Crazy1wh/oppo-a7x-root-guide/releases/download/firmware-c22-1220/PBBM00_11_OTA_1220_all_cUKUfmx0zcSQ.ozip.part001) |
| `.ozip.part002` | 1 GiB | [分卷 2](https://github.com/Crazy1wh/oppo-a7x-root-guide/releases/download/firmware-c22-1220/PBBM00_11_OTA_1220_all_cUKUfmx0zcSQ.ozip.part002) |
| `.ozip.part003` | 680463810 bytes | [分卷 3](https://github.com/Crazy1wh/oppo-a7x-root-guide/releases/download/firmware-c22-1220/PBBM00_11_OTA_1220_all_cUKUfmx0zcSQ.ozip.part003) |

完整分卷清单、各卷 SHA256 及整体校验值：[firmware-c22.json](firmware-c22.json)。Release 的 Source code ZIP / TAR 仅包含项目文本，不是刷机包。

克隆或下载本项目后，自动下载三个分卷、合并并检查 SHA256：

```powershell
python scripts/firmware_parts.py merge ./parts ./PBBM00_11_OTA_1220_all_cUKUfmx0zcSQ.ozip --download
```

已经下载分卷时去掉 `--download`。磁盘建议至少空余 6 GiB（分卷和合并文件会同时存在）。此脚本不解密、不刷机，不覆盖已有输出文件。

## 原始官方入口

- [官方自动更新 CDN](https://gauss-otacostauto-cn.allawnfs.com/remove-206f1bce6bbe35ec5fae7162ae9a0675/ota/24/12/09/2d6aa9ac-6f5a-454a-a025-2adcc943b7c4.ozip)
- [官方手动更新 CDN 备用域名](https://gauss-otacostmanual-cn.allawnfs.com/remove-206f1bce6bbe35ec5fae7162ae9a0675/ota/24/12/09/2d6aa9ac-6f5a-454a-a025-2adcc943b7c4.ozip)

两个链接属于同一官方 CDN 体系，并非独立永久备份。原链接失效后优先使用上方 GitHub Release；若 Release 也不可用，按完整文件名、OTA 版本与哈希查找并验证其他存档，不能只看“C.22”字样。

| 项目 | 值 |
|---|---|
| OTA 版本 | PBBM00_11.C.22_1220_202411251524 |
| 完整文件名 | PBBM00_11_OTA_1220_all_cUKUfmx0zcSQ.ozip |
| 大小 | 2827947458 bytes（约 2.63 GiB） |
| 官方元数据 MD5 | `467d47e11b96fbea9dc83217439ec109` |
| 本地完整文件 SHA256 | `a29df96c1430590db8655d22f3b82060b59173744b5fd96c5138301ac09ca73c` |

## 为什么不直接提交完整包

[普通 Git 文件限制 100 MiB](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)；[Release 单个附件须小于 2 GiB](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)。本包大于单附件限制，因此存入 Release，分为 1 GiB + 1 GiB + 约 649 MiB，仓库只保留说明、脚本和校验清单。

维护者可对已验证的本地副本运行 `python scripts/firmware_parts.py split ./firmware.ozip ./release-parts`，核对分卷后手动上传到 Release；仓库不配置自动发布工作流。原 CDN 失效后可使用已存档 Release 或现有已验证的本地副本。

包内型号标识 PBBM00 与实测手机 PBBT00 不同。本记录只验证了选定 boot / 重建 Recovery，**不代表整包可直接刷入**。固件不是本项目原创，MIT 许可不覆盖厂商固件。
