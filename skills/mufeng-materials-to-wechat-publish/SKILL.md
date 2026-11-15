---
name: mufeng-materials-to-wechat-publish
description: Use when source materials in a directory, such as notes, drafts, transcripts, screenshots, outlines, or code snippets, need to be turned into a professional evidence-rich WeChat Official Account article with mufeng-blog-writing, current WeChat search-intent research, natural keyword mapping, SEO/GEO-friendly Markdown metadata, content-quality gates, real screenshots when available, generated PNG cover and inline illustrations, GitHub-hosted raw image URLs, and WeChat publishing. Do not use for an already-finished article that only needs publishing; use mufeng-wechat-publish-full for that.
compatibility: "Codex and Claude Code. Web search, mufeng-blog-writing, an image tool, gh authentication and a configured WeChat publisher."
---

# Mufeng Materials To WeChat Publish

## Resource Paths

Set the shell variable `SKILL_DIR` to the directory containing the **loaded** `SKILL.md` before running the commands below. Resolve supporting paths from that directory, not the working directory or a fixed user/platform installation path. `$SKILL_DIR` is a shell variable you set, not a host-provided macro.


## Platform Dependencies

Read [references/platforms.md](references/platforms.md) before generating images or publishing. Set `MUFENG_WECHAT_SCRIPT` to the actual `wechat-api.ts` path from an installed `baoyu-post-to-wechat` skill, or use a documented publisher already configured in the host. The variable does not install the publisher. If the dependency or credentials are missing, finish the local article and report that publishing was not executed.

## Core Rules

- Use this skill for the materials-to-article workflow. If the user already has a finished Markdown article and only needs image upload, formatting, API publishing, or publish recovery, use `mufeng-wechat-publish-full` instead.
- Start from the materials in the requested directory, not from a blank topic. Generate the article first with the `mufeng-blog-writing` skill's article-writing conventions, with this skill's frontmatter requirements taking precedence.
- Apply all seven rules in `mufeng-blog-writing/SKILL.md`, section `Reader Understanding and First Principles`: define reader and outcome, select article type, explain terminology, use a continuous case, admit only relevant body details, pass the comprehension gate, and analyze technical first principles in depth. These rules govern content depth and readability throughout this workflow.
- Apply `mufeng-blog-writing/SKILL.md`, section `Article Length and Code Budget`: normally 1000–3000 字 and never over 4000 字; default to no code and retain only indispensable snippets. Technical depth and first-principles analysis must fit within this budget. Use its visible-character counting method for the final rendered article.
- Every generated Markdown article must include SEO/GEO-friendly YAML frontmatter with `title`, `slug`, `author`, `date`, `category`, `summary`, `tags`, and later `coverImage`.
- Keep `summary` and `tags` only in YAML frontmatter. Do not add visible `摘要` headings/blocks or `标签` lines/blocks to the article body. This rule overrides `mufeng-blog-writing`'s default visible `摘要` and `标签` blocks.
- Research current WeChat search intent before drafting. Choose one primary query and 3-6 supporting terms from verifiable current evidence; if live WeChat search evidence is unavailable, label the proxy source and uncertainty instead of inventing demand.
- Map keywords naturally into the title, opening, useful H2 headings, summary, and relevant body sections. Treat YAML `tags` as internal metadata, not as a WeChat ranking signal or a substitute for body relevance.
- Use the uploaded cover in both places: as `coverImage`/`--cover` publishing metadata and as the first rendered element of the WeChat article body. Put its Markdown image immediately after the H1 so the renderer can strip the H1 while leaving the cover first; place no text, visible metadata, caption, or divider before it.
- For articles whose subject is a technical thing, satisfy the `Technical Explainer Contract` and the `No-Filler Rules` before running the quality gates. The contract is a coverage requirement, not a section template.
- Every generated or substantially revised article must pass the evidence and authenticity gate: real screenshots when available, an evidence-backed case with clear attribution, at least one failure/lesson/limitation, and 2-3 authoritative sources. Use first-person experience only when supported by the author's actual experience.
- Before publishing, pass the originality, account-fit, title-integrity, and low-quality-content gates. Revise failures; stop before publishing when a material failure cannot be fixed from available evidence.
- Every generated Markdown article must be Emoji-free. Do not add any AI-assist, AI-generated, or model-use declaration to the article body or footer.
- Default cover generation to Codex built-in ImageGen (`image_gen`) and proceed directly without asking for provider confirmation. This is the user's standing preference for this workflow: do not follow a legacy DashScope / Pollinations / Gemini fallback chain for covers, and do not ask the user to approve switching from that chain to built-in ImageGen. Only use a different cover provider when the user explicitly requests it in the current task. If built-in ImageGen is unavailable or fails, report the failure; do not silently switch to another provider or CLI/API path. Immediately copy adopted images into the project and verify them before continuing. For host-specific availability, read `references/platforms.md`; platform guidance does not authorize silently substituting another provider.
- Do not use generated images as replacements for real screenshots. Real screenshots are evidence assets; never fabricate Codex, Claude, revenue, analytics, or project UI screenshots.
- For technical articles, use the Technical Visual Profile below to choose a recognizable subject before choosing a visual style. Engineering graphics are an option, not a mandatory cover style. Exclude unrelated decorative people, plants and paper texture. Do not default to neon gradients, glowing networks, floating interfaces, glossy 3D objects, robots, brains, circuit heads, or other recognizable generative-AI clichés.
- Save generated images as PNG. If a generated asset is not PNG, convert it to PNG before upload.
- Keep generated images free of readable UI text, Chinese text, labels, captions, watermarks, and signatures unless the user explicitly requests text in the image. Put titles/captions in Markdown instead.
- Do not add a `真实开发过程` section or any equivalent meta-production section about how materials, logs, commands, research, or screenshots were assembled into the article. Keep reader-relevant evidence inside the topical sections and keep workflow notes in the completion report.
- Upload the cover and all inline visual assets to GitHub image hosting, then insert `https://raw.githubusercontent.com/...` URLs into the Markdown article.
- Publish from the final Markdown file. Do not pre-convert Markdown to HTML before calling the WeChat publishing script.

## Execution Contract

Inputs:
- A source-material directory, or the current working directory if no directory is given.
- Source files may include Markdown, text notes, transcripts, outlines, screenshots/OCR notes, code snippets, and drafts.
- Optional user constraints such as target angle, title preference, image count, output filename, or whether to stop before publishing.

Outputs:
- A publish-ready Markdown article saved in the source directory, usually as `<article-slug>.md`.
- SEO/GEO-friendly frontmatter with `title`, `slug`, `author`, `date`, `category`, `summary`, `tags`, and uploaded `coverImage`.
- A documented WeChat search brief with the primary intent, primary query, 3-6 supporting terms, evidence source, and research date.
- A body that starts with the uploaded cover image after the Markdown H1 and contains no visible summary or tag metadata blocks.
- Article body with evidence-backed content: real screenshots when available, a clearly attributed case, failure/lesson/limitation, and authoritative sources.
- Local PNG images under `imgs/<article-slug>/`.
- Uploaded raw GitHub image URLs under `https://raw.githubusercontent.com/mf-blog/blogPictures/main/images/<article-slug>/...`.
- A final WeChat draft or publish result when publishing is not explicitly skipped.

Non-goals:
- Do not rewrite a finished article from scratch unless the user asks for a rewrite.
- Do not use generated images as generic decoration; each inline image should explain or reinforce nearby content.
- Do not publish before the article has metadata, image URLs, and the required ending hook.
- Do not invent personal experience, screenshots, income numbers, project results, or source citations. If evidence is unavailable, record the gap in the completion report and omit the unsupported element or use a clearly labeled non-evidence illustration.

## Markdown Emoji Rules

- The final generated `.md` article must contain no Emoji symbols anywhere.
- This ban applies to YAML frontmatter, title, H1/H2/H3 headings, summary, tags, body paragraphs, lists, blockquotes, code comments, image alt text, captions, `参考资料`, the engagement hook, footer, and any copied source-material excerpts.
- Do not add `📌 声明：本文由 AI 辅助完成` or any equivalent disclosure about AI assistance, AI generation, model use, or automated writing.
- If source materials or an existing draft contain Emoji, remove or rewrite them during article generation. Do not preserve Emoji in quotes or examples unless the user explicitly overrides this rule.
- If the `mufeng-blog-writing` footer rule is used, keep only the timestamp and location. Omit all AI-assist declarations.
- Before publishing, scan the final Markdown for Emoji and AI-assist declarations. Remove every match and re-check.

## Shared Visual Direction and Layout

Before planning images or formatting the article, read [沐风统一视觉规范](../mufeng-blog-writing/references/visual-style.md). It is the shared visual reference for this workflow and `mufeng-wechat-publish-full`.

Apply its composition rules, prompt records, layout defaults and thumbnail/mobile checks. For technical articles, the Technical Visual Profile below overrides its modern humanistic, paper-textured and hand-rendered visual defaults; non-technical articles retain the shared topic variants. Use a complete text-free cover by default; a separately typeset title is optional. Keep exact diagrams deterministic and evidence screenshots authentic. Preserve explicit user choices and record unsupported layout differences rather than editing the publisher or changing the publication path.

## Technical Visual Profile — 主题识别优先

### 适用范围与偏好依据

技术工具、AI 编程、API、框架、协议、架构与工程方法文章使用本节选择图片任务与主体，不固定为同一种画法。封面先建立主题印象，正文图再解释机制；不默认沿用“人物＋植物＋纸卡片＋纸纹”的装饰组合，也不默认退化成白底抽象线段。当前任务有明确风格要求时以该要求为准。规则调整尚未经过新一轮样图验证，不宣称用户已验收视觉效果。

参考宝玉规则中的可用部分，而非整体套用其生图工作流：

- `baoyu-cover-image/references/types.md`：`conceptual` 是可选类型；先判断主体能否让读者识别主题，再选择表现方式。
- `baoyu-cover-image/references/palettes/cool.md` 与 `mono.md`：浅底、深色线条和单一强调色是可选色板，不要求所有技术封面同色同形。
- `baoyu-article-illustrator/references/styles/blueprint.md`：工程图需要时采用网格对齐、统一线宽、几何精度和有意义的连接；不将其强制用于封面。
- `baoyu-article-illustrator/references/styles/editorial.md`：采用清楚的信息层级与因果叙事，不照搬多区块信息图或装饰图标。
- 不直接套用 `flat-vector` 的 toy-model、可爱圆角和装饰元素；不默认使用 `warm`、`watercolor`、`sketch-notes`、`hand-drawn` 或 `screen-print`。

参考文件位于宝玉插件的对应 skill `references/` 下；路径变化时按文件名定位。只借鉴视觉维度，不因此导入额外确认、提供方回退或批量生图要求。封面仍默认内置 ImageGen 直接生成。

### 封面：先选可识别的主题主体

- 先写出“读者不看标题和提示词，能从画面认出什么主题”，选择与材料直接相关的主体，再确定画法、色板和辅助关系。例如 PDF 阅读主题可选择具有页面与扫描内容特征的文档主体，配合检查局部的视觉关系；不伪造产品界面或实际分析结果。
- `conceptual × blueprint-inspired precision × cool/mono × text-none × subtle` 仅为可选工程方向，不是默认组合。可按主题采用有明确物象的编辑插画、剖面或局部放大等形式；不为改变风格添加无关装饰。
- 选择工程方向时，可用白或极浅灰背景、深灰蓝主体和工程蓝强调；需要品牌延续时可用青绿。其他方向仍使用克制的 2–4 色和清楚的明暗层级，正文排版颜色无需随封面改变。
- 工程图保持边缘清楚、线宽一致，不添加假尺寸线、假刻度、伪数据或伪代码。不要把“无纹理、少颜色”理解成“只能画几根线”。
- 不默认用无标签的时序图、寿命图、坐标线或节点关系图作封面。如果删掉标签就无法理解其含义，应改作带准确标签的确定性正文图，封面另选可识别主体。不能所有主题都画文件卡片或节点网络。
- 封面为概念隐喻，不作为精确架构证据。只有核实的依赖、顺序和方向才可用箭头表达；无依据时仅表达分组或关联。不能让画面暗示已实现自动调度、性能提升或收入增长。
- 无文字封面本身构图完整，不预留半张标题空白。默认 2.35:1，主体应充分占据横幅的有效画面，中心方形优先保留识别主题必需的部分，不要求所有辅助关系都塞入方形。裁切冲突时重新构图或按实际渠道需要另做方形版本；禁止通过整体缩小主体解决裁切。320px 缩略下仍应认出主体与主题线索。
- 技术封面默认不画人物、手、面孔、植物、树叶、盆栽、书桌、咖啡、书本、文具、纸张折角、手绘涂鸦、复古纸纹、颗粒版画、水彩或生活方式场景。文章确实讨论其中对象时才可采用，且须记录它的解释用途。
- 不生成 Logo、产品界面、终端截图或代码截图；不添加无意义的图标散布、装饰连接线、发光边缘或立体塑料材质。

### 正文：按解释任务选图，不把封面风格机械复制

| 段落需要解释什么 | 图的类型 | 制作与核查 |
| --- | --- | --- |
| 真实界面、执行结果或错误 | 证据截图 | 原始截图，必要裁切与脱敏，保留来源 |
| 步骤与分支 | flowchart | 确定性绘图，顺序和条件有依据 |
| 组件与依赖 | framework / architecture | 确定性绘图，区分真实连接与教学简化 |
| 两种方案的取舍 | comparison | 同一维度并排比较，不伪造数值 |
| 请求与响应的先后 | sequence | 确定性时序图，不把未知调用画成事实 |
| 单个难以直接展示的概念 | conceptual | 内置 ImageGen，无字，仅表达一个关系 |

精确标签、箭头、状态、数字和代码用确定性图或真实截图，导出 PNG。允许确定性图上的准确文字；“生成图无字”限制针对模型生图，不得为了无字删除理解机制所必需的标签。真实截图无需强行改成蓝灰色。

### 提示词必须包含的约束

每张图仍先保存完整提示词。记录用途、可识别主体、图类型、核心关系、事实依据、构图与裁切、色板、参考和禁用项。先明确要画什么，再写必要约束，不用长串禁用项代替主体设计。只有实际选择工程方向时才加入 blueprint、uniform strokes 等画法词，不机械套用；不默认带回旧的人物植物和纸纹装饰组合。

可用模板（将方括号替换为具体内容，不能原样提交）：

> Text-free editorial cover about [specific topic]. Make [recognizable topic-specific subject and its distinguishing features] the dominant subject, with [one meaningful supporting relationship]. Use [style chosen for this subject] and [restrained palette]. Compose a complete balanced 2.35:1 image with a substantial subject and purposeful negative space, readable at 320px. Keep the essential subject recognizable in a central square crop; recompose rather than shrinking the entire subject to fit every element inside that crop. No labels, watermark, fabricated UI, code, logos, measurements or unrelated decoration. Do not substitute an unlabeled chart or generic node network for the subject.

### 验收门禁

- 隐去标题、图注和提示词，只看实际封面：能否认出与文章相关的主体或使用场景，而不只是“科技感”或几根线？无法识别则拒用并重选主体。此项是编辑自检，不冒充真实读者测试。
- 逐项看实际图：是否出现无关人物植物、生活方式道具、装饰纸纹或通用抽象图标？有则拒用并针对偏离项改提示词重生成，不能仅因颜色符合就采用。
- 把图与邻近段落对照：能否说出它解释的技术关系？若只剩“科技感”或“好看”，重新选图或省略正文图。
- 查看横幅、320px 缩略和中心方形裁切：主题主体可识别，横幅没有因裁切兼容而缩成小图标。方形缺失识别所必需的部分时重新构图或另做版本，不能只验收线条完整。
- 核实线条没有伪造关系，且没有幻觉标签、伪数据或伪 UI。封面概念图不冒充精确机制图。
- 在交付记录中写明实际采用的维度、偏离项、重生成原因及未完成的视觉检查。规则检查不等于用户审美验收。

## Technical Explainer Contract

Apply this contract when the article's subject is a technical thing: a tool, framework, API, protocol, model, library, command, or engineering method. Skip it for 成长, 读书笔记, and 投资 articles, and record the skip in the completion report.

This is a coverage requirement, not a section template. Answer each item at the depth appropriate to the reader and primary article type defined by `mufeng-blog-writing`. Do not create eight mechanical headings to satisfy it, and never add an empty heading to pass the check. Introductions may explain the starting action and link advanced commands; tutorials require a runnable path; deep analyses expand causal mechanisms and evidence. All technical documents require the first-principles analysis below.

1. **技术点是什么** — Name the exact thing and its boundary in one or two sentences before any elaboration. State what it is not whenever readers confuse it with a neighboring concept, for example MCP 与普通插件 or Agent 与 Workflow.
2. **存在的意义** — The condition that made it necessary: what people did before it existed and what that cost them. Ground this in a real constraint; `随着 AI 的发展` and similar scene-setting does not count as an answer.
3. **有什么作用** — The concrete capability, stated as outcomes a reader can verify: 能做什么, 省掉哪一步, 换来什么结果. When this would repeat 存在的意义, merge the two. Never state the same fact twice under two headings.
4. **第一性原理** — Apply rule 7 in `mufeng-blog-writing`: derive how and why the mechanism produces its outcome from verifiable facts, inputs/outputs, constraints and assumptions; explain tradeoffs and failure conditions. Support the causal chain with documentation, source, spec, experiment or mathematical reasoning. A field inventory or module list is not this analysis. Give an intuitive explanation and the concrete case before deeper implementation detail. When internals cannot be verified, analyze the known mechanism and state the unknown boundary rather than inventing it.
5. **怎么使用** — For tutorials, give a minimal runnable path: prerequisites, the smallest working command or code, expected output, verification and the one or two common errors. For introductions, give the smallest starting action and link detailed setup; keep full projects and rare errors out of the body unless needed for the reader's task.
6. **给出实战案例** — At least one evidence-backed case: context, observable result and the decision or conclusion it supports. Distinguish the author's actual work, an attributed external case and an experiment completed during this task. This satisfies the case requirement in `Article Evidence and Authenticity Rules`; never turn an execution-stage experiment into an invented author memory.
7. **痛点与解决方法** — State the reader's concrete pain in their own words, then the specific fix, then what the fix does not solve. Pair every 痛点 with a 解决方法 in the same section; an unpaired complaint is filler. The unsolved part also satisfies the failure/limitation requirement.
8. **顺序与答案前置** — Let one concrete reader problem connect the sections. Introduce the case before abstractions that depend on it; explain concepts before using them in commands or analysis. Lead with the useful answer, including necessary concrete context, and develop mechanism, action and boundaries at the chosen depth. Do not force an abstract conclusion into the first sentence when it relies on unexplained terms.

### No-Filler Rules

These extend the low-quality-content gate in `Originality and Recommendation-Readiness Gates`. Run both together.

- Deletion test: for each paragraph ask 删掉这段，读者损失了哪条信息、哪个判断、哪个步骤，或是否失去理解下一段所需的前提. Keep useful terminology explanations, grounded analogies and causal connections; delete paragraphs that serve none of these purposes.
- Remove banned openers and transitions: `随着 XX 的发展`, `众所周知`, `在当今时代`, standalone transition paragraphs, `首先/其次/最后` used as the only structure, and background scene-setting placed before the first concrete fact.
- Do not restate a conclusion already stated verbatim. A closing section may compress the argument and add the applicability boundary, but must not repeat body sentences.
- Do not paraphrase official documentation without adding a judgment, a measurement, a comparison, or a limitation.
- Cut information-free adjectives such as `非常强大` or `极其丝滑` unless the number or observation that earns them follows immediately.
- Every H2 must deliver a fact, mechanism, step, comparison, measurement, decision, or necessary explanation that helps the target reader understand them.

## Article Evidence and Authenticity Rules

Apply these rules to every generated or substantially revised article unless the user explicitly asks to skip them. If a rule cannot be satisfied from available materials or verifiable sources, do not fake it; document the gap in the completion report and, when the gap weakens the article, stop before publishing.

### Real Screenshots

- Include at least one real screenshot when source materials, local project UIs, terminal output, Codex/Claude sessions, dashboards, or user-provided screenshots are available.
- Prefer screenshots that prove the article's claims: terminal/test/build output, project interface, product result, revenue/analytics dashboard, or configuration screen.
- For income, revenue, analytics, or account screenshots, only use user-provided or locally available screenshots. Redact private data, tokens, emails, customer names, order IDs, and unrelated balances before upload.
- Do not generate fake UI screenshots. If no real screenshot is available, use a deterministic diagram or generated illustration only as supporting visual material, and do not describe it as a screenshot.

### Personal Experience and Failure Cases

- Include a concrete evidence-backed case with context, action or observation, outcome and the judgment it supports. Use first-person narration only for experience attributable to the author in the materials or confirmed by the user. Label current task experiments as verification experiments and attribute external cases to their source; neither establishes the author's personal experience. Clearly marked teaching examples may explain concepts but do not substitute for empirical evidence.
- Include at least one failure case, wrong turn, limitation, or lesson learned. Good examples: a failed prompt, broken build, rejected publish attempt, misleading metric, unusable generated image, or implementation shortcut that later caused rework.
- Keep claims bounded. Use exact numbers only when they appear in source material or verified local artifacts; otherwise use qualitative wording.

### Authoritative Sources

- Cite at least 2 authoritative sources, target 3 when the topic supports it.
- Prefer primary or high-authority sources: official documentation, release notes, standards/specs, academic papers, vendor engineering blogs, government/regulatory pages, or original benchmark/data sources.
- For fast-moving AI/tooling topics, verify sources during the task instead of relying on memory. Keep any research or verification date in the private search brief or completion report, not in the visible reference entry.
- Do not cite unverifiable secondary summaries as authority when an official source exists. Do not invent source titles, URLs, dates, benchmark numbers, or quotes.
- Add a `## 参考资料` section near the end using concise bullets. Keep links as Markdown links if the publishing pipeline supports them; otherwise include source names and plain URLs.
- Format visible reference entries with the source title, publisher when useful, and URL. Never append access-date wording such as `访问日期`, `检索日期`, `Accessed`, or `Retrieved`. Preserve a verified publication or release date only when it is materially relevant to the citation.

## WeChat Ending Hook Rules

- Every generated or revised WeChat article must end with a short topic-specific engagement hook after the substantive conclusion.
- The hook should invite readers to comment with their own experience, mention that the discussion may help other domestic developers/readers, and ask readers to tap `在看` or share if the article was useful.
- Adapt the first paragraph to the article topic. Do not reuse the payment/card-declined example unless the article is actually about payments.
- End with this fixed brand follow block:

```markdown
写 AI，写成长，偶尔写投资。
关注沐风，不定期更新，全是干货。
```

- Keep the hook natural and restrained: no emojis, no excessive exclamation marks, no generic sales slogans, and no long unrelated self-promotion.
- If the `mufeng-blog-writing` skill has footer rules, this hook is still mandatory. Place it after the article's normal conclusion and before any publishing-only metadata.
- If the `mufeng-blog-writing` footer is used, format the timestamp as `YYYY.MM.DD HH:mm`, followed by the location on the next line. Example: `2026.08.30 18:20` and `沪 · 赵巷`. Do not use a date-only footer such as `2026.08.30`.
- When revising an existing article, add or update the hook once. Do not duplicate existing calls to action.

## WeChat Search Intent and Content Quality Rules

### Search Intent Research

- Research before drafting, not after the article structure is fixed.
- Prefer current WeChat evidence: `搜一搜` autocomplete, result pages, related searches, `微信指数`, and recent high-ranking results for the topic. Record the research date and evidence source.
- When direct WeChat access is unavailable, use current web search, official documentation, user-provided screenshots, or recent platform evidence as a labeled proxy. Do not describe proxy data as verified WeChat search volume or ranking data.
- Inspect 3-5 query variants and representative results to determine what readers want: explanation, troubleshooting, tutorial, comparison, decision support, or recent change. Use competitors only to identify intent and content gaps; do not copy their wording or structure.
- Choose one primary query, 3-6 supporting terms/entities, and one clear reader outcome. If the material cannot satisfy that intent truthfully, choose a narrower query or stop before drafting.

### Natural Keyword Mapping

- Put the primary query or its natural equivalent once in the title. Make the title accurately state the article's concrete value or outcome.
- Answer the primary intent in the opening paragraph immediately after the cover. Include the main entity and problem naturally within the first 120 Chinese characters when readable.
- Use the primary query or a close variant in at least one useful H2. Build other H2 headings around genuine reader questions, decisions, steps, or findings; do not force the keyword into every heading.
- Place supporting terms, named entities, synonyms, and related questions only in sections that actually answer them. Prefer semantic coverage over exact-match repetition.
- Include the primary entity/problem and concrete outcome once in the 90-120-character `summary` digest.
- Do not add keyword lists, hidden keyword blocks, visible tag blocks, mechanical repetitions, or keyword-density targets. Remove any term that makes the sentence less natural.

### Originality and Recommendation-Readiness Gates

- **Originality:** require at least one material contribution grounded in source evidence or actual work: a first-person decision, real screenshot, failure, measurement, comparison, implementation detail, or bounded conclusion. Synthesize sources in original wording; do not closely paraphrase or imitate another article's structure. Never claim a plagiarism check unless source comparisons were actually performed.
- **Account fit:** classify the topic as core, adjacent, or off-topic for the account promise `写 AI，写成长，偶尔写投资`. Core topics are AI, software development, and practical growth; investment is occasional. Reframe an adjacent topic around a credible connection. For an off-topic article, report the mismatch and stop before publishing unless the user explicitly approves it.
- **Title integrity:** ensure the title's entity, problem, timeframe, and promised outcome are supported by the body. Reject fake urgency, unexplained absolutes, misleading omissions, impersonation of official notices, and words such as `必看`, `震惊`, `封神`, `最强`, `100%`, or `官方推荐` unless the exact claim is necessary and verifiable.
- **Low-quality content:** remove generic scene-setting, repeated conclusions, empty transition paragraphs, fabricated quotes, unsupported rankings, keyword stuffing, and sections that add no evidence, decision, example, comparison, actionable step or necessary understanding prerequisite. Retain useful concept explanations and causal connections, plus limitations and counter-evidence when they materially change the conclusion.
- **Comprehension:** apply rule 6 in `mufeng-blog-writing`. For the declared reader, check the ability to explain what the thing is, why it is needed, how to start, what the result proves and what remains unproven without unexplained terminology or jumping between sections. Also verify that technical documents explain the first-principles causal chain, assumptions and boundaries. Treat this as editorial self-review unless actual readers participated; do not invent reader-test results.
- Pass these five gates before image upload and publishing. If a gate fails, revise and re-check; document any unresolved limitation in the completion report.

## SEO/GEO Frontmatter Rules

- Use `category`, not the misspelled `categery`.
- Required frontmatter fields before publishing:
  - `title`: include the core keyword or entity naturally, usually under 60 Chinese characters.
  - `slug`: SEO/GEO-friendly ASCII slug. Use the same value as `<article-slug>` for image folders and GitHub paths.
  - `author`: always `changyou`.
  - `date`: `YYYY-MM-DD`.
  - `category`: one concise human-readable category, for example `AI 编程`, `开发工具`, `iOS 开发`, `后端开发`, `前端开发`, `成长复盘`, or `投资笔记`.
  - `summary`: 90-120 Chinese characters covering the problem, solution, and outcome. Include the primary entity/problem naturally once. No Markdown, links, line breaks, or promotional filler. This overrides `mufeng-blog-writing`'s 150-200-character default and stays within the WeChat publishing script's digest limit.
  - `tags`: 4-8 tags as a YAML list for internal organization. Include the main entity/tool, technology stack, problem domain, and reader intent. Do not use `#` prefixes, render them in the body, or treat them as submitted WeChat ranking signals.
  - `coverImage`: add after GitHub upload using the uploaded cover raw URL.
- Frontmatter `summary` and `tags` are mandatory metadata, but must never be duplicated as visible `摘要` or `标签` sections in the article body.
- Put the slug in YAML frontmatter exactly as `slug: <article-slug>`.
- Use lowercase ASCII kebab-case only: `a-z`, `0-9`, and single hyphens. Do not use Chinese characters, spaces, underscores, punctuation, emoji, or URL encoding.
- Make it semantic and search-aligned: include the main entity/tool/technology plus the concrete problem, solution, or outcome. Prefer `codex-wechat-article-image-publish` over generic values like `article`, `wechat-post`, or `notes`.
- Keep it concise: 3-8 meaningful words, usually under 70 characters.
- Translate Chinese topic words into common English search terms, but preserve established product, framework, API, and library names in normalized lowercase form, for example `swiftui`, `spring-boot`, `wechat`, `codex`.
- Avoid filler and clickbait terms such as `best`, `ultimate`, `guide`, `new`, `latest`, `awesome`, unless they are genuinely part of the user's target keyword.
- Do not include dates unless the date is essential to the topic or needed to avoid a real collision. For filename collisions, prefer the file suffix (`-v2`) without changing the frontmatter slug.
- Reuse this exact slug in local image paths (`imgs/<article-slug>/...`), GitHub remote paths (`images/<article-slug>/...`), and the completion report.
- If revising an existing article that already has a good slug, preserve it. If it is missing or poor, replace it and mention the change.

Recommended frontmatter shape:

```yaml
---
title: "Superpowers Skill - 让 Claude Code 和 Codex 按工程流程做开发"
slug: superpowers-skill-claude-codex-workflow
author: changyou
date: YYYY-MM-DD
category: AI 编程
summary: "这篇文章基于真实复盘 Superpowers Skill 如何把 Claude Code 和 Codex 的临时问答转成可验证的工程流程，拆解计划、测试、实现和复盘，并说明失败案例与适用边界，帮助开发者减少返工、提升 AI 编程交付质量。"
tags:
  - Superpowers
  - Claude Code
  - Codex
  - AI 编程
  - 工程流程
coverImage: https://raw.githubusercontent.com/mf-blog/blogPictures/main/images/superpowers-skill-claude-codex-workflow/cover.png
---
```

## Workflow

1. Locate source materials, research search intent, and make an evidence inventory.
   - If the user gives a directory, use that directory. Otherwise use the current working directory.
   - Treat Markdown, text notes, transcripts, outlines, code snippets, screenshots/OCR notes, and other user-provided files in that directory as source material.
   - Ignore build/cache/vendor folders, generated image folders, previous WeChat output folders, and existing `github-image-urls.json` files.
   - Identify available real screenshots and evidence assets before drafting: project UI, terminal/test output, analytics/revenue screenshots, code diffs, diagrams, and existing article screenshots.
   - Identify personal-experience material: project context, decisions, mistakes, failed attempts, tradeoffs, and results.
   - Identify source needs: list the claims that require 2-3 authoritative references, then verify those references before finalizing the article.
   - Research current WeChat search intent using the rules above. Record the research date, evidence source, 3-5 query variants, representative result patterns, and any access limitation.
   - Select one primary intent, one primary query, 3-6 supporting terms/entities, and one concrete reader outcome. Keep this search brief outside the visible article body.
   - Read the `mufeng-blog-writing` skill and follow its workflow, tone, structure, metadata, and footer rules.
   - Before outlining, state the target reader, assumed prerequisites, one reader outcome and primary article type. Select one evidence-backed case to connect the explanations; keep this writing plan outside the visible body.
   - Before drafting, derive one canonical `article-slug` from the source material's core topic, target query, and specific outcome.

2. Generate the article.
   - Generate a professional Chinese WeChat Official Account article as Markdown. It should be publish-ready, with frontmatter `title`, `slug`, `author: changyou`, `date: YYYY-MM-DD`, `category`, `summary`, and `tags`, plus a clear `#` title and practical structure.
   - Do not generate visible `摘要` or `标签` blocks before the main body. Store both values only in YAML frontmatter, overriding the `mufeng-blog-writing` output-format default.
   - Apply the keyword map while drafting: primary query in the title, direct intent answer in the opening, a natural H2 variant, and supporting terms only in relevant sections. Do not retrofit repeated keywords after drafting.
   - For a technical-subject article, organize the draft around the `Technical Explainer Contract` while writing. Do not draft first and retrofit the required answers afterwards.
   - Include the evidence and authenticity requirements: real screenshot placements when available, a clearly attributed case, at least one failure/lesson/limitation, and `参考资料`. Do not invent author experience from the task's execution history.
   - Do not add a standalone or disguised `真实开发过程`/`材料整理过程`/`证据链合成过程` section. Do not narrate files inspected, commands run, source-count inventory, research steps, or missing screenshots as article content.
   - In `参考资料`, omit access dates and access-date phrases. Keep verification dates only in the non-visible search brief or completion report.
   - Remove all Emoji from the generated article. Do not append `📌 声明：本文由 AI 辅助完成` or any equivalent AI-assist declaration.
   - Put `参考资料` after the substantive conclusion and before the required WeChat ending hook.
   - Append the required WeChat ending hook before saving the article.
   - Save the generated Markdown article in the requested directory unless the user specifies another output path. If no filename is specified, prefer `<article-slug>.md` over the Chinese title. If a target filename already exists, append `-v2`, `-v3`, etc. rather than overwriting.
   - The generated article becomes the target article for all later steps.

3. Read the generated article and make an image plan.
   - Use one cover image.
   - Prioritize real screenshots for evidence-heavy sections. Use generated illustrations only for the cover or for ideas that cannot be shown with real artifacts.
   - Use the shared visual reference to select the topic variant and record each image's purpose, main relationship, composition, palette and references. Compare relevant local images when available; retain brand continuity without repeating the same metaphor.
   - Add inline screenshots or illustrations at natural breakpoints: after the opening setup, before dense technical sections, after major H2 sections, or near claims that need visual proof.
   - Avoid inserting images inside code blocks, tables, lists, blockquotes, or YAML frontmatter.
   - Choose image count by explanatory or evidence value, not character intervals or section count. Omit inline illustrations that add nothing beyond the text.

4. Prepare PNG image assets.
   - Recommended local layout: `imgs/<article-slug>/cover.png`, `imgs/<article-slug>/shot-01.png`, `imgs/<article-slug>/fig-01.png`.
   - Copy, redact, crop, or convert real screenshots into this folder as PNGs. Keep screenshot filenames distinct from generated figure filenames.
   - Generate the cover directly with Codex built-in ImageGen by default; no provider-selection or switching confirmation is needed. Optional generated illustrations also default to built-in ImageGen unless the user specifies otherwise. Save the complete prompt before generation and keep every adopted image in the project as required by the shared visual reference.
   - Default to a complete text-free cover with a recognizable topic-specific subject and one supporting relationship. For technical articles, apply the Technical Visual Profile to choose the subject first; precise engineering geometry and a single accent are optional, not mandatory. Check topic recognition as well as crop safety; recompose instead of shrinking the subject. Do not reserve unused title space or use unrelated humanistic decoration.
   - For inline illustrations, explain exactly one nearby idea. For technical content, select screenshot, flowchart, framework, comparison, sequence or conceptual illustration using the Technical Visual Profile; non-technical content uses the shared topic variant.
   - If exact labels, arrows, UI states, code, or numeric relationships are essential, use a verified screenshot or render a deterministic diagram locally and save it as PNG; do not rely on ImageGen for exact technical notation.

5. Validate image files, article evidence, search alignment, and content quality.
   - Confirm each image asset exists, is non-empty, and is PNG.
   - Prefer keeping each PNG under 5 MB. Compress or resize only if upload/publish tools reject the file.
   - Confirm generated visuals are article-specific, restrained, legible at article width, and free of the prohibited AI clichés. Reject and regenerate generic neon/glowing-network/floating-UI/glossy-3D results.
   - Run the shared reference's thumbnail and crop checks on the actual images. Keep brand colors consistent; revise repetitive metaphors or unreadable compositions. Record missing references or previews honestly.
   - Confirm the article includes: real screenshots when available, a clearly attributed case, failure/lesson/limitation, and 2-3 authoritative sources.
   - Confirm no `真实开发过程` or equivalent meta-production section remains in the article.
   - Confirm visible `参考资料` entries contain no access-date wording or appended access dates.
   - Confirm `summary` is 90-120 Chinese characters and accurately describes the published body without promotional filler.
   - Confirm the title, opening, at least one useful H2, and relevant body sections implement the keyword map naturally. Remove repetitions added only for ranking.
   - Run the technical-contract coverage check: name the section that answers each of the eight required items. Fix a missing answer by rewriting or merging sections, never by adding an empty heading.
   - Apply the `No-Filler Rules` to every paragraph and heading before running the quality gates.
   - Run the originality, account-fit, title-integrity, low-quality-content and comprehension gates, including first-principles analysis. Revise every failure before continuing.
   - If authoritative sources or real screenshots are missing for claims that depend on them, fix the article before publishing.

6. Upload images to GitHub.
   - Fixed image host:
     - Repository: `https://github.com/mf-blog/blogPictures`
     - Branch: `main`
     - Directory: `images`
   - Use this repository and directory for future article images. Do not read `MUFENG_GITHUB_IMAGE_REPO`, `MUFENG_GITHUB_IMAGE_BRANCH`, or `MUFENG_GITHUB_IMAGE_DIR` for this skill unless the user explicitly asks to override the fixed image host.
   - Use the bundled helper:

```bash
python3 "$SKILL_DIR/scripts/upload_github_images.py" \
  --repo "mf-blog/blogPictures" \
  --branch "main" \
  --remote-dir "images/<article-slug>" \
  --json-out "imgs/<article-slug>/github-image-urls.json" \
  imgs/<article-slug>/cover.png \
  imgs/<article-slug>/shot-01.png \
  imgs/<article-slug>/fig-01.png
```

7. Insert image URLs into the generated Markdown article.
   - Add or update frontmatter with `coverImage: <cover-url>` while preserving the existing `slug`, `category`, `summary`, and `tags`.
   - If `category`, `summary`, or `tags` are missing or only present in the body, add them to YAML frontmatter before publishing.
   - Remove any visible metadata-only `摘要` heading/block and `标签` line/block from the body after their values are safely present in frontmatter. Do not remove a substantive section merely because it discusses summaries or tags as the article topic.
   - Always insert the uploaded cover as the first body image, immediately after the H1 and before the opening paragraph. Do not add a visible caption, divider, summary, tags, author, or date before it. Use this order:

```markdown
# <article-title>

![<concise-cover-alt-text>](<cover-url>)

<opening-paragraph>
```

   - Keep the same uploaded URL in frontmatter `coverImage`, the first body image, and the publishing command's `--cover` argument. Do not upload or generate a second copy solely for the body.
   - Insert real screenshots and inline illustrations as normal Markdown images:

```markdown
![Codex 实际修改过程截图](https://raw.githubusercontent.com/mf-blog/blogPictures/main/images/<article-slug>/shot-01.png)
```

   - Use concise alt text that describes the real artifact or idea, not `image1`.
   - Preserve existing user content and formatting.

8. Upload and verify a WeChat Official Account draft.
   - Resolve theme/color using the shared visual reference. The command below is the default starting point only; substitute explicit user, article or account preferences. Before upload, inspect local rendered previews at 375px and 430px and record unsupported layout differences. Keep the final Markdown as the publishing input.
   - Read `$HOME/.baoyu-skills/baoyu-post-to-wechat/EXTEND.md` if present for defaults.
   - Follow `mufeng-wechat-publish-full` for API draft upload and verification. “发布到公众号” defaults to a draft, not public publication or mass sending.
   - Use API; do not open the backend or invoke browser automation/Computer Use unless the user explicitly requests browser operation. A saved browser preference or an API error alone does not authorize switching.
   - Resolve the requested account from local configuration and pass `--account <account-alias>`; do not fall back to another account when credentials are missing.
   - Use the existing baoyu script directly:

```bash
bun "$MUFENG_WECHAT_SCRIPT" \
  <article.md> \
  --account <account-alias> \
  --theme modern \
  --color '#59766C' \
  --author changyou \
  --cover <cover-url>
```

   - Always include a title if it cannot be reliably extracted from frontmatter or the first H1.
   - Record outbound IP where possible, then inspect actual API errors. Do not require a backend whitelist pre-check. On explicit invalid-IP errors (such as `40164`), stop blind retries until the whitelist or configured route changes; HTTP 401/403 alone does not prove an IP issue.
   - After `draft/add`, separately call `draft/get` with the returned `media_id`, using the same account and transport. Verify title, author, body, cover and image references; save a redacted record. On read-back failure, preserve the ID and report upload success separately without creating a duplicate draft.
   - Original declaration and platform topic tags unsupported by the API remain pending manual settings and do not block upload. Frontmatter tags are not platform topic tags.
   - Report local article completion, draft upload, read-back verification and public publication separately. Only execute public publication or mass sending when explicitly requested; verify its final status.

## Pre-Publish Evidence Checklist

Do not publish until this checklist has been checked against the final Markdown:

- [ ] Final visible article has been counted using the writing skill's method: normally 1000–3000 字, at most 4000 字; 3001–4000 字 has a concrete content justification. No appendix or code screenshot bypasses the budget.
- [ ] Every code, command, configuration, pseudocode or log excerpt has a reader-task or evidence necessity; explanations replace dispensable snippets, and complete implementations are linked outside the article.
- [ ] SEO/GEO frontmatter includes `title`, `slug`, `author`, `date`, `category`, `summary`, `tags`, and uploaded `coverImage`.
- [ ] A dated search brief records the primary intent, primary query, 3-6 supporting terms, evidence source, and any proxy-data limitation.
- [ ] The title, opening, at least one useful H2, and relevant body sections map keywords naturally; no keyword list, stuffing, or mechanical repetition remains.
- [ ] Frontmatter `summary` is 90-120 Chinese characters, matches the body, and contains the primary entity/problem and outcome naturally.
- [ ] Originality gate passed with at least one material first-hand or evidence-backed contribution; no copied wording, imitated structure, or unperformed plagiarism claim remains.
- [ ] Account-fit gate passed for `写 AI，写成长，偶尔写投资`, or explicit user approval for an off-topic article is documented.
- [ ] Title-integrity gate passed: every promise is supported and no fake urgency, unsupported absolute, misleading omission, or official impersonation remains.
- [ ] Low-quality-content gate passed: every section adds evidence, a decision, example, comparison, finding, actionable step or necessary understanding prerequisite.
- [ ] Reader and single outcome are defined; primary article type governs depth; essential terms are explained before use; one concrete case connects the main sections; advanced details are included only when needed for the task.
- [ ] Comprehension gate passed as editorial self-review or an accurately reported real reader test: the target reader can explain what it is, why needed, how to start, what results establish and what remains unproven.
- [ ] Technical Explainer Contract covered at the declared reader's and article type's depth: 技术点是什么, 存在的意义, 有什么作用, 第一性原理, 怎么使用, 给出实战案例, and 痛点与解决方法 are answered in named sections without restating facts, or the article is documented as non-technical.
- [ ] 第一性原理 deeply explains the causal chain from basic facts and constraints to mechanism and outcome, with assumptions, tradeoffs and failure boundaries; evidence supports it, and unknown internals are explicitly bounded. Field or module inventories do not count as this explanation.
- [ ] No-Filler Rules applied: no banned opener, empty transition, verbatim restated conclusion, or unearned adjective remains; every H2 delivers a fact, mechanism, step, comparison, measurement, decision or necessary concept explanation, and useful understanding prerequisites are retained.
- [ ] The body contains no visible metadata-only `摘要` or `标签` blocks; `summary` and `tags` exist only in frontmatter.
- [ ] The first rendered body element is the uploaded cover image: in Markdown it appears immediately after the H1, with no text, caption, or divider before it.
- [ ] At least one real screenshot is included when available, and every screenshot is redacted as needed.
- [ ] Generated images are used only as cover/illustrations, not as fake product, revenue, Codex, or Claude screenshots.
- [ ] Each generated visual is tied to a concrete article concept, uses a restrained 2-4-color palette and clear hierarchy, and avoids the prohibited AI clichés.
- [ ] Shared visual reference applied; complete cover, thumbnail/crop checks and 375px/430px layout previews checked on actual artifacts, or missing checks explicitly recorded. Local references were compared when available; brand consistency does not require a different palette each time.
- [ ] The article contains a concrete evidence-backed case with accurate attribution; current verification experiments and external cases are not presented as the author's personal history.
- [ ] The article includes at least one failure case, limitation, wrong turn, or lesson learned.
- [ ] The article contains no `真实开发过程`, `材料整理过程`, `证据链合成过程`, or equivalent meta-production section.
- [ ] The article cites 2-3 authoritative sources in `参考资料`; fast-moving facts have been verified during the task.
- [ ] Visible `参考资料` entries do not contain `访问日期`, `检索日期`, `Accessed`, `Retrieved`, or appended access dates.
- [ ] No Emoji appears anywhere in the final Markdown.
- [ ] No AI-assist, AI-generated, or model-use declaration appears in the article body or footer.
- [ ] The final engagement hook and fixed brand follow block are present exactly once.

## GitHub Upload Notes

- The helper uses `gh api`; GitHub CLI must be installed and authenticated.
- It rejects non-PNG files by default.
- If a remote path already exists, it appends a timestamp suffix unless `--overwrite` is passed.
- Raw URLs are printed and optionally saved to JSON for precise insertion.

## Completion Report

Report:

- Source material directory used.
- Article slug.
- Frontmatter category, summary, and tags.
- Search brief: research date, evidence source, primary intent, primary query, supporting terms, reader outcome, and any proxy-data limitation.
- Keyword mapping result: title, opening, H2, and body placements; confirm no stuffing or visible keyword/tag block.
- Length and code check: report counting method, final total, whether the 1000–3000 字 target and 4000 字 ceiling are met, and the number and necessity of retained code-like snippets (0 when none).
- Digest check: report the `summary` character count and confirm it is within 90-120 characters.
- Quality-gate results: originality evidence, account-fit classification, title-integrity result, and low-quality-content result.
- Reader profile, assumed prerequisites, primary article type, single reader outcome, and comprehension-gate result; distinguish editorial self-review from any actual reader testing.
- First-principles analysis result for technical documents: core constraints, causal mechanism, evidence, assumptions and failure boundaries, plus any unknown internals.
- Body-opening check: confirm visible summary/tag blocks were removed and the cover is the first rendered body element.
- Generated article path.
- Article path changed.
- Technical-contract coverage table: each of the eight required items mapped to the section that answers it, or the reason the article is exempt.
- Evidence inventory: real screenshots used, case attribution (author experience, current verification experiment or external source), and failure/lesson/limitation added.
- Article-structure check: confirm no real-development-process or other meta-production section was added.
- Authoritative sources cited, including count and whether they were verified during the task.
- Reference-format check: confirm visible references omit access dates and access-date wording.
- Emoji and disclosure check result: confirm no Emoji or AI-assist declaration remains.
- Whether the required WeChat ending hook was added or preserved.
- Image direction used: subject, visual form, palette/material language, comparison against recent local images when available, and AI-cliché check result.
- Cover URL and inline image URLs.
- WeChat publishing method and result, including draft `media_id` if the API returns one.
- Any skipped step or manual action still required.
