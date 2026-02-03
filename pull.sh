#!/bin/bash
# PythonAnywhere'de çalıştır: bash ~/mysite/pull.sh
# GitHub'dan son değişiklikleri alır

cd ~/mysite || exit 1

echo "=== Git remote ==="
git remote -v

echo ""
echo "=== Fetch + Pull (main) ==="
git fetch origin
git pull origin main

echo ""
echo "=== Güncel durum ==="
git status
git log -1 --oneline

echo ""
echo "Bitti. Web sekmesinden Reload yap."
