#!/usr/bin/env python3
"""
caption.py — Automation caption editable (gaya auto-caption Filmora/CapCut).

Alur:
  1. transcribe : video -> .ass (subtitle editable, highlight per-kata karaoke)
  2. (opsional)  : edit .ass di Aegisub kalau Whisper salah dengar / salah translate
  3. burn        : video + .ass -> video final (teks dibakar di langkah TERAKHIR saja)

Kenapa .ass, bukan render PNG:
  - Teks tetap berupa teks sampai detik terakhir -> gampang dibenerin.
  - Outline + shadow tebal -> kata kunci selalu kebaca (nggak item lagi).
  - Highlight per-kata + template -> mirip Filmora, tapi otomatis & batch.

Butuh (di Mac): ffmpeg (brew install ffmpeg) + pip install -r requirements.txt
"""

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass

VIDEO_EXTS = (".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi")

# ---------------------------------------------------------------------------
# Template gaya caption. Warna ASS = &HAABBGGRR (AA=alpha, 00=solid).
#   base      : warna kata SEBELUM diucapkan (SecondaryColour)
#   highlight : warna kata SAAT/SETELAH diucapkan (PrimaryColour) -> efek nyala
#   outline   : garis tepi (bikin teks kebaca di background apa pun)
#   size_frac : ukuran font sebagai fraksi tinggi video (resolution-independent)
#   align     : 2=bawah-tengah, 5=tengah, 8=atas-tengah
# ---------------------------------------------------------------------------
TEMPLATES = {
    "classic": {
        "font": "Arial", "bold": 1, "size_frac": 0.045,
        "base": "&H00FFFFFF", "highlight": "&H0000FFFF",   # putih -> kuning
        "outline_col": "&H00000000", "outline": 4, "shadow": 2,
        "align": 2, "margin_frac": 0.10,
    },
    "hormozi": {
        "font": "Arial Black", "bold": 1, "size_frac": 0.055,
        "base": "&H00FFFFFF", "highlight": "&H0000FFFF",   # putih -> kuning, gede di tengah
        "outline_col": "&H00000000", "outline": 6, "shadow": 3,
        "align": 5, "margin_frac": 0.0,
    },
    "tiktok": {
        "font": "Arial", "bold": 1, "size_frac": 0.045,
        "base": "&H00FFFFFF", "highlight": "&H00EAF200",   # putih -> cyan/hijau
        "outline_col": "&H00000000", "outline": 4, "shadow": 2,
        "align": 2, "margin_frac": 0.12,
    },
}


@dataclass
class Word:
    start: float
    end: float
    text: str


# ---------------------------------------------------------------------------
# ffmpeg / ffprobe helpers
# ---------------------------------------------------------------------------
def _require(cmd):
    from shutil import which
    if which(cmd) is None:
        sys.exit(f"[error] '{cmd}' nggak ketemu. Di Mac: brew install ffmpeg")


def probe_resolution(video, default=(1080, 1920)):
    """Ambil ukuran video biar font & margin pas dalam piksel."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", video],
            capture_output=True, text=True, check=True).stdout.strip()
        w, h = out.split("x")
        return int(w), int(h)
    except Exception:
        return default


def extract_audio(video, wav_path):
    subprocess.run(
        ["ffmpeg", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav_path],
        check=True, capture_output=True)


# ---------------------------------------------------------------------------
# Transkripsi -> daftar Word
# ---------------------------------------------------------------------------
def transcribe(video, model_name="small", lang=None):
    from faster_whisper import WhisperModel
    _require("ffmpeg")
    wav = video + ".tmp.wav"
    extract_audio(video, wav)
    try:
        model = WhisperModel(model_name, device="auto", compute_type="auto")
        segments, info = model.transcribe(wav, language=lang, word_timestamps=True)
        print(f"  bahasa terdeteksi: {info.language} (p={info.language_probability:.2f})")
        words = []
        for seg in segments:
            for w in (seg.words or []):
                txt = w.word.strip()
                if txt:
                    words.append(Word(w.start, w.end, txt))
        return words
    finally:
        if os.path.exists(wav):
            os.remove(wav)


# ---------------------------------------------------------------------------
# Word -> chunk (sekelompok kata per baris di layar)
# ---------------------------------------------------------------------------
def chunk_words(words, max_words=4, max_dur=2.5):
    chunks, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words
                    or (w.end - cur[0].start) > max_dur
                    or cur[-1].text[-1:] in ".!?,"):
            chunks.append(cur)
            cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


# ---------------------------------------------------------------------------
# Bangun file .ass
# ---------------------------------------------------------------------------
def _ass_escape(t):
    return t.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def _ts(seconds):
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs == 100:
        cs = 0
        s += 1
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass(chunks, width, height, template="classic"):
    if template not in TEMPLATES:
        sys.exit(f"[error] template '{template}' nggak ada. Pilihan: {', '.join(TEMPLATES)}")
    t = TEMPLATES[template]
    fontsize = max(12, round(height * t["size_frac"]))
    marginv = round(height * t["margin_frac"])

    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{t['font']},{fontsize},{t['highlight']},{t['base']},{t['outline_col']},&H64000000,{t['bold']},0,0,0,100,100,0,0,1,{t['outline']},{t['shadow']},{t['align']},40,40,{marginv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, Effect, Text
"""
    lines = []
    for chunk in chunks:
        start, end = chunk[0].start, chunk[-1].end
        parts = []
        for w in chunk:
            dur_cs = max(1, int(round((w.end - w.start) * 100)))
            parts.append(f"{{\\kf{dur_cs}}}{_ass_escape(w.text)} ")
        text = "".join(parts).rstrip()
        lines.append(f"Dialogue: 0,{_ts(start)},{_ts(end)},Default,,0,0,0,,{text}")
    return head + "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Burn .ass ke video (langkah TERAKHIR)
# ---------------------------------------------------------------------------
def burn(video, ass_path, out_path):
    _require("ffmpeg")
    safe = ass_path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    subprocess.run(
        ["ffmpeg", "-y", "-i", video, "-vf", f"ass='{safe}'",
         "-c:a", "copy", out_path],
        check=True)
    print(f"  -> {out_path}")


# ---------------------------------------------------------------------------
# Kumpulkan daftar video dari argumen (file atau folder)
# ---------------------------------------------------------------------------
def collect_videos(paths):
    vids = []
    for p in paths:
        if os.path.isdir(p):
            for name in sorted(os.listdir(p)):
                if name.lower().endswith(VIDEO_EXTS):
                    vids.append(os.path.join(p, name))
        elif p.lower().endswith(VIDEO_EXTS):
            vids.append(p)
        else:
            print(f"  [skip] bukan video: {p}")
    return vids


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def cmd_transcribe(args):
    vids = collect_videos(args.inputs)
    if not vids:
        sys.exit("[error] nggak ada video ditemukan.")
    for v in vids:
        print(f"[transcribe] {v}")
        words = transcribe(v, model_name=args.model, lang=args.lang)
        if not words:
            print("  [warn] nggak ada teks terdeteksi, dilewati.")
            continue
        chunks = chunk_words(words, max_words=args.max_words)
        w, h = probe_resolution(v)
        ass = build_ass(chunks, w, h, template=args.template)
        ass_path = os.path.splitext(v)[0] + ".ass"
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass)
        print(f"  -> {ass_path}  ({len(chunks)} baris, {w}x{h}, template={args.template})")
        if args.burn:
            out = os.path.splitext(v)[0] + ".captioned.mp4"
            burn(v, ass_path, out)


def cmd_burn(args):
    out = args.out or (os.path.splitext(args.video)[0] + ".captioned.mp4")
    print(f"[burn] {args.video} + {args.ass}")
    burn(args.video, args.ass, out)


def main():
    p = argparse.ArgumentParser(description="Automation caption editable (.ass) ala Filmora.")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("transcribe", help="video -> .ass (editable). Bisa folder buat batch.")
    t.add_argument("inputs", nargs="+", help="file video atau folder")
    t.add_argument("--model", default="small",
                   help="ukuran model whisper: tiny/base/small/medium/large-v3 (default: small)")
    t.add_argument("--lang", default=None, help="paksa bahasa, mis. id / en (default: auto)")
    t.add_argument("--template", default="classic",
                   choices=list(TEMPLATES), help="gaya caption (default: classic)")
    t.add_argument("--max-words", type=int, default=4, help="maks kata per baris (default: 4)")
    t.add_argument("--burn", action="store_true",
                   help="langsung burn ke video setelah transcribe (skip langkah edit)")
    t.set_defaults(func=cmd_transcribe)

    b = sub.add_parser("burn", help="video + .ass (yang sudah diedit) -> video final")
    b.add_argument("video")
    b.add_argument("ass")
    b.add_argument("-o", "--out", default=None, help="path output (default: <video>.captioned.mp4)")
    b.set_defaults(func=cmd_burn)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
