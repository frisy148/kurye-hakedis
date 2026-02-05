# Sorumlu Komisyon – %8.5 Hesaplama

Kendi listendeki kuryelerin **Toplam Hakediş** verisini Excel’den alır; **+** (kazanç) ve **−** (kesintiler) dağılımını hesaplar; toplam hakedişin **%8.5**’ini sizin komisyonunuz olarak gösterir.

## Çalıştırma

```bash
cd komisyon
python app_komisyon.py
```

Tarayıcıda: **http://127.0.0.1:5001**

## Kurye listesi

- **data/benim_kuryelerim.txt** – Her satıra bir kurye adı. `#` ile başlayan satırlar yorumdur.
- İsimler Excel’deki “Ad-Soyad” / ilk sütunla **küçük harfle** eşleştirilir; küçük farklılıklar (boşluk, nokta) tolere edilir.

## Excel

- **Hafta seçimi:** Ana sayfada dropdown’dan bir hafta/dönem Excel’i seçin (proje kökündeki `excel_files/` veya komisyon **Yükle** ile eklenen dosyalar).
- **Yükle:** “Excel Yükle” ile `.xlsx` / `.xls` yükleyebilirsiniz; dosya `komisyon/uploads/` altına kaydedilir ve listede görünür.

## Hesaplama

- Sadece **benim_kuryelerim.txt**’teki isimlerle eşleşen satırlar toplanır.
- **Toplam Hakediş:** Excel’deki “Toplam Hakediş” (veya kazanç sütunları toplamı).
- **Kesintiler:** Tevkifat, Nakit, Kredi Kartı, Sigorta, SSK İş Güvenlik, Saha Kesintileri, Ekipman, İade Edilmesi Gereken Maaş. **Yemeksepeti İade** kesintiye eklenmez (iade olarak + gösterilir).
- **Komisyon:** Toplam Hakediş × %8.5.

## Klasör yapısı

```
komisyon/
  app_komisyon.py
  data/
    benim_kuryelerim.txt
  templates/
    komisyon_index.html
    komisyon_upload.html
  uploads/          (yüklenen Excel’ler)
```

Ana projedeki **excel_files/** klasörü de okunur; Excel’leri oraya koyarsanız komisyon sayfasında da seçilebilir.
