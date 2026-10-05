# mufeng-parallel-root-cause

支持 Codex 和 Claude Code。安装与更新见 [项目安装文档](https://github.com/ichangyou/mf-ai-skills/blob/main/docs/installation.md)。

## 调用

Codex：

```text
$mufeng-parallel-root-cause [任务或素材]
```

Claude Code：

```text
/mufeng-parallel-root-cause [任务或素材]
```

## 依赖与执行范围

真实日志与可复现实验；并行模式需要宿主提供子代理。

“支持”表示提供两端入口和执行说明；外部服务、账号认证及工具能力需单独配置。实际执行规则见 [SKILL.md](SKILL.md)。

并行证伪式根因调查。用于调查已经卡住的硬 bug：两条以上线索已经追死、故障横跨多层（应用代码 / 配置 / 第三方服务 / 系统 / 本地工具链）、或者症状和最显然的解释相互矛盾。

核心原则不是并行找证据支持猜想，而是并行地**杀死**猜想。每个子代理的任务是证伪自己的假设，活到最后的假设才配谈修复。

```
/mufeng-parallel-root-cause [问题描述]
```

不适用于第一次看这个 bug，或 stack trace 已直接指向某个文件的情况。
