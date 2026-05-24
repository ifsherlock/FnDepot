# Docker Copilot for fnOS

Docker Copilot 是一个面向 Docker 容器运维的 Web 管理工具。本目录用于为 FnDepot 提供该应用的元数据、图标和自动生成的 FPK 安装包。

## 目录内容

- `ICON.PNG`：FnDepot 应用图标
- `Preview/`：预览图目录
- `README.md`：应用说明
- `fpk-dockercopilot_x86.fpk`：x86 架构安装包（由 workflow 生成）
- `fpk-dockercopilot_arm.fpk`：arm 架构安装包（由 workflow 生成）
- `fpk-dockercopilot.fpk`：兼容文件名，默认复制 x86 版本
- `SHA256SUMS.txt`：安装包校验文件

## 构建来源

FPK 源模板来自 `build-src/fpk-dockercopilot/`，其核心基底是当前可用的 CGI 版 Docker Copilot 打包目录：

- CGI 入口代理
- `cmd/main` 生命周期控制脚本
- `install_callback` / `upgrade_callback` 中的 CGI 清洗与权限修复
- Web 内部打开所需的 `app/ui/config`

## 上游二进制来源

工作流会从以下上游仓库 Release 自动拉取二进制：

- 仓库：`https://github.com/ifsherlock/dockerCopilot`
- 资产：
  - `dockerCopilot-amd64.tar.gz`
  - `dockerCopilot-arm64.tar.gz`

## 发布方式

触发 `.github/workflows/build-dockercopilot.yml` 后，工作流会：

1. 下载上游 Release 二进制
2. 更新打包模板 `manifest`
3. 分别构建 x86 / arm 两个 FPK
4. 更新本目录内的 `.fpk` 与 `SHA256SUMS.txt`
5. 自动提交回仓库
