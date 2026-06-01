# Bilingual Storybook Maker

Turn Markdown story material into bilingual English-Chinese picture books.

This Agent helps creators, parents, educators, and language-learning content makers transform plain story drafts into structured picture-
book projects with scene breakdowns, child-friendly narration, illustration prompts, generated page artwork, and final PDF storybooks.

## What It Does

- Reads Markdown story files from your project
- Splits the story into picture-book scenes
- Writes natural Chinese narration for each page
- Writes child-friendly English narration for each page
- Generates illustration prompts for every scene
- Uses Codex built-in image generation for page illustrations
- Assembles final PDF storybooks:
  - `storybook.pdf` for Chinese
  - `storybook_en.pdf` for English

## Best For

- Children's picture books
- Bilingual Chinese-English reading materials
- Parent-child reading content
- Language-learning stories
- Classic story adaptation
- Educational storytelling projects
- Turning rough Markdown drafts into polished visual books

## Typical Workflow

1. Provide one or more Markdown story files.
2. Ask the Agent to create a bilingual picture book.
3. The Agent reads the story and chooses a suitable page count.
4. It creates scene plans, bilingual narration, and illustration prompts.
5. It generates one full-page illustration per scene.
6. It builds Chinese and English PDF versions using the same image set.
7. It checks page count, image count, and rendered output.

## Page Count Strategy

The Agent can automatically choose the page count based on story length and complexity:

| Story Type | Recommended Length |
|---|---:|
| Short story / single episode | 12 pages |
| Medium chapter / several story beats | 16 pages |
| Formal picture-book chapter | 20 pages |
| Long or complex chapter | 24 pages |

You can also request a fixed page count, such as 12, 16, 20, or 24 pages.

## Example Prompts

```text
Use this Agent to read all Markdown files in the current project and generate a bilingual English-Chinese picture book PDF.

Create a 12-page bilingual picture book from this Markdown story. Keep the Chinese natural and the English suitable for children.

Turn this classic Chinese story into a English-Chinese picture book with one illustration per page.

## Output Files

A typical output folder includes:

build/storybook_auto/
├── scenes.parsed.md
├── prompts.generated.md
├── manifest.json
├── images/
│   ├── scene_01.png
│   ├── scene_02.png
│   └── ...
├── storybook.pdf
└── storybook_en.pdf

## Design Principles

- One clear story moment per page
- Short narration suitable for children
- Natural Chinese, not stiff textbook language
- English translation focused on clarity and emotion, not literal word-for-word translation
- Consistent visual style across all pages
- No readable text inside generated images
- No watermarks, captions, speech bubbles, or embedded labels in illustrations

## Important Notes

This Agent uses Codex built-in image generation. It does not call the OpenAI Images API and does not require OPENAI_API_KEY.

The helper script handles deterministic text, layout, image checking, and PDF assembly. Image creation is handled through Codex's built-in image generation workflow.

## 中文说明

这个 Agent 可以把 Markdown 故事素材制作成中英双语绘本。它会自动拆分分镜，生成中文旁白、英文旁白和插画提示词，使用 Codex 内置生图能力生成每页插图，并最终输出中文版和英文版 PDF。

适合用于儿童绘本、亲子阅读、双语学习、经典故事改编和教育内容制作。
