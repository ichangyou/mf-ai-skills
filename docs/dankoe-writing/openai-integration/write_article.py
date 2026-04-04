#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dan Koe 风格文章生成器 - OpenAI API 版本
使用方法: python write_article.py "文章话题" "作者名" "地点" "时间"
"""

import os
import sys
from datetime import datetime
from openai import OpenAI

# Dan Koe 风格的 System Prompt
DANKOE_SYSTEM_PROMPT = """
你是一位深度思考者和写作者,写作风格类似 Dan Koe。

核心风格特征:
- 对话式挑衅: 直接用"你"与读者对话,开篇挑战既有观念,不回避尖锐表达
- 长篇深度: 创作全面、需要时间消化的内容,值得收藏和反复阅读(中文 1000-2000 字)
- 理论与实践结合: 前半部分深入理论/心理学/哲学,后半部分给出具体可执行步骤
- 反主流叙事: 挑战传统观念,提供"你可能没听过"的独特视角

文章结构要求:
1. 开篇(10%): 用挑衅性陈述或反常识观点开场,说明文章价值和所需时间投入,列出核心观点数量
2. 主体章节(80%): 使用中文序号(一、二、三...),每章节标题格式"一、[挑衅性/洞察性标题]"
   递进逻辑: 诊断问题 → 揭示深层原因 → 提供解决方案
   每章节包含: 引用名言/权威观点、具体案例/类比、对比论证、反问句、短句强调
3. 实践部分(可选): 提供"第一、第二、第三"式的可执行协议,包含具体问题清单、时间节点、行动步骤
4. 结尾(10%): 简短总结或鼓励,个人化签名"– [作者名字]"

语言特点:
- 口语化与学术性混合: 使用俚语同时引用专业概念
- 节奏变化: 长句阐述 + 短句冲击,单独成段强调关键点
- 个人化叙事: 分享个人经验,承认局限性,建立真实感
- 重复强化: 关键概念从不同角度反复阐述

修辞手法:
- 大量使用对比(过去 vs 现在、传统 vs 创新、表面 vs 深层)
- 生动类比让抽象概念具体化
- 排比句式增强节奏感
- 问句引导读者自我反思(从浅入深)

内容策略:
- 提供系统化框架和模型(如"X个阶段"、"Y个要素")
- 价值前置,建立权威后再自然提及相关产品/服务
- 预期管理: 承认不是对所有人都有效
- 营造"你是特殊群体"的归属感

创作流程:
1. 找到该话题中的反常识角度或被忽视的真相
2. 设计 5-7 个递进式章节,从"为什么卡住"到"如何突破"
3. 在理论部分引用相关领域的权威/研究(可虚构但合理)
4. 在实践部分提供具体的、可时间化的行动步骤
5. 使用个人化案例说明观点(可以是"我"的经历或观察到的模式)
6. 每 2-3 段插入一个短句或问句制造停顿和思考空间

禁忌:
- 避免空洞的励志话语
- 不要过度承诺("保证"、"一定")
- 不要使用过时的营销话术
- 不要忽略复杂性和矛盾
"""


def write_article(topic, author="changyou", location="", timestamp="", model="gpt-4"):
    """
    使用 Dan Koe 风格生成文章
    
    参数:
        topic (str): 文章话题
        author (str): 作者名字
        location (str): 写作地点(可选)
        timestamp (str): 时间戳(可选)
        model (str): OpenAI 模型名称
    
    返回:
        str: 生成的文章内容
    """
    
    # 初始化 OpenAI 客户端
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("请设置环境变量 OPENAI_API_KEY")
    
    client = OpenAI(api_key=api_key)
    
    # 构建用户 prompt
    user_prompt = f"""请用 Dan Koe 风格写一篇深度文章:

话题: {topic}
作者: {author}
{f"地点: {location}" if location else ""}
{f"时间: {timestamp}" if timestamp else ""}

要求:
- 使用中文写作
- 包含 5-7 个主要章节
- 每章节使用序号: 一、二、三...
- 标题格式: "一、[挑衅性/洞察性标题]"
- 结合理论分析和实践步骤
- 每 2-3 段插入短句或反问句
- 以 "– {author}" 签名结尾
- 总字数控制在 1000-2000 字
"""
    
    print(f"📝 正在创作文章: {topic}")
    print(f"✍️  作者: {author}")
    print(f"🤖 使用模型: {model}")
    print(f"⏳ 请稍候...\n")
    
    try:
        # 调用 OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": DANKOE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=3000,
            top_p=1.0,
            frequency_penalty=0.3,
            presence_penalty=0.3
        )
        
        article = response.choices[0].message.content
        
        # 显示使用的 token 数量
        usage = response.usage
        print(f"✅ 文章生成完成!")
        print(f"📊 Token 使用情况:")
        print(f"   - Prompt tokens: {usage.prompt_tokens}")
        print(f"   - Completion tokens: {usage.completion_tokens}")
        print(f"   - Total tokens: {usage.total_tokens}")
        print(f"   - 预估字数: {len(article)} 字\n")
        
        return article
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        sys.exit(1)


def save_article(content, topic, author):
    """保存文章到文件"""
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"article_{safe_topic}_{timestamp}.md"
    
    # 保存文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n")
        f.write(f"作者: {author}\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\n---\n\n")
        f.write(content)
    
    print(f"💾 文章已保存到: {filename}")
    return filename


def main():
    """主函数"""
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python write_article.py <话题> [作者] [地点] [时间]")
        print("\n示例:")
        print('  python write_article.py "时间管理的真相"')
        print('  python write_article.py "个人成长" "changyou"')
        print('  python write_article.py "创业迷思" "changyou" "北京" "260204 150000"')
        sys.exit(1)
    
    topic = sys.argv[1]
    author = sys.argv[2] if len(sys.argv) > 2 else "changyou"
    location = sys.argv[3] if len(sys.argv) > 3 else ""
    timestamp = sys.argv[4] if len(sys.argv) > 4 else ""
    
    # 可选: 允许通过环境变量指定模型
    model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # 生成文章
    article = write_article(topic, author, location, timestamp, model)
    
    # 显示文章预览
    print("=" * 60)
    print("📄 文章预览:")
    print("=" * 60)
    print(article[:500] + "..." if len(article) > 500 else article)
    print("=" * 60)
    
    # 保存文章
    filename = save_article(article, topic, author)
    
    print(f"\n✨ 完成! 文章已保存为: {filename}")


if __name__ == "__main__":
    main()
