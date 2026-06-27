#!/usr/bin/env bash
# Cek kesiapan Claude Code biar pakai langganan Max (BUKAN API berbayar).
# Jalanin di Mac:  bash setup-claude-code.sh
set -u

echo "==> 1. Claude Code keinstall?"
if command -v claude >/dev/null 2>&1; then
  echo "    [OK] $(claude --version 2>/dev/null)"
else
  echo "    [!] 'claude' nggak ketemu. Install: npm i -g @anthropic-ai/claude-code"
fi

echo
echo "==> 2. Jebakan API key (HARUS kosong biar kepakai Max):"
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  echo "    [!!] ANTHROPIC_API_KEY ke-set -> ini bakal nge-bill API, bukan Max!"
  echo "         Hapus barisnya dari file config di bawah, lalu buka Terminal baru."
else
  echo "    [OK] ANTHROPIC_API_KEY kosong."
fi

echo
echo "==> 3. Sisa 'export ANTHROPIC_API_KEY' di config shell:"
found=0
for f in ~/.zshrc ~/.zprofile ~/.bash_profile ~/.bashrc ~/.profile; do
  if [ -f "$f" ] && grep -q "ANTHROPIC_API_KEY" "$f" 2>/dev/null; then
    grep -nH "ANTHROPIC_API_KEY" "$f"; found=1
  fi
done
[ "$found" -eq 0 ] && echo "    [OK] nggak ada di file config."

echo
echo "==> 4. Langkah terakhir (manual):"
echo "    Jalanin 'claude' -> ketik '/login' -> pilih akun Claude (Max)."
echo "    Cek hasilnya dengan '/status' (harus nunjukin login via subscription)."
