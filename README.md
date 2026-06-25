# Caption Automation (editable, ala Filmora/CapCut)

Auto-caption buat video — **editable**, highlight per-kata, bisa batch banyak video.
Beda dari pendekatan render PNG: teks tetap berupa **teks** (`.ass`) sampai langkah
terakhir, jadi kalau Whisper salah dengar / salah translate, tinggal dibenerin —
nggak usah render ulang dari nol. Kata kunci juga selalu kebaca (outline + shadow tebal).

## Alur kerja

```
video.mp4  ──transcribe──▶  video.ass  ──(edit kalau perlu)──▶  burn  ──▶  video.captioned.mp4
                            (teks editable)     Aegisub             ffmpeg
```

1. **transcribe** — bikin subtitle `.ass` dari audio (Whisper, timing per-kata).
2. **edit** *(opsional)* — buka `.ass` di [Aegisub](https://aegisub.org) kalau ada teks salah,
   atau ganti warna/template. File `.ass` itu teks biasa, bisa dibuka di editor apa pun.
3. **burn** — bakar caption ke video di langkah terakhir aja.

## Setup (di Mac, sekali aja)

```bash
brew install ffmpeg                 # buat ekstrak audio + burn
pip install -r requirements.txt     # faster-whisper
```

## Pakai

**Satu video, langsung jadi (transcribe + burn sekaligus):**
```bash
python caption.py transcribe video.mp4 --template hormozi --burn
```

**Batch satu folder (transcribe dulu, edit, baru burn) — alur yang disaranin:**
```bash
python caption.py transcribe ./videos --template classic   # bikin .ass semua video
# ... benerin teks yang salah di Aegisub kalau perlu ...
python caption.py burn videos/clip1.mp4 videos/clip1.ass    # burn per video
```

## Template

| Template  | Gaya                                        |
|-----------|---------------------------------------------|
| `classic` | Putih → kuning, di bawah-tengah             |
| `hormozi` | Gede, di tengah layar, kuning (gaya reels)  |
| `tiktok`  | Putih → cyan/hijau, di bawah                |

Mau warna/font sendiri? Edit dict `TEMPLATES` di `caption.py` (warna format `&HAABBGGRR`).

## Opsi penting

| Opsi           | Fungsi                                                            |
|----------------|------------------------------------------------------------------|
| `--model`      | `tiny`/`base`/`small`/`medium`/`large-v3`. Makin gede makin akurat tapi lambat. Default `small`. |
| `--lang`       | Paksa bahasa, mis. `--lang id` atau `--lang en`. Default: auto-deteksi. |
| `--template`   | Pilih gaya (lihat tabel di atas).                                |
| `--max-words`  | Maks kata per baris (default 4). Kecilin buat gaya 1–2 kata.     |
| `--burn`       | Langsung burn setelah transcribe (skip langkah edit).            |

## Tips akurasi

- Bahasa Indonesia campur Inggris sering lebih bagus pakai `--model medium` ke atas.
- Kalau hasil deteksi bahasa ngaco, paksa pakai `--lang id`.
- Edit teks di Aegisub: timing karaoke (`\kf`) tetap, lo cukup ganti tulisan katanya.
