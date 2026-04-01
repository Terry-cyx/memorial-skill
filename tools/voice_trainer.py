#!/usr/bin/env python3
"""
voice_trainer.py — 声音模型训练工具（Phase 2）

封装 GPT-SoVITS 的训练流程：预处理音频 → 切片 → 标注 → SoVITS 微调 → GPT 微调。

前置条件：
  1. 已安装 GPT-SoVITS（见 setup 命令）
  2. 已通过 voice_preprocessor.py 生成干净 WAV 文件
  3. RTX 4080S / 3060 或更高显卡

用法：
  # 第一步：安装 GPT-SoVITS 环境
  python voice_trainer.py --action setup

  # 第二步：准备训练数据（切片 + 标注）
  python voice_trainer.py --action prepare --slug grandpa_wang --audio-dir ./processed/

  # 第三步：训练模型
  python voice_trainer.py --action train --slug grandpa_wang

  # 查看训练状态
  python voice_trainer.py --action status --slug grandpa_wang
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
MEMORIALS_DIR = os.path.join(PROJECT_ROOT, "memorials")

# GPT-SoVITS 默认安装位置
DEFAULT_SOVITS_DIR = os.path.join(PROJECT_ROOT, "GPT-SoVITS")


def get_sovits_dir() -> str:
    """查找 GPT-SoVITS 安装路径。"""
    # 优先环境变量
    env_dir = os.environ.get("GPT_SOVITS_DIR")
    if env_dir and os.path.isdir(env_dir):
        return env_dir
    # 默认路径
    if os.path.isdir(DEFAULT_SOVITS_DIR):
        return DEFAULT_SOVITS_DIR
    return ""


def voice_dir(slug: str) -> str:
    return os.path.join(MEMORIALS_DIR, slug, "voice")


def training_dir(slug: str) -> str:
    return os.path.join(voice_dir(slug), "training_data")


# ── Setup ─────────────────────────────────────────────────────────────────────

def action_setup():
    """下载并安装 GPT-SoVITS。"""
    if get_sovits_dir():
        print(f"[已安装] GPT-SoVITS 位于：{get_sovits_dir()}")
        return

    print("=" * 60)
    print("GPT-SoVITS 安装指引")
    print("=" * 60)
    print()
    print("GPT-SoVITS 需要独立安装，有以下两种方式：")
    print()
    print("方式一：整合包（推荐 Windows 用户）")
    print("  1. 访问 https://github.com/RVC-Boss/GPT-SoVITS/releases")
    print("  2. 下载最新的整合包（.7z 或 .zip）")
    print(f"  3. 解压到 {DEFAULT_SOVITS_DIR}")
    print()
    print("方式二：从源码安装")
    print(f"  git clone https://github.com/RVC-Boss/GPT-SoVITS.git {DEFAULT_SOVITS_DIR}")
    print(f"  cd {DEFAULT_SOVITS_DIR}")
    print("  pip install -r requirements.txt")
    print()
    print("方式三：指定已有安装路径")
    print("  设置环境变量 GPT_SOVITS_DIR 指向你的 GPT-SoVITS 目录")
    print()

    # 尝试自动 clone
    print("-" * 60)
    answer = input("是否自动从 GitHub 克隆？(y/n) ").strip().lower()
    if answer == "y":
        print(f"\n[下载] 正在克隆到 {DEFAULT_SOVITS_DIR} ...")
        result = subprocess.run(
            ["git", "clone", "--depth", "1",
             "https://github.com/RVC-Boss/GPT-SoVITS.git",
             DEFAULT_SOVITS_DIR],
            capture_output=False,
        )
        if result.returncode == 0:
            print("[完成] 克隆成功")
            print(f"[下一步] cd {DEFAULT_SOVITS_DIR} && pip install -r requirements.txt")
        else:
            print("[失败] 克隆失败，请手动下载")


# ── Prepare ───────────────────────────────────────────────────────────────────

def action_prepare(slug: str, audio_dir: str):
    """准备训练数据：收集 WAV → 切片 → Whisper 标注。"""
    vdir = voice_dir(slug)
    tdir = training_dir(slug)
    os.makedirs(tdir, exist_ok=True)
    os.makedirs(os.path.join(tdir, "wavs"), exist_ok=True)

    # 收集所有 WAV 文件到训练目录
    wavs = sorted([
        f for f in os.listdir(audio_dir)
        if f.lower().endswith(".wav")
    ])

    if not wavs:
        print(f"[错误] {audio_dir} 中没有 WAV 文件")
        print("请先运行 voice_preprocessor.py 处理原始音频")
        return

    print(f"[收集] {len(wavs)} 个 WAV 文件")

    total_dur = 0
    manifest = []

    for wav in wavs:
        src = os.path.join(audio_dir, wav)
        dst = os.path.join(tdir, "wavs", wav)
        shutil.copy2(src, dst)

        # 获取时长
        try:
            import soundfile as sf
            info = sf.info(src)
            dur = info.duration
        except Exception:
            dur = 0

        total_dur += dur
        manifest.append({"file": wav, "duration": round(dur, 2)})

    # 保存数据清单
    manifest_path = os.path.join(tdir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "slug": slug,
            "total_files": len(wavs),
            "total_duration_seconds": round(total_dur, 1),
            "files": manifest,
        }, f, ensure_ascii=False, indent=2)

    # Whisper 标注（如果已安装）
    annotation_path = os.path.join(tdir, "annotations.list")
    try:
        import whisper
        print(f"[标注] 正在用 Whisper 生成文字标注 ...")
        model = whisper.load_model("small")
        annotations = []
        for wav in wavs:
            wav_path = os.path.join(tdir, "wavs", wav)
            result = model.transcribe(wav_path, language="zh", verbose=False)
            text = result["text"].strip()
            lang = result.get("language", "zh")
            # GPT-SoVITS 标注格式：wav路径|说话人|语言|文本
            annotations.append(f"{wav_path}|{slug}|{lang}|{text}")
            print(f"  {wav}: {text[:50]}{'...' if len(text) > 50 else ''}")

        with open(annotation_path, "w", encoding="utf-8") as f:
            f.write("\n".join(annotations))
        print(f"[标注] 已保存到 {annotation_path}")

    except ImportError:
        print("[警告] 未安装 whisper，跳过自动标注")
        print("  请手动创建标注文件，或安装：pip install openai-whisper")

    # 训练建议
    print()
    print(f"[汇总] 训练数据准备完毕")
    print(f"  文件数：{len(wavs)}")
    print(f"  总时长：{total_dur:.1f}秒 ({total_dur/60:.1f}分钟)")
    print(f"  数据目录：{tdir}")
    print()
    if total_dur < 30:
        print("  ⚠️ 音频不足 30 秒，建议使用 CosyVoice 零样本模式")
    elif total_dur < 180:
        print("  ℹ️ 音频 < 3 分钟，可尝试 GPT-SoVITS few-shot，效果有限")
    else:
        print("  ✅ 音频充足，适合 GPT-SoVITS 微调训练")
        print()
        print("  [下一步] python voice_trainer.py --action train --slug " + slug)


# ── Train ─────────────────────────────────────────────────────────────────────

def action_train(slug: str):
    """调用 GPT-SoVITS 进行微调训练。"""
    sovits_dir = get_sovits_dir()
    if not sovits_dir:
        print("[错误] 未找到 GPT-SoVITS，请先运行：python voice_trainer.py --action setup")
        return

    tdir = training_dir(slug)
    if not os.path.isdir(tdir):
        print(f"[错误] 训练数据不存在：{tdir}")
        print("请先运行：python voice_trainer.py --action prepare --slug " + slug)
        return

    annotation_path = os.path.join(tdir, "annotations.list")
    if not os.path.exists(annotation_path):
        print(f"[错误] 标注文件不存在：{annotation_path}")
        print("请确保 prepare 步骤已完成 Whisper 标注")
        return

    vdir = voice_dir(slug)
    model_dir = os.path.join(vdir, "gpt_sovits")
    os.makedirs(model_dir, exist_ok=True)

    print("=" * 60)
    print(f"GPT-SoVITS 微调训练 — {slug}")
    print("=" * 60)
    print()
    print(f"  GPT-SoVITS 路径：{sovits_dir}")
    print(f"  训练数据：{tdir}")
    print(f"  模型输出：{model_dir}")
    print()

    # GPT-SoVITS 训练通常通过其 WebUI 或内置脚本完成
    # 这里生成训练配置并提供命令指引
    config = {
        "experiment_name": slug,
        "training_data_dir": os.path.join(tdir, "wavs"),
        "annotation_file": annotation_path,
        "output_dir": model_dir,
        "sovits_dir": sovits_dir,
    }

    config_path = os.path.join(model_dir, "train_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("训练配置已生成。GPT-SoVITS 提供两种训练方式：")
    print()
    print("方式一：WebUI（推荐，可视化操作）")
    print(f"  1. cd {sovits_dir}")
    print(f"  2. python webui.py")
    print(f"  3. 在浏览器中打开 WebUI")
    print(f"  4. 在「训练」页面，选择训练数据目录：{os.path.join(tdir, 'wavs')}")
    print(f"  5. 加载标注文件：{annotation_path}")
    print(f"  6. 开始 SoVITS 微调 → 再 GPT 微调")
    print(f"  7. 训练完成后，将模型文件复制到：{model_dir}")
    print()
    print("方式二：命令行")
    print(f"  详见 GPT-SoVITS 文档中的 CLI 训练说明")
    print(f"  训练配置已保存到：{config_path}")
    print()
    print("训练参数建议（RTX 4080S 16GB）：")
    print("  SoVITS 微调：batch_size=16, epochs=8-12")
    print("  GPT 微调：batch_size=8, epochs=15-20")
    print("  预计耗时：10-25 分钟（取决于音频量）")


# ── Status ────────────────────────────────────────────────────────────────────

def action_status(slug: str):
    """查看训练数据和模型状态。"""
    vdir = voice_dir(slug)
    tdir = training_dir(slug)
    model_dir = os.path.join(vdir, "gpt_sovits")

    print(f"=== {slug} 声音模型状态 ===\n")

    # 训练数据
    if os.path.isdir(tdir):
        manifest_path = os.path.join(tdir, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
            print(f"训练数据：✅ 已准备")
            print(f"  文件数：{manifest['total_files']}")
            print(f"  总时长：{manifest['total_duration_seconds']}秒")
        else:
            print("训练数据：⚠️ 目录存在但缺少 manifest")

        annotation_path = os.path.join(tdir, "annotations.list")
        if os.path.exists(annotation_path):
            with open(annotation_path, encoding="utf-8") as f:
                n_lines = len(f.readlines())
            print(f"  标注：✅ {n_lines} 条")
        else:
            print("  标注：❌ 未完成")
    else:
        print("训练数据：❌ 未准备")
        print(f"  请运行：python voice_trainer.py --action prepare --slug {slug}")

    # 模型文件
    print()
    if os.path.isdir(model_dir):
        pth_files = [f for f in os.listdir(model_dir) if f.endswith(".pth")]
        if pth_files:
            print(f"训练模型：✅ 已完成")
            for f in pth_files:
                size_mb = os.path.getsize(os.path.join(model_dir, f)) / 1024 / 1024
                print(f"  {f} ({size_mb:.1f}MB)")
        else:
            print("训练模型：⏳ 目录已创建，模型待训练")
    else:
        print("训练模型：❌ 未开始")

    # GPT-SoVITS 安装
    print()
    sovits_dir = get_sovits_dir()
    if sovits_dir:
        print(f"GPT-SoVITS：✅ {sovits_dir}")
    else:
        print("GPT-SoVITS：❌ 未安装")
        print(f"  请运行：python voice_trainer.py --action setup")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="声音模型训练工具（GPT-SoVITS）")
    parser.add_argument("--action", required=True,
                        choices=["setup", "prepare", "train", "status"],
                        help="操作：setup=安装, prepare=准备数据, train=训练, status=查看状态")
    parser.add_argument("--slug", help="纪念档案 slug")
    parser.add_argument("--audio-dir", help="预处理后的 WAV 文件目录（prepare 时用）")

    args = parser.parse_args()

    if args.action == "setup":
        action_setup()
    elif args.action == "prepare":
        if not args.slug or not args.audio_dir:
            parser.error("--action prepare 需要 --slug 和 --audio-dir")
        action_prepare(args.slug, args.audio_dir)
    elif args.action == "train":
        if not args.slug:
            parser.error("--action train 需要 --slug")
        action_train(args.slug)
    elif args.action == "status":
        if not args.slug:
            parser.error("--action status 需要 --slug")
        action_status(args.slug)


if __name__ == "__main__":
    main()
