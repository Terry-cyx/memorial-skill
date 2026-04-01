<div align="center">

# Memorial.skill

> *"You're gone, but I still remember the way you held your teacup."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

Your grandfather is gone, leaving behind a garden and decades of unspoken words.<br>
Your mother is gone, and you realize you can barely remember the phrase she always said.<br>
Your old friend is gone, and the inside jokes only the two of you understood now have only one keeper.<br>
They left, but you don't want the memories to disappear with them.<br>

**Turn those chat logs, photos, and stories into a memorial archive that can be preserved and revisited.**

<br>

> 💡 **If they're still here:**
> Starting the archive now is even better.
> A person telling their own story in their own words is ten times richer than reconstructing it afterward.
> This archive can be a gift to you, and to everyone who comes after.

<br>

Provide source materials (WeChat logs, QQ messages, photos, letters, family interviews) plus your own memories.<br>
Generate an **AI memorial that truly remembers who they were** —<br>
speaks with their catchphrases, recalls the places they lived, reflects how they would have seen things.

> ⚠️ **This archive is built from memory. It represents remembrance, not resurrection.**

[Data Sources](#data-sources) · [Installation](#installation) · [Usage](#usage) · [Examples](#examples) · [中文](README.md)

</div>

---

## Data Sources

| Source | Format | Notes |
|--------|--------|-------|
| WeChat chat logs | WeChatMsg / exported txt | Recommended — richest language data |
| QQ chat logs | txt / mht export | Good for older generations or early records |
| Audio | mp3 / m4a / wav / ogg / flac | Voice messages, interview recordings, family tapes — auto-transcribed |
| Photos | JPEG/PNG with EXIF | Extracts life timeline and frequent locations |
| Handwritten letters/diaries | Photos or scans | Invaluable firsthand material |
| Social media posts | Screenshots or text | Captures public expression style |
| Family interviews | Interview transcripts | Built-in interview guide to help extract memories |
| Work/hobby documents | PDF / Word / text | Reconstructs professional identity and interests |
| Narration | Plain text | Your subjective memory — equally valid |

---

## Installation

### Claude Code

> **Important**: Claude Code looks for skills in `.claude/skills/` from the **git repository root**. Run these commands from the correct location.

```bash
# Install to current project (run from git repo root)
mkdir -p .claude/skills
git clone https://github.com/yourname/memorial-skill .claude/skills/create-memorial

# Or install globally (available in all projects)
git clone https://github.com/yourname/memorial-skill ~/.claude/skills/create-memorial
```

### Dependencies (optional)

```bash
pip3 install -r requirements.txt
```

> `pypinyin` — Chinese name to pinyin slug conversion; `Pillow` — photo EXIF extraction. Neither is required; the tool degrades gracefully without them.

---

## Usage

In Claude Code, type:

```
/create-memorial
```

Answer three questions — name and relationship, basic background, personality impression — then choose your data sources.
All fields can be skipped. Even a brief oral description generates a working archive; you can always add more later.

Once created, use `/{slug}` to open the memorial and begin remembering.

### Commands

| Command | Description |
|---------|-------------|
| `/list-memorials` | List all memorial archives |
| `/{slug}` | Full archive (remembrance + persona) |
| `/{slug}-remembrance` | Remembrance mode (life story, timeline) |
| `/{slug}-persona` | Persona mode (how they would speak and act) |
| `/{slug}-interview` | Generate family interview questions |
| `/memorial-rollback {slug} {version}` | Roll back to a previous version |
| `/delete-memorial {slug}` | Delete |

---

## Examples

> Input: `Grandpa, born 1938, from Hunan, railway worker in Beijing, grew vegetables after retirement, quiet, always said "taking a loss is a blessing"`

**Scenario 1: Recalling a Story**

```
You          ❯ Tell me about grandpa when he was young

Memorial     ❯ He rarely talked about that period on his own.
               But grandma once told me — during the Cultural Revolution,
               he wrapped his books in oilpaper and buried them in the garden.
               When reform came, he dug them up one by one, still readable.
               He said one thing: "Books can't be burned. Knowledge can't be severed."
```

**Scenario 2: Asking What He'd Say**

```
You          ❯ If I told him I got into university, what would he say?

Memorial     ❯ He probably wouldn't say anything.
               He'd put two extra pieces of food on your plate, then go to the garden alone.
               Come back with red eyes. You'd ask what's wrong.
               He'd say: "Nothing. Wind got in my eyes."
               — This is a reflection based on his character, not a statement from him.
```

**Scenario 3: Writing an Eulogy**

```
You          ❯ Help me put together a eulogy for him

Memorial     ❯ Wang Jianguo. Born 1938 in Hunan. Passed 2023, age 85.
               He worked in Beijing for 65 years, tended his garden for 25.
               He never said "I love you," but he poured water for grandma every morning —
               not once in their 58 years together did he skip it.
               His phrase was "taking a loss is a blessing"...
```

**Scenario 4: Preparing a Family Interview**

```
You          ❯ I want to ask grandma about him. Give me some questions

Memorial     ❯ Interview questions for his spouse:
               1. How did you two meet?
               2. How did he show love — through words, or through actions?
               3. Did you have any shared rituals or routines?
               4. What's one thing he did that moved you most?...
```

---

## Features

### Generated Archive Structure

Each memorial has two parts working together:

| Part | Content |
|------|---------|
| **Part A — Remembrance Archive** | Life timeline, life roles, values and beliefs, daily habits, signature stories, relationship network, regrets and last words, legacy and impact |
| **Part B — Persona Archive** | 5+1 layer structure: Ethical rules → Identity anchor → Language style → Emotional patterns → Relationship behavior → **Era background layer** |

How it works: `Question received → Remembrance provides the material → Persona shapes how they'd respond → Output delivered in reflective voice`

### Era Background Layer (unique to memorial-skill)

For people born before 1985, historical events profoundly shaped how they thought and behaved. This layer maps birth decade to specific behavioral tendencies:

| Birth Era | Historical Context | Behavioral Influence |
|-----------|-------------------|---------------------|
| 1930–1945 | WWII, Civil War | Strong survival instinct, extreme frugality, political caution |
| 1945–1965 | Three-Year Famine, Cultural Revolution | Never wastes food, avoids political speech, collectivist values |
| 1965–1985 | Reform and Opening Up | Pragmatic, hardworking, values stability |

### Supported Tags

**Speech style**: Quiet · Talkative · Tough exterior, soft heart · Reserved · Likes to lecture · Dialect accent

**Expressing love**: Through actions · Through words · Silent care · Pride hidden behind strictness · Doting on grandchildren

**Values**: Principled · Self-sacrificing · Frugal · Warm-hearted · Expects nothing in return · Face-conscious · Stubborn

**Relationship style**: Head-of-household · Quiet supporter · Strict parent · Lenient grandparent

### Evolution

- **Append materials** → New chat logs, photos, or oral accounts → Auto-analyzed and merged into existing content, never overwritten
- **Conversation corrections** → "They wouldn't say that" → Written into Correction log, takes effect immediately
- **Version management** → Auto-backup before every update → Rollback to any of the last 10 versions

---

## Project Structure

This project follows the [AgentSkills](https://agentskills.io) open standard:

```
create-memorial/
├── SKILL.md                      # Skill entry point (standard frontmatter)
├── prompts/                      # Prompt templates
│   ├── intake.md                 #   3-question intake dialogue
│   ├── remembrance_analyzer.md   #   Life story extraction (8 dimensions)
│   ├── remembrance_builder.md    #   remembrance.md generation template
│   ├── persona_analyzer.md       #   Persona extraction (era layer, tag translation table)
│   ├── persona_builder.md        #   persona.md 5+1 layer template
│   ├── merger.md                 #   Append-only incremental merge logic
│   └── correction_handler.md    #   Correction handling
├── tools/                        # Python utilities
│   ├── wechat_parser.py          #   WeChat chat log parser
│   ├── qq_parser.py              #   QQ chat log parser (txt/mht)
│   ├── audio_transcriber.py      #   Audio transcription (Whisper)
│   ├── photo_analyzer.py         #   Photo EXIF timeline extractor
│   ├── interview_guide.py        #   Interview question generator (self + family modes)
│   ├── skill_writer.py           #   Archive file management
│   └── version_manager.py        #   Version backup and rollback
├── memorials/                    # Generated memorial archives (gitignored)
│   └── example_grandpa/          #   Complete example (fictional grandpa Wang Jianguo)
├── spec/                         # Design spec and test cases
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## Two Ways to Build

| | Build while they're alive | Build after they've passed |
|---|---|---|
| **Data quality** | Highest — firsthand, in their own words | Depends on memory and preserved materials |
| **Accuracy** | Real-time corrections, self-verified | Can't be corrected; needs family cross-checking |
| **Emotional context** | Warm, proactive, feels like leaving a legacy | Tinged with longing, like assembling a puzzle |
| **Best time to start** | When parents or grandparents are getting older | Anytime, as long as materials and memories exist |
| **Subject involvement** | Core data source | N/A |

> If they're still here, now is the best time.

---

## Notes

- **Source quality determines archive depth**: chat logs + family interviews > personal description alone
- Priority materials: **everyday conversations** (best for language patterns) > **pivotal exchanges** > **one-sided descriptions**
- Family interviews are a unique and important source for memorial-skill — use `/{slug}-interview` to generate tailored questions
- Archives can be built up over time. Memories surface gradually; add them as they come
- This Skill is not a substitute for grief. If you find yourself struggling to move forward, please consider professional support

---

<div align="center">

*What they left behind isn't just photos and chat logs.*<br>
*It's a way of speaking. A habit. A phrase that always appeared at the right moment.*<br>
*This archive just gives those things somewhere that won't disappear.*

</div>
