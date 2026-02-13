# -*- coding: utf-8 -*-
"""Komisyon hesaplama mantığı – Flask’tan bağımsız (blueprint ve standalone için)."""
import os
import json
import pandas as pd
from typing import List, Dict, Optional, Set

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, 'data')
EXCEL_FOLDER = os.path.join(PARENT_DIR, 'excel_files')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

KOMISYON_ORANI = 0.085  # %8.5

DEDUCTION_CATEGORIES = {
    'Vergi & Sigorta': ['Tevkifat Tutar', 'Sigorta Kesintisi', 'Ssk, İş Güvenlik Kesintisi'],
    'Tahsilat Farkı': ['Nakit', 'Kredi Kartı'],
    'İadeler': ['İade Edilmesi Gereken Maaş Tutarı'],
    'Ekipman': ['Ekipman Kesintisi'],
    'Saha': ['Saha Kesintileri'],
}
YEMEKSEPETI_IADE_COL = 'Yemeksepeti İade'

EARNING_COLUMNS = [
    'Pickup Tutar', 'Dropoff Tutar', 'Mesafe Tutarı', 'Garanti Bölge Tutarı',
    'Gece Mesaisi Tutarı', 'Bölge Kampanya Tutarı', 'Haftalık Ek Paket Tutarı',
    'Günlük Bonus', 'Hakediş Zam Ödemesi KDV Dahil', 'Bahşiş Tutar'
]


BENIM_KURYELERIM_FILE = os.path.join(DATA_DIR, 'benim_kuryelerim.txt')
ESKI_KURYELER_FILE = os.path.join(DATA_DIR, 'eski_kuryeler.txt')
ALT_EKIPLER_FILE = os.path.join(DATA_DIR, 'alt_ekipler.json')


def load_my_couriers() -> Set[str]:
    """Eşleştirme için: normalize edilmiş isim seti (Türkçe İ/I/ı uyumlu)."""
    names = set()
    for line in load_my_couriers_list():
        names.add(normalize_name(line))
    return names


def load_my_couriers_list() -> List[str]:
    """Düzenleme için: dosyadaki isimler (satır sırası, boş ve # atlanır)."""
    path = BENIM_KURYELERIM_FILE
    out = []
    if not os.path.exists(path):
        return out
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            out.append(line)
    return out


def save_my_couriers(names: List[str]) -> None:
    """Kurye listesini dosyaya yazar (boş satırlar atlanır)."""
    path = BENIM_KURYELERIM_FILE
    lines = [s.strip() for s in names if s and s.strip()]
    with open(path, 'w', encoding='utf-8') as f:
        f.write('# Benim kuryelerim – her satıra bir isim (Excel Ad-Soyad ile eşleşir)\n')
        for line in lines:
            f.write(line.strip() + '\n')


def load_alt_ekipler() -> Dict[str, List[str]]:
    """Alt ekip grupları: { "Barış": ["Ali Veli", ...], ... }. Her grupta o kişiye bağlı kurye isimleri."""
    path = ALT_EKIPLER_FILE
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        return {k: (v if isinstance(v, list) else []) for k, v in data.items()}
    except (json.JSONDecodeError, IOError):
        return {}


def save_alt_ekipler(data: Dict[str, List[str]]) -> None:
    """Alt ekipler JSON dosyasına yazılır."""
    with open(ALT_EKIPLER_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compute_alt_ekipler_ozet(kurye_detay: List[Dict], alt_ekipler: Dict[str, List[str]]) -> List[Dict]:
    """
    kurye_detay ve alt_ekipler ile her grup için bu dönemde eşleşen kuryeleri, toplamı ve %5'i hesaplar.
    Dönen: [ {"grup_adi": "Barış", "kuryeler": [{"ad_soyad": "...", "toplam_hakedis": x}, ...], "toplam": y, "yuzde5": z}, ... ]
    """
    if not kurye_detay or not alt_ekipler:
        return []
    out = []
    for grup_adi, grup_isimleri in alt_ekipler.items():
        grup_norm = {normalize_name(n) for n in (grup_isimleri or [])}
        matched = [k for k in kurye_detay if normalize_name(k.get('ad_soyad', '') or '') in grup_norm]
        toplam = sum(m.get('toplam_hakedis', 0) or 0 for m in matched)
        out.append({
            'grup_adi': grup_adi,
            'kuryeler': matched,
            'toplam': toplam,
            'yuzde5': round(toplam * 0.05, 2),
        })
    return out


def normalize_name(name: str) -> str:
    """
    Excel ile eşleştirme: Türkçe karakterleri tek forma getirir (İ/I/ı, Ğ, Ş, Ü, Ö, Ç).
    PDF: YİĞİT BARAN MECAN | Excel: YIGIT BARAN MECAN → aynı anahtara düşer.
    """
    s = (name or '').strip()
    if not s:
        return ''
    # Türkçe İ/I/ı
    s = s.replace('\u0130', 'i').replace('İ', 'i').replace('ı', 'i').replace('I', 'i')
    s = s.lower()
    # Excel bazen Ğ→G, Ş→S, Ü→U, Ö→O, Ç→C yazar; hepsini ortak forma getir
    for tr, ascii_ in [('ğ', 'g'), ('ş', 's'), ('ü', 'u'), ('ö', 'o'), ('ç', 'c')]:
        s = s.replace(tr, ascii_)
    s = ' '.join(s.split())
    return s


def find_column(columns: List[str], candidates: List[str], fallback_index: Optional[int] = None) -> Optional[str]:
    for c in candidates:
        if c in columns:
            return c
    if fallback_index is not None and 0 <= fallback_index < len(columns):
        return columns[fallback_index]
    return None


def to_num(val) -> float:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 0.0
    try:
        return float(pd.to_numeric(val, errors='coerce') or 0)
    except (TypeError, ValueError):
        return 0.0


def get_excel_files() -> List[Dict]:
    """uploads, excel_files ve proje kökündeki .xlsx/.xls dosyalarını listeler (ana site ile aynı kaynak)."""
    files = []
    # Sıra: önce uploads, sonra excel_files, sonra proje kökü (PythonAnywhere'de Excel'ler burada olabilir)
    for folder in (UPLOAD_FOLDER, EXCEL_FOLDER, PARENT_DIR):
        if not os.path.exists(folder):
            continue
        for f in os.listdir(folder):
            if f.endswith(('.xlsx', '.xls')) and not f.startswith('~'):
                display = f.replace('.xlsx', '').replace('.xls', '')
                label = display.replace('_', ' ')
                for suffix in (' Hakedis Tablosu', ' Hakediş Tablosu', ' Hakedis', ' Hakediş'):
                    if label.endswith(suffix):
                        label = label[:-len(suffix)].strip()
                        break
                if folder == UPLOAD_FOLDER:
                    rel = os.path.join('uploads', f)
                    full = os.path.join(UPLOAD_FOLDER, f)
                elif folder == EXCEL_FOLDER:
                    rel = os.path.join('excel_files', f)  # ana sitedeki excel_files/ ile aynı
                    full = os.path.join(EXCEL_FOLDER, f)
                else:
                    rel = f
                    full = os.path.join(PARENT_DIR, f)
                files.append({
                    'path': full,
                    'filename': f,
                    'display_label': label,
                    'rel': rel,
                })
    files.sort(key=lambda x: x['display_label'], reverse=True)
    return files


def compute_period_summary(excel_path: str, my_couriers: Set[str]) -> Optional[Dict]:
    try:
        df = pd.read_excel(excel_path)
    except Exception:
        return None
    if df.empty or len(df.columns) == 0:
        return None

    columns = [str(c).strip() for c in df.columns.tolist()]
    name_col = find_column(columns, ['Ad-Soyad', 'Ad Soyad', 'Kurye', 'Kurye Adı'], 0)
    if not name_col:
        name_col = columns[0]

    total_hakedis_col = find_column(columns, ['Toplam Hakediş', 'Toplam Hakediş Tutarı'], 11)
    odenecek_col = find_column(columns, ['Ödenecek Tutar', 'Odenecek Tutar', 'Net Ödeme'], None)

    toplam_hakedis = 0.0
    odenecek_ekside = 0.0
    matched_names = []
    ekside_listesi = []
    kurye_kazanci: Dict[str, float] = {}  # ad_soyad -> toplam hakediş (bir haftada aynı isim iki kez olursa toplanır)
    row_count = 0

    for _, row in df.iterrows():
        name_raw = row.get(name_col)
        name = normalize_name(str(name_raw) if name_raw is not None else '')
        if not name or name not in my_couriers:
            continue

        row_count += 1
        ad_soyad = str(name_raw).strip() if name_raw is not None else ''
        matched_names.append(ad_soyad)

        h = to_num(row.get(total_hakedis_col)) if total_hakedis_col else 0
        toplam_hakedis += h
        kurye_kazanci[ad_soyad] = kurye_kazanci.get(ad_soyad, 0.0) + h

        odenecek = to_num(row.get(odenecek_col)) if odenecek_col else 0
        if odenecek < 0:
            odenecek_ekside += odenecek
            ekside_listesi.append({'ad_soyad': ad_soyad, 'tutar': round(odenecek, 2)})

    komisyon = toplam_hakedis * KOMISYON_ORANI
    kurye_detay = [{'ad_soyad': k, 'toplam_hakedis': round(v, 2)} for k, v in sorted(kurye_kazanci.items())]

    return {
        'row_count': row_count,
        'matched_names': sorted(set(matched_names)),
        'toplam_hakedis': round(toplam_hakedis, 2),
        'odenecek_ekside': round(odenecek_ekside, 2),
        'komisyon_yuzde': KOMISYON_ORANI * 100,
        'komisyon_tutar': round(komisyon, 2),
        'ekside_listesi': ekside_listesi,
        'kurye_detay': kurye_detay,
    }


def merge_period_summaries(summaries: List[Dict], week_labels: Optional[List[str]] = None) -> Dict:
    """İki veya daha fazla haftanın özetini tek 2 haftalık özet olarak birleştirir."""
    if not summaries:
        return {}
    if len(summaries) == 1:
        out = dict(summaries[0])
        if week_labels:
            out['week_labels'] = week_labels
        return out

    toplam_hakedis = sum(s.get('toplam_hakedis', 0) for s in summaries)
    odenecek_ekside = sum(s.get('odenecek_ekside', 0) for s in summaries)
    komisyon_tutar = toplam_hakedis * KOMISYON_ORANI

    # Ekside listesini isme göre birleştir
    ekside_by_key: Dict[str, Dict] = {}
    for s in summaries:
        for item in s.get('ekside_listesi', []):
            ad = item.get('ad_soyad', '')
            key = normalize_name(ad)
            t = float(item.get('tutar', 0))
            if key not in ekside_by_key:
                ekside_by_key[key] = {'ad_soyad': ad, 'tutar': 0.0}
            ekside_by_key[key]['tutar'] += t
    ekside_listesi = [{'ad_soyad': v['ad_soyad'], 'tutar': round(v['tutar'], 2)} for v in ekside_by_key.values()]

    # Kurye bazında kazancı birleştir (2 haftada aynı isim toplanır)
    kurye_by_key: Dict[str, Dict] = {}
    for s in summaries:
        for item in s.get('kurye_detay', []):
            ad = item.get('ad_soyad', '')
            key = normalize_name(ad)
            t = float(item.get('toplam_hakedis', 0))
            if key not in kurye_by_key:
                kurye_by_key[key] = {'ad_soyad': ad, 'toplam_hakedis': 0.0}
            kurye_by_key[key]['toplam_hakedis'] += t
    kurye_detay = [{'ad_soyad': v['ad_soyad'], 'toplam_hakedis': round(v['toplam_hakedis'], 2)} for v in kurye_by_key.values()]
    kurye_detay.sort(key=lambda x: x['ad_soyad'])

    matched_set = set()
    for s in summaries:
        matched_set.update(s.get('matched_names', []))
    row_count = sum(s.get('row_count', 0) for s in summaries)

    out = {
        'row_count': row_count,
        'matched_names': sorted(matched_set),
        'toplam_hakedis': round(toplam_hakedis, 2),
        'odenecek_ekside': round(odenecek_ekside, 2),
        'komisyon_yuzde': KOMISYON_ORANI * 100,
        'komisyon_tutar': round(komisyon_tutar, 2),
        'ekside_listesi': ekside_listesi,
        'kurye_detay': kurye_detay,
        'week_count': len(summaries),
        'week_labels': week_labels or [],
    }
    return out


def resolve_excel_path(rel: str) -> Optional[str]:
    """rel (dropdown değeri) -> tam dosya yolu. uploads/, excel_files veya proje kökünde aranır."""
    if not rel:
        return None
    base = os.path.basename(rel)
    if rel.startswith('uploads/'):
        full = os.path.join(UPLOAD_FOLDER, base)
    elif rel.startswith('excel_files/'):
        full = os.path.join(EXCEL_FOLDER, base)
    else:
        full = os.path.join(EXCEL_FOLDER, base)
        if not os.path.exists(full):
            full = os.path.join(PARENT_DIR, base)
    return full if os.path.exists(full) else None


# ---------- Eski kuryeler (listede sadece görüntüleme / yönetim) ----------
def load_old_couriers_list() -> List[str]:
    """Eski kurye listesini döndürür (her satır bir isim)."""
    path = ESKI_KURYELER_FILE
    out = []
    if not os.path.exists(path):
        return out
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            out.append(line)
    return out


def save_old_couriers(names: List[str]) -> None:
    """Eski kurye listesini dosyaya yazar."""
    path = ESKI_KURYELER_FILE
    lines = [s.strip() for s in names if s and s.strip()]
    with open(path, 'w', encoding='utf-8') as f:
        f.write('# Eski / ayrılmış kuryeler – sadece liste\n')
        for line in lines:
            f.write(line.strip() + '\n')
