# -*- coding: utf-8 -*-
"""
Komisyon özelliğini tamamen kaldırır; projeyi komisyon eklenmeden önceki ana haline döndürür.
Site bozulursa bu script'i çalıştır:  python revert_komisyon.py

Yapılanlar:
- komisyon/ klasörü silinir (tüm dosyalar)
- flask_app.py içindeki komisyon satırları kaldırılır
- PROJE-OZET.md komisyon referanslarından temizlenir
"""
import os
import shutil

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
KOMM_DIR = os.path.join(PROJECT_ROOT, 'komisyon')
FLASK_APP = os.path.join(PROJECT_ROOT, 'flask_app.py')
PROJE_OZET = os.path.join(PROJECT_ROOT, 'PROJE-OZET.md')


def main():
    print("Komisyon geri aliniyor, proje ana haline donuyor...")

    # 1. komisyon/ klasörünü sil
    if os.path.isdir(KOMM_DIR):
        shutil.rmtree(KOMM_DIR)
        print("  [OK] komisyon/ klasoru silindi.")
    else:
        print("  [--] komisyon/ zaten yok.")

    # 2. flask_app.py'den komisyon satırlarını kaldır (tek blok)
    with open(FLASK_APP, 'r', encoding='utf-8') as f:
        content = f.read()

    block = """app.config['KOMISYON_PASSWORD'] = os.environ.get('KOMISYON_PASSWORD', '186081')

# Sorumlu komisyon: /komisyon – şifre ile giriş (ana projeyi bozmaz)
from komisyon.bp import komisyon_bp
app.register_blueprint(komisyon_bp)

"""
    if block in content:
        content = content.replace(block, '')
        with open(FLASK_APP, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  [OK] flask_app.py komisyon satirlari kaldirildi.")
    else:
        print("  [--] flask_app.py'de beklenen komisyon blogu bulunamadi (zaten kaldirilmis olabilir).")

    # 3. PROJE-OZET.md'den komisyon kısımlarını kaldır
    with open(PROJE_OZET, 'r', encoding='utf-8') as f:
        content = f.read()

    # Kaldırılacak parçalar
    to_remove = [
        "- **Sorumlu komisyon** `/komisyon` – Şifre ile giriş; kendi kurye listesine göre toplam hakediş, +/− ve %8.5 komisyon hesaplanır (ana projeden bağımsız, aynı sitede).\n\n",
        "| `komisyon/` | Sorumlu komisyon: `bp.py` (blueprint), `logic.py`, `data/benim_kuryelerim.txt` |\n",
        "\n---\n\n## /komisyon (sorumlu komisyon)\n\n- Adres: **https://savasky148.pythonanywhere.com/komisyon** (veya sitenin `/komisyon` yolu).\n- **Şifre:** Varsayılan `186081`; production'da `KOMISYON_PASSWORD` env ile değiştirilebilir.\n- Kendi kurye listesi `komisyon/data/benim_kuryelerim.txt`; Excel'ler ana sitedekiyle aynı (proje kökü + excel_files + komisyon/uploads). Komisyon = toplam hakediş × %8.5.\n\n",
        " – /komisyon blueprint eklendi (şifreli); ",
    ]
    for s in to_remove:
        content = content.replace(s, '')

    with open(PROJE_OZET, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  [OK] PROJE-OZET.md komisyon referanslari temizlendi.")

    print("\nBitti. Proje komisyon eklenmeden onceki ana haline dondu.")
    print("PythonAnywhere'de: git pull sonrasi Web -> Reload yap.")


if __name__ == '__main__':
    main()
