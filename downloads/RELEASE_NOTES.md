OPPO A7x C.22 原始官方 OZIP 固件存档，未修改内容。大文件拆为三个二进制分卷，必须全部下载并合并，不能分别解压或刷入。

- 文件：`PBBM00_11_OTA_1220_all_cUKUfmx0zcSQ.ozip`
- 大小：2827947458 bytes
- MD5：`467d47e11b96fbea9dc83217439ec109`
- SHA256：`a29df96c1430590db8655d22f3b82060b59173744b5fd96c5138301ac09ca73c`
- 下载仓库中的 `scripts/firmware_parts.py` 与 `downloads/firmware-c22.json`，运行：

```sh
python scripts/firmware_parts.py merge ./parts ./PBBM00_11_OTA_1220_all_cUKUfmx0zcSQ.ozip --download
```

也可手动下载三个 `.part001` / `.part002` / `.part003` 到 parts 目录后去掉 `--download`，脚本会先检查每卷，再检查合并结果 SHA256。

详情与官方备用链接见 [下载入口](https://github.com/Crazy1wh/oppo-a7x-root-guide/blob/main/downloads/README.md)。GitHub 自动附带的 Source code ZIP / TAR 是项目源代码，不是固件。

包内型号标识为 PBBM00，实测手机为 PBBT00。本案例只验证了选定 boot 和重建 Recovery 的适配，不代表整包可直接刷入 PBBT00。固件权利归 OPPO 等原权利人，项目 MIT 许可不覆盖它。
