# PythonAnywhere Güncelleme

## ⚠️ HER GÜNCELLEMEDE SIRASIYLA:

### 1. GitHub Desktop
**Commit + Push** yap (önce bunu unutma!)

### 2. PythonAnywhere Konsol
Bash açıp şunu yaz:
```bash
cd ~/mysite && git pull origin main
```

### 3. Web
**Web** sekmesi → **Reload** butonu

### 4. Tarayıcı
**Ctrl+Shift+R** ile sayfayı yenile

---

## Detaylı Adımlar

### 1. Konsolu aç
- PythonAnywhere → **Consoles** → **Bash**

### 2. Konsolda çalıştır
```bash
cd ~/mysite && git pull origin main
```

### 3. Web'i yenile
- **Web** sekmesi → **Reload** butonu

---

## Pull çalışmıyorsa (Already up to date / hata)

### A) Remote doğru mu?
Konsolda:
```bash
cd ~/mysite
git remote -v
```
Çıktıda `github.com/frisy148/kurye-hakedis` görünmeli. Farklıysa:
```bash
git remote set-url origin https://github.com/frisy148/kurye-hakedis.git
```

### B) Dal adı: main
```bash
git branch
```
`* main` olmalı. `master` ise:
```bash
git checkout main
```
veya ilk kurulumda:
```bash
git branch -M main
```

### C) Son commit'i kontrol et
```bash
git log -1 --oneline
```
Buradaki commit mesajı GitHub’daki son commit ile aynı olmalı.

---

## İlk kez clone ettiysen
Eğer projeyi GitHub’dan yeni clone ettiysen, klasör `mysite` değilse veya boşsa:
```bash
cd ~
git clone https://github.com/frisy148/kurye-hakedis.git mysite
```
Sonra Web ayarında **Source code** ve **WSGI** yolunu `mysite` klasörüne göre yap.
