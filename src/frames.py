#!/usr/bin/env python3
"""
视频抽帧工具 — Looki 的 files API 几乎全返 10 秒 mp4,必须抽帧才能让 Claude 多模态读图。

用法(命令行):
    python frames.py <video_url_or_path> <output.jpg> [--ss 3] [--quality 3]

作为库:
    from frames import extract_frame
    extract_frame(url, "out.jpg", ss_seconds=3, quality=3)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def find_ffmpeg() -> str:
    """找 ffmpeg 可执行路径,支持 winget 默认装的位置"""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    candidates = []
    if os.name == "nt":
        local = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
        if local.exists():
            for p in local.glob("Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe"):
                candidates.append(str(p))
    if candidates:
        return candidates[0]
    raise RuntimeError(
        "没找到 ffmpeg。请先装:\n"
        "  Windows: winget install Gyan.FFmpeg\n"
        "  Mac:    brew install ffmpeg\n"
        "  Linux:  apt install ffmpeg / yum install ffmpeg"
    )


def extract_frame(
    video_url: str,
    out_path: str,
    ss_seconds: float = 3.0,
    quality: int = 3,
) -> str:
    """
    从视频 URL(或本地路径)抽一帧,保存为 JPG。

    - video_url: Looki API 返回的 temporary_url(1 小时过期),或本地 mp4 路径
    - out_path: 输出 JPG 路径
    - ss_seconds: 从第几秒抽(默认 3,避开开头的跳动)
    - quality: 2 最好,5 够用,数字越大质量越差

    返回 out_path。
    """
    ffmpeg = find_ffmpeg()
    out_path = str(out_path)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-ss",
        str(ss_seconds),
        "-i",
        video_url,
        "-frames:v",
        "1",
        "-q:v",
        str(quality),
        out_path,
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore"
    )
    if result.returncode != 0 or not Path(out_path).exists():
        raise RuntimeError(
            f"ffmpeg 抽帧失败 (exit {result.returncode}):\n{result.stderr[:500]}"
        )
    return out_path


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    url = sys.argv[1]
    out = sys.argv[2]
    ss = 3.0
    q = 3
    if "--ss" in sys.argv:
        ss = float(sys.argv[sys.argv.index("--ss") + 1])
    if "--quality" in sys.argv:
        q = int(sys.argv[sys.argv.index("--quality") + 1])
    result = extract_frame(url, out, ss_seconds=ss, quality=q)
    size = Path(result).stat().st_size
    print(f"抽帧成功: {result} ({size} bytes)")


if __name__ == "__main__":
    main()
