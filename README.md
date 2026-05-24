# FnDepot - Docker Copilot

这是一个面向 fnOS 的第三方应用源仓库骨架，用于为 Docker Copilot 自动生成并发布双架构 FPK 安装包。

## 仓库要求

根据 FnDepot 规范：

- 仓库名必须为 `FnDepot`
- 默认分支必须为 `main`
- 仓库必须为公开仓库
- 应用目录名必须与 `fnpack.json` 中的键完全一致

## 当前应用

- `fpk-dockercopilot`：Docker Copilot

## 目录说明

```text
FnDepot-main/
├─ .github/workflows/build-dockercopilot.yml   # GitHub Actions 自动构建流程
├─ fnpack.json                                 # FnDepot 全局索引
├─ tools/fnpack/                               # 随仓库存放的 fnpack Linux 二进制
├─ build-src/fpk-dockercopilot/                # FPK 打包源模板（基于 dockercopilot_cgi）
└─ fpk-dockercopilot/                          # FnDepot 客户端实际读取的应用目录
```

## 自动构建逻辑

工作流 `build-dockercopilot.yml` 会执行以下步骤：

1. 从上游仓库 `ifsherlock/dockerCopilot` 的 Release 获取版本信息
2. 分别下载：
   - `dockerCopilot-amd64.tar.gz`
   - `dockerCopilot-arm64.tar.gz`
3. 将解包后的 `dockerCopilot` 二进制替换进 `build-src/fpk-dockercopilot/app/bin/dockerCopilot`
4. 按架构更新 `manifest` 中的 `version` 与 `arch`
5. 使用：
   - `tools/fnpack/fnpack-1.2.1-linux-amd64`
   - `tools/fnpack/fnpack-1.2.1-linux-arm64`
   分别构建 FPK
6. 将产物发布到 `fpk-dockercopilot/`：
   - `fpk-dockercopilot_x86.fpk`
   - `fpk-dockercopilot_arm.fpk`
   - `fpk-dockercopilot.fpk`（兼容文件，默认复制 x86 版本）
7. 自动更新 `fnpack.json` 与 `fpk-dockercopilot/SHA256SUMS.txt`
8. 自动提交回仓库 `main` 分支

## 首次使用

1. 将当前目录内容推送到目标仓库 `https://github.com/ifsherlock/FnDepot`
2. 确认仓库默认分支为 `main`
3. 在 GitHub Actions 中手动运行 `Build Docker Copilot FPK`
4. 等待工作流完成并自动提交生成结果
5. 在 fnOS / FnDepot 客户端中添加该仓库地址进行索引

## 可选输入

手动触发工作流时可传入 `release_tag`：

- 留空：自动使用上游 latest release
- 填写例如 `2.1.10`：固定构建指定 release

## 说明

- `build-src/fpk-dockercopilot/` 是打包模板源目录，不是最终给 FnDepot 客户端读取的安装包目录。
- `fpk-dockercopilot/` 目录必须保留 `ICON.PNG`、`README.md`、`Preview/` 等元数据文件。
- 在首次工作流成功前，仓库中不会包含最终的 `.fpk` 安装包文件。
