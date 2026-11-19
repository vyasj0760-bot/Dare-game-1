#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

ROOT = Path("video-workflow")
RAW = ROOT / "Raw-Footage"
REF = ROOT / "Reference"
OUT = ROOT / "Output"
STILLS = OUT / "reference-stills"
META = OUT / "metadata"
TRANSCRIPTS = OUT / "transcripts"
for folder in (STILLS, META, TRANSCRIPTS):
    folder.mkdir(parents=True, exist_ok=True)

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".aac", ".flac"}
MEDIA_EXTS = VIDEO_EXTS | AUDIO_EXTS

def run(cmd):
    return subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def probe(path):
    result = run([
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(path)
    ])
    data = json.loads(result.stdout)
    (META / (path.stem + ".json")).write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data

def extract_stills(path, label):
    data = probe(path)
    duration = float(data.get("format", {}).get("duration", 0) or 0)
    if duration <= 0:
        return
    # Three representative moments, not a substitute for watching the complete reference.
    for tag, fraction in (("early", 0.12), ("middle", 0.50), ("late", 0.88)):
        stamp = max(0, min(duration - 0.05, duration * fraction))
        target = STILLS / f"{label}_{path.stem}_{tag}.jpg"
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", str(stamp), "-i", str(path), "-frames:v", "1",
            "-vf", "scale=480:-2", str(target)
        ])

def transcribe(path):
    # Whisper auto-detects language; this is preferable for Hindi-English mixed speech.
    run([
        "whisper", str(path), "--model", "tiny",
        "--output_dir", str(TRANSCRIPTS), "--output_format", "txt",
        "--fp16", "False"
    ])

raw_files = sorted(p for p in RAW.rglob("*") if p.is_file() and p.suffix.lower() in MEDIA_EXTS)
ref_files = sorted(p for p in REF.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS)

if not raw_files and not ref_files:
    raise SystemExit("No media found. Upload clips to Raw-Footage and a reference video to Reference, then rerun.")

for path in raw_files:
    info = probe(path)
    if path.suffix.lower() in VIDEO_EXTS:
        extract_stills(path, "raw")
    if any(s.get("codec_type") == "audio" for s in info.get("streams", [])) or path.suffix.lower() in AUDIO_EXTS:
        transcribe(path)

for path in ref_files:
    extract_stills(path, "reference")

summary = {
    "raw_media": [str(p) for p in raw_files],
    "reference_videos": [str(p) for p in ref_files],
    "reference_stills": sorted(str(p) for p in STILLS.glob("*.jpg")),
    "transcripts": sorted(str(p) for p in TRANSCRIPTS.glob("*.txt")),
    "note": "Analysis pass only. Review full reference and footage before creating a final edit."
}
(OUT / "analysis-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
