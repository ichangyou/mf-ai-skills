---
name: mufeng-parallel-root-cause
description: Use when a bug investigation has stalled — two or more leads already
  died, the failure spans multiple layers (app code / config / third-party service /
  OS / local toolchain), or symptoms contradict the obvious explanation. Triggers:
  硬 bug、根因不明、调查卡住、死路、又是环境问题？、proxy/SDK/上游 分不清。
  Not for first-look debugging or bugs with a clear stack trace.
---

# 并行证伪式根因调查

## 核心原则
不是并行地找证据支持某个猜想，而是并行地**杀死**猜想。
每个子代理的任务是证伪自己的假设；活到最后的假设才配谈修复。

## 何时不用
- 第一次看这个 bug（先按 CLAUDE.md 调试规则线性复现）
- stack trace 直接指向一个文件
- 只是想确认一个已有的强假设（一条 curl 就够）

## 流程
1. **固定原始现象**：完整报错/日志/截图，不要总结。复现路径写成一条可重跑的命令。
2. **写 4-5 个互斥假设**，必须覆盖五层：
   应用代码 / 配置与环境变量 / 第三方服务或 SDK / 操作系统与平台行为 / 本地工具链。
   每个假设附一条**证伪标准**：「如果 X 实验出现 Y 结果，此假设死亡」。
3. **同一消息块扇出子代理**，一个假设一个 agent。每个 prompt 必须包含：
   - 假设原文 + 证伪标准
   - 指定实验手段（curl -v / log stream / 最小复现 / 受控 A/B）
   - 只读约束：不许改代码、配置、环境
   - 汇报格式：结论（存活/死亡）、跑过的确切命令、原始输出（不是总结）
   - 明令禁止提出修复方案
4. **主线程只依据证据裁决**。逐条宣布：哪些假设被什么证据判死（引用命令+输出），
   哪个存活。证据不足以裁决时补实验，不靠推理补位。
5. 裁决后才提**最小修复 + 一个回归测试**，修完按同一复现路径给前后对照。

## 常见错误
| 错误 | 后果 |
|------|------|
| 假设不互斥（两个都是"代码有 bug"的变体） | 漏掉真实层（如上游服务挂了） |
| 子代理去"验证"而不是"证伪" | 确认偏误，每个假设都"找到了支持证据" |
| 子代理顺手改了配置来测试 | 污染现场，后续实验全部作废 |
| 汇报"我认为是 X" 而没有命令+输出 | 观点不是证据，裁决失去依据 |
