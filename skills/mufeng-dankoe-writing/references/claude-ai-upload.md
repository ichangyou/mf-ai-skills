# 可选的 .skill 打包

Codex 和 Claude Code 使用目录安装，不需要上传压缩包。安装方式见本 skill 的 README。

需要给接受 `.skill` 文件的其他产品提供源码包时，在仓库根目录运行：

```bash
python3 scripts/package.py mufeng-dankoe-writing
```

文件生成在 `dist/mufeng-dankoe-writing.skill`。内容来自当前 `skills/mufeng-dankoe-writing/`，不再维护旧的手工包。
修改源码后重新执行命令，再按目标产品当前支持的方式上传；包的生成不代表目标产品已验证支持。
