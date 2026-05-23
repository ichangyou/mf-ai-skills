---
name: mufeng-blog-writing
description: Chinese technical blog writing for mufeng.blog with Joey's tone, clear problem-solution structure, runnable code examples, and publish-ready SEO metadata. Use when drafting or revising technical posts, tutorials, or troubleshooting articles, especially for iOS (Swift/Objective-C), Java/Spring Boot, Vue.js, or JavaScript/TypeScript.
---

# mufeng-blog-writing

## Overview
Produce mufeng.blog technical articles in Joey's friendly, professional tone. Keep structure clear, include practical code with Chinese comments, and deliver title, summary, and tags ready for publishing. By default, save the generated article as a Markdown file in the current working directory.

## Workflow
1. Clarify the request. Confirm topic, article type (tech share, tutorial, or problem-solving), target stack, and expected depth. If missing, assume a standard technical article and state assumptions.
2. Select the structure. Use the templates in `references/templates.md` and match the article type.
3. Draft the content. Follow `references/identity.md`, ensure code is runnable and contextualized, and include best practices and pitfalls where relevant.
4. Add metadata. Provide an optimized title, a 150-200 Chinese character summary, and 4-8 tags using `references/seo-checklist.md`.
5. Append signature footer. Unless the user explicitly asks to skip, add a footer block at the end of the article with timestamp, location, and AI-assist declaration.
6. Run quality checks. Use the checklist in `references/seo-checklist.md` and fix issues.
7. Save output file. Unless the user explicitly asks not to save, write the final Markdown article to the current working directory as a `.md` file.

## Output Format
- Return Markdown only.
- Start with a YAML frontmatter block containing `title`, `author: changyou`, and `date: YYYY-MM-DD` (today's date).
- Then `# 标题` heading.
- Include `摘要` and `标签` blocks before the正文 if they are not provided.
- Use fenced code blocks with language tags.
- Append a default footer block at the end of the article (unless user says not to):
  - Line 1: `YYYY.MM.DD HH:mm`
  - Line 2: `沪 · 赵巷` (or user-provided location)
  - Blank line
  - Line 4: `📌 声明：本文由 AI 辅助完成`
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
