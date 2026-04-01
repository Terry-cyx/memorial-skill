#!/usr/bin/env python3
"""
voice_synthesizer.py — 语音合成工具（Phase 3）

输入文字 → 输出亲人声音的音频。

支持两种模式：
  1. GPT-SoVITS 推理（需要已训练的模型，效果最好）
  2. CosyVoice 零样本（无需训练，提供参考音频即可，Phase 4 备选）

用法：
  # 使用 GPT-SoVITS 模型合成
  python voice_synthesizer.py --slug grandpa_wang --text "吃亏是福" --output output.wav

  # 使用 CosyVoice 零样本
  python voice_synthesizer.py --slug grandpa_wang --text "吃亏是福" --engine cosyvoice --ref-audio ref.wav

  # 批量合成（从文本文件读取，每行一句）
  python voice_synthesizer.py --slug grandpa_wang --text-file sentences.txt --outdir ./audio_out/

  # 查看可用引擎和模型
  python voice_synthesizer.py --slug grandpa_wang --action check
"""

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
MEMORIALS_DIR = os.path.join(PROJECT_ROOT, "memorials")

DEFAULT_SOVITS_DIR = os.path.join(PROJECT_ROOT, "GPT-SoVITS")


def voice_dir(slug: str) -> str:
    return os.path.join(MEMORIALS_DIR, slug, "voice")


# ── 引擎检测 ──────────────────────────────────────────────────────────────────

def check_engines(slug: str) -> dict:
    """检查可用的合成引擎和模型。"""
    status = {
        "gpt_sovits": {"available": False, "model_ready": False, "detail": ""},
        "cosyvoice": {"available": False, "detail": ""},
    }

    # GPT-SoVITS
    sovits_dir = os.environ.get("GPT_SOVITS_DIR", DEFAULT_SOVITS_DIR)
    if os.path.isdir(sovits_dir):
        status["gpt_sovits"]["available"] = True
        status["gpt_sovits"]["detail"] = sovits_dir

        model_dir = os.path.join(voice_dir(slug), "gpt_sovits")
        if os.path.isdir(model_dir):
            pth_files = [f for f in os.listdir(model_dir) if f.endswith(".pth")]
            if pth_files:
                status["gpt_sovits"]["model_ready"] = True
                status["gpt_sovits"]["models"] = pth_files

    # CosyVoice
    try:
        import importlib
        importlib.import_module("cosyvoice")
        status["cosyvoice"]["available"] = True
        status["cosyvoice"]["detail"] = "已安装"
    except ImportError:
        status["cosyvoice"]["detail"] = "未安装（pip install cosyvoice）"

    return status


# ── GPT-SoVITS 合成 ──────────────────────────────────────────────────────────

def synthesize_sovits(
    text: str,
    slug: str,
    ref_audio: str = "",
    ref_text: str = "",
    output_path: str = "output.wav",
) -> bool:
    """
    调用 GPT-SoVITS 进行语音合成。

    GPT-SoVITS 通常通过 API 服务运行：
    1. 启动 API 服务：cd GPT-SoVITS && python api.py
    2. 本工具通过 HTTP 调用 API
    """
    import urllib.request
    import urllib.parse

    # GPT-SoVITS API 默认端口
    api_base = os.environ.get("GPT_SOVITS_API", "http://127.0.0.1:9880")

    # 构建请求参数
    params = {
        "text": text,
        "text_language": "zh",
    }
    if ref_audio:
        params["refer_wav_path"] = ref_audio
    if ref_text:
        params["prompt_text"] = ref_text
        params["prompt_language"] = "zh"

    try:
        url = f"{api_base}/?" + urllib.parse.urlencode(params)
        print(f"[合成] 请求 GPT-SoVITS API ...")

        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=60) as resp:
            if resp.status == 200:
                audio_data = resp.read()
                with open(output_path, "wb") as f:
                    f.write(audio_data)
                print(f"[完成] {output_path}")
                return True
            else:
                print(f"[错误] API 返回 {resp.status}")
                return False

    except urllib.error.URLError as e:
        print(f"[错误] 无法连接 GPT-SoVITS API ({api_base})")
        print(f"  请确保已启动 API 服务：")
        sovits_dir = os.environ.get("GPT_SOVITS_DIR", DEFAULT_SOVITS_DIR)
        print(f"  cd {sovits_dir} && python api.py")
        return False
    except Exception as e:
        print(f"[错误] 合成失败：{e}")
        return False


# ── CosyVoice 合成 ───────────────────────────────────────────────────────────

def synthesize_cosyvoice(
    text: str,
    ref_audio: str,
    output_path: str = "output.wav",
) -> bool:
    """
    调用 CosyVoice 进行零样本合成。
    只需要一段参考音频（3-30秒），无需训练。
    """
    try:
        from cosyvoice.cli.cosyvoice import CosyVoice
        import torchaudio

        print("[加载] CosyVoice 模型 ...")
        cosyvoice = CosyVoice("pretrained_models/CosyVoice-300M")

        print(f"[合成] 零样本模式，参考音频：{ref_audio}")
        output = cosyvoice.inference_zero_shot(
            tts_text=text,
            prompt_text="",
            prompt_speech_16k=ref_audio,
        )

        # 保存输出
        for result in output:
            torchaudio.save(output_path, result["tts_speech"], 22050)
            print(f"[完成] {output_path}")
            return True

    except ImportError:
        print("[错误] 未安装 CosyVoice")
        print("  安装说明：https://github.com/FunAudioLLM/CosyVoice")
        return False
    except Exception as e:
        print(f"[错误] CosyVoice 合成失败：{e}")
        return False


# ── 批量合成 ──────────────────────────────────────────────────────────────────

def synthesize_batch(
    text_file: str,
    slug: str,
    outdir: str,
    engine: str = "sovits",
    ref_audio: str = "",
) -> dict:
    """从文本文件批量合成，每行一句。"""
    os.makedirs(outdir, exist_ok=True)

    with open(text_file, encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    if not lines:
        print("[错误] 文本文件为空")
        return {"total": 0, "success": 0, "failed": 0}

    print(f"[批量] {len(lines)} 句文本待合成")

    stats = {"total": len(lines), "success": 0, "failed": 0}

    for i, text in enumerate(lines, 1):
        out_path = os.path.join(outdir, f"{i:03d}.wav")
        print(f"[{i}/{len(lines)}] {text[:30]}{'...' if len(text) > 30 else ''}")

        if engine == "cosyvoice":
            ok = synthesize_cosyvoice(text, ref_audio, out_path)
        else:
            ok = synthesize_sovits(text, slug, ref_audio=ref_audio, output_path=out_path)

        if ok:
            stats["success"] += 1
        else:
            stats["failed"] += 1

    return stats


# ── 自动选择参考音频 ──────────────────────────────────────────────────────────

def find_ref_audio(slug: str) -> str:
    """从训练数据中自动选择一段参考音频（时长 5-15秒的优先）。"""
    tdir = os.path.join(voice_dir(slug), "training_data", "wavs")
    if not os.path.isdir(tdir):
        return ""

    try:
        import soundfile as sf
        best = None
        best_score = float("inf")

        for f in os.listdir(tdir):
            if not f.endswith(".wav"):
                continue
            path = os.path.join(tdir, f)
            info = sf.info(path)
            dur = info.duration
            # 理想参考音频 5-15 秒
            score = abs(dur - 10)
            if 3 <= dur <= 20 and score < best_score:
                best = path
                best_score = score

        return best or ""
    except Exception:
        return ""


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="语音合成工具 — 输入文字，输出亲人声音",
    )
    parser.add_argument("--slug", required=True, help="纪念档案 slug")
    parser.add_argument("--action", default="synthesize",
                        choices=["synthesize", "check"],
                        help="操作：synthesize=合成（默认），check=检查环境")

    parser.add_argument("--text", help="要合成的文字")
    parser.add_argument("--text-file", help="批量合成：每行一句的文本文件")
    parser.add_argument("--output", default="output.wav", help="输出音频路径")
    parser.add_argument("--outdir", default="./audio_out", help="批量输出目录")

    parser.add_argument("--engine", default="sovits",
                        choices=["sovits", "cosyvoice"],
                        help="合成引擎：sovits（默认）或 cosyvoice")
    parser.add_argument("--ref-audio", help="参考音频路径（影响语气，cosyvoice 必填）")

    args = parser.parse_args()

    if args.action == "check":
        status = check_engines(args.slug)
        print(f"=== {args.slug} 语音合成环境 ===\n")

        s = status["gpt_sovits"]
        print(f"GPT-SoVITS：{'✅ 已安装' if s['available'] else '❌ 未安装'}")
        if s["available"]:
            print(f"  路径：{s['detail']}")
            print(f"  模型：{'✅ 已训练 — ' + ', '.join(s.get('models', [])) if s['model_ready'] else '❌ 未训练'}")

        c = status["cosyvoice"]
        print(f"\nCosyVoice：{'✅' if c['available'] else '❌'} {c['detail']}")

        ref = find_ref_audio(args.slug)
        if ref:
            print(f"\n自动选择的参考音频：{ref}")
        return

    # 合成模式
    if not args.text and not args.text_file:
        parser.error("需要 --text 或 --text-file")

    ref_audio = args.ref_audio or find_ref_audio(args.slug)

    if args.text_file:
        stats = synthesize_batch(
            args.text_file, args.slug, args.outdir,
            engine=args.engine, ref_audio=ref_audio,
        )
        print(f"\n[汇总] 成功 {stats['success']}/{stats['total']}")
    else:
        if args.engine == "cosyvoice":
            if not ref_audio:
                parser.error("CosyVoice 模式需要 --ref-audio 参考音频")
            synthesize_cosyvoice(args.text, ref_audio, args.output)
        else:
            synthesize_sovits(args.text, args.slug,
                              ref_audio=ref_audio, output_path=args.output)


if __name__ == "__main__":
    main()
