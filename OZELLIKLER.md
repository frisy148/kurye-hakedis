# Kurye Hakediş Sistemi - Özellikler

## Ana sayfa (login)
- **Liderlik tablosu:** Son 2 haftanın Excel verilerine göre en iyi 5 kurye (dropoff sayısı doğru – sütun index: 3)
- **Excel’den hafta listesi:** `mysite` ve `mysite/excel_files` klasörlerindeki .xlsx dosyaları
- **Kurye seçimi:** Hafta seçilince o haftanın kurye listesi API’den gelir, arama ile seçilir
- **Ödeme takvimi:** Butona tıklanınca modal açılır, 2026 ödeme tarihleri tablo halinde
- **Arka plan:** `static/bg-kurye.png` (opacity 0.5)
- **Logo:** `static/lumen-logo.png`
- **Tema:** Açık arka plan (Lümen tarzı)

## Hakediş ekranı (dashboard)
- Excel’den gelen sütunlara göre: Toplam Hakediş, Ödenecek Tutar, Kesintiler, Bölge, Pickup/Dropoff, Kazanç/Kesinti detayları

## Excel formatı
- İlk sütun: Ad-Soyad
- Sütun 1: Bölge, 2: Pickup, 3: Dropoff, 14: Toplam Hakediş (liderlik tablosu için)
- Diğer sütunlar: Dashboard’da isimle kullanılıyor (Toplam Hakediş, Ödenecek Tutar, Bölge, vb.)

## Güncelleme (PythonAnywhere)
1. GitHub’a push
2. Konsol: `cd ~/mysite && git pull origin main`
3. Web → Reload
