# Workflow Produksi Video — Higgsfield → Edit → Caption

Panduan alur produksi video pendek (reels/shorts) dari nol sampai jadi.
Prinsip utama: **caption itu langkah TERAKHIR**, nempel ke final cut yang udah dikunci.

```
Skrip  →  Higgsfield (visual+audio)  →  Jahit final cut  →  caption.py  →  Upload
(gratis)     (makan kredit)            (editor, manual)     (terakhir)
```

---

## Prinsip hemat kredit (penting — plan Free/kredit tipis)

1. **Generate murah dulu, mahal belakangan.** Bikin GAMBAR diam dulu (`generate_image`,
   relatif murah) → pilih yang bagus → baru animasikan yang kepilih aja (`generate_video`).
   Jangan animasikan seed jelek = buang kredit.
2. **B-roll = bisukan.** B-roll cuma background; pakai `generate_audio:false` /
   `sound:off` → lebih murah. Audio utama dari voiceover/musik terpisah.
3. **Resolusi secukupnya.** 720p buat b-roll background. 1080p/4k cuma buat hero shot.
4. **Mode fast/turbo/mini** buat b-roll biasa; mode std/pro cuma buat shot penting.

---

## Stage 1 — Skrip & shotlist (gratis, di mana aja)

1. Tulis naskah / voiceover (per kalimat).
2. Pecah jadi **shot**: tiap kalimat → 1 visual (b-roll) apa.
3. Tentukan: aspect ratio (shorts = **9:16**), durasi tiap shot (biasanya 3–6 dtk).

> Output stage ini: tabel shotlist (nomor shot, teks VO, deskripsi visual, durasi).

## Stage 2 — Generate visual & audio di Higgsfield (makan kredit)

**2a. Voiceover (opsional):** `generate_audio` buat TTS, atau rekam suara sendiri.
**2b. Gambar dulu:** `generate_image` — prompt per shot, aspect `9:16`. Generate beberapa
   variasi, pilih yang paling oke. (Murah → aman bereksperimen.)
**2c. Animasikan:** `generate_video` dengan `start_image` = gambar pilihan, **silent**.

**Rekomendasi model:**
| Kebutuhan | Model | Catatan |
|---|---|---|
| B-roll cepat & murah | `kling3_0_turbo`, `seedance_2_0_mini`, `grok_video` | hemat, 720p, silent |
| Hero shot / kualitas | `veo3`, `kling3_0`, `seedance_2_0` | mahal, simpan buat shot penting |
| Gerak realistis/wajah | `minimax_hailuo` | physics & emosi wajah |

> Cek model lain & detail: tool `models_explore`. Cek saldo: `balance`.

## Stage 3 — Kumpulin aset ke Mac

Hasil generate ada di Higgsfield (`show_generations` / `show_medias` → dapat URL).
Download semua klip + audio ke satu folder kerja di Mac, mis. `~/proyek/footage/`.

## Stage 4 — Jahit final cut (editor, manual — stage kreatif)

Di CapCut / Final Cut / Filmora:
1. Susun b-roll sesuai shotlist + voiceover + musik.
2. Potong, atur timing, transisi, color kalau perlu.
3. **Export "final cut" 9:16 .mp4** — ini versi yang udah DIKUNCI (audio nggak berubah lagi).

> Stage ini sengaja manual: nyusun b-roll itu keputusan kreatif, bukan otomatis.

## Stage 5 — Caption (caption.py — TERAKHIR)

```bash
# bikin subtitle editable dari final cut:
python caption.py transcribe final_cut.mp4 --template hormozi
# (opsional) benerin teks yang salah di Aegisub...
# bakar ke video:
python caption.py burn final_cut.mp4 final_cut.ass
```
Atau langsung: `python caption.py transcribe final_cut.mp4 --template hormozi --burn`

## Stage 6 — Upload

`final_cut.captioned.mp4` siap diupload ke TikTok/Reels/Shorts.

---

## Checklist sekali jalan

- [ ] Skrip + shotlist beres
- [ ] (kalau perlu) Top-up kredit Higgsfield
- [ ] Generate gambar per shot → pilih yang bagus
- [ ] Animasikan gambar terpilih (silent, 9:16)
- [ ] Generate/rekam voiceover + siapin musik
- [ ] Download semua aset ke Mac
- [ ] Jahit final cut di editor → export .mp4 (locked)
- [ ] Jalanin caption.py (transcribe → edit → burn)
- [ ] Upload

---

> **Catatan format:** dipakai 3 format buat variasi konten:
> - **Shorts/Reels/TikTok → 9:16** (default; b-roll AI + voiceover + caption).
> - **YouTube → 16:9** (durasi & pacing lebih panjang, model bisa res lebih tinggi).
>
> Sesuaikan aspect ratio di Stage 1–2 sesuai target platform tiap konten.
