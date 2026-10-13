---
name: mufeng-blog-writing
description: Chinese technical blog writing for mufeng.blog with Joey's tone, clear problem-solution structure, runnable code examples, and publish-ready SEO metadata. Use when drafting or revising technical posts, tutorials, or troubleshooting articles, especially for iOS (Swift/Objective-C), Java/Spring Boot, Vue.js, or JavaScript/TypeScript.
compatibility: "Codex and Claude Code. Current conversation and any task-specific source materials; subagents are optional unless the workflow requires independent execution."
---

# mufeng-blog-writing

## Overview
Produce mufeng.blog technical articles in Joey's friendly, professional tone. Keep structure clear, include practical code with Chinese comments, and deliver title, summary, and tags ready for publishing. By default, save the generated article as a Markdown file in the current working directory.

## Workflow
1. Define the reader and single reader outcome using `Reader Understanding and First Principles` below. Infer reasonable prerequisites and article type from the request and materials; state the assumption briefly and ask only when missing information materially changes the article.
2. Select the structure and depth for an introduction, tutorial, deep analysis, or troubleshooting article. Use `references/templates.md` as optional scaffolding, not mandatory headings.
3. Draft the content. Follow `references/identity.md`, ensure code is runnable and contextualized, and include best practices and pitfalls where relevant. For a technical-subject article, also satisfy the `Technical Explainer Contract` below while drafting.
4. Add metadata. Provide an optimized title, a 150-200 Chinese character summary, and 4-8 tags using `references/seo-checklist.md`.
5. Append signature footer. Unless the user explicitly asks to skip, add a footer block at the end of the article with timestamp and location only. Do not add any AI-assist, AI-generated, or model-use declaration.
6. Run the comprehension gate below alongside `references/seo-checklist.md`. Check accuracy and readability separately; fix failures before delivery.
7. Save output file. Unless the user explicitly asks not to save, write the final Markdown article to the current working directory as a `.md` file.

## Reader Understanding and First Principles

Apply these seven rules when drafting or revising an article. 用户明确指定的读者、形式与深度优先；“专业、详尽”不能默认解释为面向领域专家或罗列全部细节。

1. **先确定读者和唯一任务。** 写作前用一句话说明本文面向谁、假设他们已经懂什么、读完要能理解或完成哪件事。未指定时，默认面向有一般开发经验、但不了解本文专门领域的读者；AI 工具文章可默认读者会用 AI 编程工具，但不懂相关底层技术。该定位用于写作决策，不必作为制作说明放进正文。
2. **区分介绍、教程与深度分析。** 介绍帮助读者理解用途、工作机制和适用条件；教程围绕一条可运行路径说明前提、操作、结果与常见错误；深度分析展开机制、证据、替代方案和取舍；排错文章围绕症状、原因与修复。选择一个主类型，其他内容只在服务主任务时补充。介绍无需展开完整工程与接口契约；用户要求详尽时应增加解释和分析深度，避免无关扩张。
3. **关键术语首次出现必须解释。** 用“中文含义＋它在当前问题中的作用”解释影响理解的缩写和领域术语，不能只列英文全称。一个解释中避免引入多个未解释的概念；不必要的术语直接换成普通说法。后续保持名称一致，不用文末术语表替代首次解释。
4. **用同一个具体案例贯穿。** 在抽象机制前给出读者能理解的问题、输入与期望结果，再说明每个关键概念在案例中对应什么。选择素材中可核查的案例；没有作者亲历材料时，可使用明确标注的示例或本次实际完成的验证实验，不得写成作者过去的亲身经历。额外案例只有在揭示新机制或边界时才加入。
5. **正文细节设准入条件。** 一个细节应帮助目标读者理解机制、完成操作或做出决策。完整工程、协议字段、统计内部项和罕见故障优先放附录、项目文件或参考链接，除非它们就是本文任务。理解前提、准确类比和必要因果衔接也有价值；删除测试必须问“删掉后，读者是否失去理解下一段所需的前提”。限制在影响判断处说明，集中整理共同边界，避免重复声明。
6. **发布或交付前增加理解门禁。** 按已声明的读者检查：能否用普通话复述“它是什么、为什么需要、怎么开始、结果说明什么、哪些尚未证明”？核查开头是否回答具体问题、概念是否先解释后使用、章节是否沿同一任务推进、代码前后是否说明目的和结果。回答若依赖未解释术语、读者需要来回跳读，或仅能照抄命令，必须修改。该检查是编辑自检；没有真实读者参与时，不得宣称已通过读者测试。
7. **技术文档必须深入分析第一性原理。** 从最基础、可验证的事实与约束出发，回答：核心问题是什么；输入、输出和关键状态是什么；有哪些无法绕过的约束；关键机制如何产生结果、为什么有效；它依赖哪些假设、付出什么代价、在什么条件下失效。用证据串成因果链，并在有助理解时与一种直接或常见替代做法比较。依据官方文档、源码、协议、实验或数学推导，区分事实、推断、教学简化与未知；不臆造闭源内部机制。深度体现在解释“为什么”，不能用字段清单、模块名称或宣传概述充当第一性原理。正文先给直观解释与贯穿案例，再逐层深入；介绍也要回答机制与关键约束，深度分析进一步展开实现、推导或实验，不机械增加固定标题。无法验证的部分明确边界，并分析已知机制。

## Technical Explainer Contract

For an article whose subject is a technical thing (tool, framework, API, protocol, model, library, command, or engineering method), answer the following at the depth appropriate to its reader and article type. This is a coverage requirement, not a section template: merge overlapping items instead of restating the same fact. Lead each section with its useful answer, including concrete context when the answer would otherwise require unexplained concepts.

1. 技术点是什么 — the exact definition and boundary, including what it is not.
2. 存在的意义 — what people did before it existed and what that cost them.
3. 有什么作用 — verifiable outcomes: 能做什么 / 省掉哪一步 / 换来什么结果.
4. 第一性原理 — apply rule 7 above: derive why the mechanism works from verifiable facts, constraints and assumptions, with evidence and failure boundaries.
5. 怎么使用 — tutorials provide a minimal runnable path with prerequisites, expected output, verification and common errors; introductions explain the smallest starting action and link advanced setup instead of reproducing a full implementation.
6. 给出实战案例 — one evidence-backed case with context, observable results and a decision; distinguish author experience, attributed external cases and current verification experiments.
7. 痛点与解决方法 — paired in the same section, plus what the fix does not solve.
8. 不要有废话 — delete paragraphs that add no information, judgment, step or necessary understanding prerequisite; retain useful concept explanations and causal connections. No generic `随着 XX 的发展` openers, empty transitions, verbatim restated conclusions, or unearned adjectives.

Check each claim against source material or an actual experiment. Do not invent personal experience, sources, or results. Remove filler and repeated conclusions before saving.

## Output Format
- Return Markdown only.
- Start with a YAML frontmatter block containing `title`, `author: changyou`, and `date: YYYY-MM-DD` (today's date).
- Then `# 标题` heading.
- Include `摘要` and `标签` blocks before the正文 if they are not provided.
- Use fenced code blocks with language tags.
- Append a default footer block at the end of the article (unless user says not to):
  - Line 1: `YYYY.MM.DD HH:mm`
  - Line 2: `沪 · 赵巷` (or user-provided location)
  - Do not add `📌 声明：本文由 AI 辅助完成` or any equivalent AI-assist disclosure.
- Default file output behavior:
  - Save a Markdown file to the current working directory.
  - If no filename is specified by the user, use the article title as filename and append `.md`.
  - If the target filename already exists, append a suffix like `-v2`, `-v3` to avoid overwriting unless the user explicitly requests overwrite.

## References
- `references/identity.md`: Blog identity, tone, and language rules.
- `references/templates.md`: Article and tutorial templates plus reusable snippets.
- `references/code-standards.md`: Code example conventions and language samples.
- `references/stack-guidelines.md`: Stack-specific emphasis and pitfalls.
- `references/seo-checklist.md`: SEO guidance and publish checklist.
