---
name: mufeng-writing-skill
description: Chinese technical blog writing for mufeng.blog with Joey's tone, clear problem-solution structure, runnable code examples, and publish-ready SEO metadata. Use when drafting or revising technical posts, tutorials, or troubleshooting articles, especially for iOS (Swift/Objective-C), Java/Spring Boot, Vue.js, or JavaScript/TypeScript.
---

# Mufeng Blog Writing

## Overview
Produce mufeng.blog technical articles in Joey's friendly, professional tone. Keep structure clear, include practical code with Chinese comments, and deliver title, summary, and tags ready for publishing.

## Workflow
1. Clarify the request. Confirm topic, article type (tech share, tutorial, or problem-solving), target stack, and expected depth. If missing, assume a standard technical article and state assumptions.
2. Select the structure. Use the templates in `references/templates.md` and match the article type.
3. Draft the content. Follow `references/identity.md`, ensure code is runnable and contextualized, and include best practices and pitfalls where relevant.
4. Add metadata. Provide an optimized title, a 150-200 Chinese character summary, and 4-8 tags using `references/seo-checklist.md`.
5. Run quality checks. Use the checklist in `references/seo-checklist.md` and fix issues.

## Output Format
- Return Markdown only.
- Start with `# 标题`.
- Include `摘要` and `标签` blocks before the正文 if they are not provided.
- Use fenced code blocks with language tags.

## References
- `references/identity.md`: Blog identity, tone, and language rules.
- `references/templates.md`: Article and tutorial templates plus reusable snippets.
- `references/code-standards.md`: Code example conventions and language samples.
- `references/stack-guidelines.md`: Stack-specific emphasis and pitfalls.
- `references/seo-checklist.md`: SEO guidance and publish checklist.
