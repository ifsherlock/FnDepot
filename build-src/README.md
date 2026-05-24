# build-src 说明

本目录存放 GitHub Actions 打包时使用的 FPK 源模板。

## 当前模板

- `fpk-dockercopilot/`

该模板直接基于当前已验证可用的 CGI 打包基底 `dockercopilot_cgi/` 拷贝而来，保留了：

- `manifest`
- `cmd/`
- `config/`
- `wizard/`
- `app/bin/`
- `app/ui/`

## 用途

工作流会在运行时：

1. 复制 `build-src/fpk-dockercopilot/` 到临时工作目录
2. 替换 `app/bin/dockerCopilot` 为上游 Release 对应架构的二进制
3. 更新 `manifest` 的 `version` 和 `arch`
4. 调用 `tools/fnpack/` 中的 Linux 版 fnpack 构建 `.fpk`

## 注意事项

- 不要把最终发布用的 `.fpk` 文件提交到本目录
- 本目录仅用于构建，不是 FnDepot 客户端索引目录
- FnDepot 客户端实际读取的是根目录下的 `fpk-dockercopilot/`
