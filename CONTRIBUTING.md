# 维护与贡献

1. 在 `skills/<name>/` 维护唯一正文，名称使用小写字母、数字和连字符，不复制两套平台内容。
2. `SKILL.md` 必须有合法 YAML `name`、`description`；名称与目录一致。`compatibility` 说明真实执行条件。
3. `README.md` 提供两端调用、依赖、示例与输出说明；执行细节放 `SKILL.md`。
4. 脚本放 `scripts/`，规则放 `references/`，图片与模板放 `assets/`，简单 skill 不创建空目录。
5. 资源从实际加载路径定位，不写作者电脑的绝对路径；外部工具使用明确配置或实际发现的位置。
6. 新增后更新根 README，运行 `python3 scripts/install.py --platform both --scope project` 并提交两端链接。
7. 完成静态校验和相关行为测试，外部依赖未验证时如实记录。

## 检查

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m unittest discover -s skills/mufeng-bilingual-storybook/tests -v
```

Windows 使用 `.venv\Scripts\python.exe`；绘本 PDF 字体测试在 macOS 运行。CI 不调用付费模型、账号或发布接口。

## 元数据与发布物

可选 `agents/openai.yaml` 的 `default_prompt` 必须包含准确的 `$skill-name`；图标路径相对于 skill 目录并存放在 `assets/`。
本仓库校验器按当前通用字段检查，包括 `compatibility`。旧版 skill-creator 的 `quick_validate.py` 可能不接受该字段，不能用它的旧字段列表替代当前平台文档。
生成 `.skill` 包：

```bash
python3 scripts/package.py mufeng-dankoe-writing
```

输出在 `dist/`，不提交生成包。该格式不替代两端目录安装，其他产品是否接受包内字段需按其规则验证。
运行状态、历史和缓存不进入源码；采用的业务图片保存在使用 skill 的目标项目内。
