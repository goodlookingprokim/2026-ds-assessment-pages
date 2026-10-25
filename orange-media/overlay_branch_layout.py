#!/usr/bin/env python3
"""Show the recommended two-branch layout during the original connection demo."""

from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent

subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-i", str(HERE / "manual-student.mp4"),
    "-loop", "1", "-i", str(HERE / "file-two-branches.png"),
    "-filter_complex", "[0:v][1:v]overlay=1180:300:enable='between(t,65,83)':shortest=1[v]",
    "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "22",
    "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "copy",
    "-movflags", "+faststart", str(HERE / "manual-branch-layout.mp4"),
], check=True)
