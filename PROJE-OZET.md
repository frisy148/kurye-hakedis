# Kurye Hakediş Sistemi – Proje Özeti

Bu dosya, projeyi bırakıp yeni agent/projeye geçerken veya geri dönüldüğünde hızlı referans içindir.

---

## Ne yapar?

- **Kuryeler** hafta seçip isimlerini girerek o haftanın hakediş detayını görür (kazançlar, kesintiler, ödenecek tutar).
- **Ödeme takvimi** ile “Sıradaki ödeme” / “Bu tarihte ödendi” bilgisi gösterilir.
- **Liderlik** (son 2 haftanın top 5) login sayfasında listelenir.
- **Admin** `/upload` ile parola girip Excel yükleyebilir; dosyalar `excel_files/` altına kaydedilir.
- **Sorumlu komisyon** `/komisyon` – Şifre ile giriş; kendi kurye listesine göre toplam hakediş, +/− ve %8.5 komisyon hesaplanır (ana projeden bağımsız, aynı sitede).

---

## Teknoloji

- **Backend:** Flask (`flask_app.py` – ana uygulama)
- **Frontend:** HTML şablonlar (Jinja2), `static/style.css`, `static/theme.js` (koyu/açık tema)
- **Veri:** Excel (.xlsx/.xls) dosyaları; sütun isimleriyle eşleştirme (Toplam Hakediş, Ödenecek Tutar, Nakit, SSK, Yemeksepeti İade vb.)
- **Hosting:** PythonAnywhere (ör. savasky148.pythonanywhere.com)

---

## Önemli dosyalar

| Dosya | Açıklama |
|-------|----------|
| `flask_app.py` | Tüm route’lar, Excel okuma, ödeme takvimi, kesinti/kazanç hesapları, cache |
| `templates/login.html` | Hafta seçimi, isim seçimi, liderlik, ödeme takvimi modal |
| `templates/dashboard.html` | Hakediş özeti, kazanç/kesinti detayı, ödeme kartı |
| `templates/upload.html` | Parola + Excel yükleme formu |
| `static/style.css` | Tüm stiller (login, dashboard, dark mode) |
| `static/theme.js` | Tema (localStorage + data-theme) |
| `DEPLOY.md` | PythonAnywhere deploy adımları |
| `komisyon/` | Sorumlu komisyon: `bp.py` (blueprint), `logic.py`, `data/benim_kuryelerim.txt` |

---

## /komisyon (sorumlu komisyon)

- Adres: **https://savasky148.pythonanywhere.com/komisyon** (veya sitenin `/komisyon` yolu).
- **Şifre:** Varsayılan `komisyon2026`; production’da `KOMISYON_PASSWORD` env ile değiştirilmeli.
- Kendi kurye listesi `komisyon/data/benim_kuryelerim.txt`; Excel’ler ana sitedekiyle aynı (proje kökü + excel_files + komisyon/uploads). Komisyon = toplam hakediş × %8.5.

---

## Hesaplama kuralları (önemli)

- **Toplam kesinti:** Sadece şu kalemlerin toplamı: Tevkifat, Nakit, Kredi Kartı, Sigorta, SSK İş Güvenlik, Saha Kesintileri, Ekipman, İade Edilmesi Gereken Maaş. **Yemeksepeti İade toplam kesintiye eklenmez** (kuryeye iade, artı olarak yansır).
- **Ödenecek tutar:** Toplam Hakediş − (Toplam Kesinti − Yemeksepeti İade). Excel’deki “Ödenecek Tutar” sütunu kullanılmıyor.
- **Hafta eşleştirme:** Dosya adı `19-25_Ocak_2026_Hakedis_Tablosu` veya `5-11 Ocak Hakediş Tablosu` formatında; ödeme takvimiyle eşleşir.

---

## Cache (performans)

- `get_excel_files_cached()`: Excel listesi 90 sn cache.
- `get_top5_couriers_3weeks_cached()`: Liderlik 90 sn cache (aynı dosya listesi için).
- Excel yükleme sonrası `invalidate_cache()` çağrılır.

---

## Deploy (PythonAnywhere)

1. GitHub Desktop → Commit + Push  
2. Konsol: `cd ~/mysite && git pull origin main`  
3. Web sekmesi → Reload  
4. Tarayıcı: Ctrl+Shift+R  

Detay: `DEPLOY.md`

---

## Notlar

- WSGI’da `flask_app.py` kullanılmalı (`from flask_app import app`). `app.py` (manage_couriers vb.) bu projede kullanılmıyor.
- Upload parolası: varsayılan `kurye2026!`; production’da `UPLOAD_PASSWORD` env ile değiştirilmeli.
- Ödeme takvimi `ODEME_TAKVIMI` listesi `flask_app.py` içinde; yeni yıl/dönemde güncellenmeli.
- **Site bozulursa:** Komisyonu tamamen kaldırıp ana haline dönmek için proje kökünde `python revert_komisyon.py` çalıştır (sonra Commit + Push ve PythonAnywhere Reload).

---

*Son güncelleme: Şubat 2026 – /komisyon blueprint eklendi (şifreli); cache, kesinti hesapları, Yemeksepeti İade, dönem etiketi, hafta dropdown temizliği tamamlandı.*
