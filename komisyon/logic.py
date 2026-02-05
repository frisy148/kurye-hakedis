# -*- coding: utf-8 -*-
"""Komisyon hesaplama mantığı – Flask’tan bağımsız (blueprint ve standalone için)."""
import os
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


def load_my_couriers() -> Set[str]:
    path = os.path.join(DATA_DIR, 'benim_kuryelerim.txt')
    names = set()
    if not os.path.exists(path):
        return names
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            names.add(line.lower().strip())
    return names


def normalize_name(name: str) -> str:
    return (name or '').lower().strip()


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
                    rel = f
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

    total_hakedis_col = find_column(columns, ['Toplam Hakediş', 'Toplam Hakediş Tutarı'], 14)
    yemek_iade_col = YEMEKSEPETI_IADE_COL if YEMEKSEPETI_IADE_COL in columns else None

    toplam_hakedis = 0.0
    toplam_kesinti = 0.0
    yemeksepeti_iade = 0.0
    breakdown = {label: 0.0 for label in DEDUCTION_CATEGORIES}
    kazanim_detay = {col: 0.0 for col in EARNING_COLUMNS if col in columns}
    matched_names = []
    row_count = 0

    for _, row in df.iterrows():
        name_raw = row.get(name_col)
        name = normalize_name(str(name_raw) if name_raw is not None else '')
        if not name or name not in my_couriers:
            continue

        row_count += 1
        matched_names.append(str(name_raw).strip())

        h = to_num(row.get(total_hakedis_col)) if total_hakedis_col else 0
        if h == 0 and total_hakedis_col is None:
            for col in EARNING_COLUMNS:
                if col in row.index:
                    h += to_num(row.get(col))
        toplam_hakedis += h

        if yemek_iade_col and yemek_iade_col in row.index:
            yemeksepeti_iade += to_num(row.get(yemek_iade_col))

        for label, col_names in DEDUCTION_CATEGORIES.items():
            for col in col_names:
                if col in row.index:
                    val = to_num(row.get(col))
                    breakdown[label] += val
                    toplam_kesinti += val

        for col in kazanim_detay:
            kazanim_detay[col] += to_num(row.get(col))

    net_kesinti_gosterim = toplam_kesinti - yemeksepeti_iade
    komisyon = toplam_hakedis * KOMISYON_ORANI

    return {
        'row_count': row_count,
        'matched_names': sorted(set(matched_names)),
        'toplam_hakedis': round(toplam_hakedis, 2),
        'toplam_kesinti': round(toplam_kesinti, 2),
        'yemeksepeti_iade': round(yemeksepeti_iade, 2),
        'net_kesinti_gosterim': round(net_kesinti_gosterim, 2),
        'odenecek_net': round(toplam_hakedis - net_kesinti_gosterim, 2),
        'komisyon_yuzde': KOMISYON_ORANI * 100,
        'komisyon_tutar': round(komisyon, 2),
        'breakdown': {k: round(v, 2) for k, v in breakdown.items() if v},
        'kazanim_detay': {k: round(v, 2) for k, v in kazanim_detay.items() if v},
    }


def resolve_excel_path(rel: str) -> Optional[str]:
    """rel (dropdown değeri) -> tam dosya yolu. uploads/, excel_files veya proje kökünde aranır."""
    if not rel:
        return None
    base = os.path.basename(rel)
    if rel.startswith('uploads/'):
        full = os.path.join(UPLOAD_FOLDER, base)
    else:
        # Önce excel_files, yoksa proje kökü (ana sitedeki Excel'ler)
        full = os.path.join(EXCEL_FOLDER, base)
        if not os.path.exists(full):
            full = os.path.join(PARENT_DIR, base)
    return full if os.path.exists(full) else None
