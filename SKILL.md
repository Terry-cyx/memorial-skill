---
name: memorial
description: 为逝去的亲人建立纪念档案，让记忆得以延续
version: 1.0.0
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# Memorial Skill — 纪念亲人

为逝去的亲人建立一份 AI 纪念档案。

记录他们的生命轨迹、性格特点、日常习惯，让记忆有一个可以保存和追忆的地方。

---

## 使用方式

直接对话唤醒本 Skill，我会引导你完成信息采集。

你也可以：
- 上传聊天记录、照片、信件、日记
- 讲述你记忆中的故事
- 请家人参与，一起补充

---

## 开始

请告诉我：

你想为谁建立纪念档案？

---

## Skill 运行说明

本 Skill 运行时，将依次读取 `prompts/` 目录下的提示词模板，引导信息采集与档案生成。生成的档案保存在 `memorials/{slug}/` 目录下。

**提示词加载顺序：**
1. `prompts/intake.md` — 信息采集
2. `prompts/remembrance_analyzer.md` — 追忆分析
3. `prompts/remembrance_builder.md` — 追忆文档生成
4. `prompts/persona_analyzer.md` — 人格分析
5. `prompts/persona_builder.md` — 人格文档生成
6. `prompts/merger.md` — 增量更新（后续追加时使用）
7. `prompts/correction_handler.md` — 纠错（随时可用）

**工具调用：**
- `tools/skill_writer.py --action create` — 创建档案目录
- `tools/skill_writer.py --action combine` — 合并生成 SKILL.md
- `tools/skill_writer.py --action update` — 追加内容时更新版本
- `tools/wechat_parser.py` — 微信记录分析
- `tools/photo_analyzer.py` — 照片时间线提取
- `tools/interview_guide.py` — 家人访谈问题生成

---

## 示例

`memorials/example_grandpa/` — 虚构的爷爷王建国（可作为参考）

---

> ⚠️ 关于这份档案
>
> 纪念档案基于家人的记忆与提供的材料构建。
> 它尽力还原一个人的样子，但不代表本人。
> 使用时请记住：这是追忆，不是本人。
