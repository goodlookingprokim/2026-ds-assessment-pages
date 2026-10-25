#!/usr/bin/env python3
"""Edit genuine Orange window captures with matching GoodlookingproKim audio."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
MEDIA = ROOT.parent
SCENES = [
    ("02", "02-canvas-branch.png"),
    ("03", "03-table.png"),
    ("04", "04-scatter-participation-performance.png"),
]
# Sentence boundaries checked against a local transcription of the finished audio.
# Values are relative to the start of each scene; the last value is the clip end.
SCENE_CUE_BOUNDARIES = {
    "02": [0, 6.3, 9.8, 13.0, 20.5, 24.8, 27.2],
    "03": [0, 3.4, 6.1, 12.0, 15.7, 18.8],
    "04": [0, 3.2, 8.8, 10.9, 19.4, 23.2, 29.44],
}
BRANCH_STAGES = [
    ("02a-canvas-unconnected.png", 6.3),
    ("02b-canvas-one-link.png", 3.5),
    ("02-canvas-branch.png", 17.4),
]
PROFILE = "4414558b-b6d6-48af-a810-b60c991040a0"


def duration(path: Path) -> float:
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ], text=True))


def timestamp(seconds: float) -> str:
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02}.{ms % 1000:03}"


def main() -> None:
    segments = []
    cues = []
    evidence = []
    offset = 0.0
    for number, picture in SCENES:
        image = ROOT / picture
        audio = ROOT / f"voice_{number}.wav"
        meta = json.loads((ROOT / f"voice_{number}.json").read_text(encoding="utf-8"))
        if meta["profile_id"] != PROFILE or meta["profile_name"] != "GoodlookingproKim":
            raise ValueError(f"Unexpected voice profile for scene {number}")
        if meta["status"] != "completed" or not image.is_file() or not audio.is_file():
            raise ValueError(f"Incomplete scene {number}")
        seconds = duration(audio)
        segment = ROOT / f"segment_{number}.mp4"
        image_input = ["-loop", "1", "-framerate", "15", "-i", str(image)]
        if number == "02":
            if abs(sum(stage_seconds for _, stage_seconds in BRANCH_STAGES) - seconds) > 0.05:
                raise ValueError("The connection stages do not match the narration")
            frames = ROOT / "branch-stages.ffconcat"
            frames.write_text("ffconcat version 1.0\n" + "".join(
                f"file '{picture}'\nduration {stage_seconds}\n"
                for picture, stage_seconds in BRANCH_STAGES
            ) + f"file '{BRANCH_STAGES[-1][0]}'\n", encoding="utf-8")
            image_input = ["-f", "concat", "-safe", "0", "-i", str(frames)]
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", *image_input, "-i", str(audio),
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x152025,setsar=1",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-r", "15",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
            "-t", str(seconds), "-movflags", "+faststart", str(segment),
        ], check=True)
        if number == "02":
            frames.unlink()
        segments.append(segment)

        # These are the sentences submitted to Voicebox, not descriptions of the images.
        sentences = [part.strip() + "." for part in re.split(r"\.(?:\s+|$)", meta["text"]) if part.strip()]
        boundaries = SCENE_CUE_BOUNDARIES[number]
        if len(boundaries) != len(sentences) + 1 or abs(boundaries[-1] - seconds) > 0.05:
            raise ValueError(f"Narration timing needs review for scene {number}")
        for sentence, start, end in zip(sentences, boundaries, boundaries[1:]):
            cues.append(f"{timestamp(offset + start)} --> {timestamp(offset + end)}\n{sentence}\n")
        evidence.append({
            "scene": number,
            "capture": picture,
            "capture_sha256": sha256(image.read_bytes()).hexdigest(),
            "audio_sha256": sha256(audio.read_bytes()).hexdigest(),
            "voice_profile": meta["profile_name"],
            "spoken_text": meta["text"],
            "duration_seconds": seconds,
            **({"connection_stages": [{"capture": stage,
                "capture_sha256": sha256((ROOT / stage).read_bytes()).hexdigest(),
                "duration_seconds": stage_seconds} for stage, stage_seconds in BRANCH_STAGES]}
                if number == "02" else {}),
        })
        offset += seconds

    listing = ROOT / "segments.ffconcat"
    listing.write_text("".join(f"file '{segment.name}'\n" for segment in segments), encoding="utf-8")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
        "-c", "copy", "-movflags", "+faststart", str(MEDIA / "manual-recaptured.mp4"),
    ], check=True)
    listing.unlink()
    for segment in segments:
        segment.unlink()
    (MEDIA / "subtitles-recaptured.vtt").write_text("WEBVTT\n\n" + "\n".join(cues), encoding="utf-8")
    (ROOT / "evidence.json").write_text(json.dumps({
        "source": "Orange 안정화.app actual window captures of the current 11-column CSV",
        "voice_profile_id": PROFILE,
        "voicebox_generation": "Existing completed clips; fresh generation failed with missing default metallib",
        "subtitle_basis": "Exact Voicebox text for each reused clip; sentence timing checked against local audio transcription",
        "scenes": evidence,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {MEDIA / 'manual-recaptured.mp4'} ({offset:.2f} seconds)")


if __name__ == "__main__":
    main()
