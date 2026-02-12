# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import pandas as pd
import os
import re
import json
import io
import time
from datetime import datetime
from typing import List, Dict, Optional
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'kurye-hakedis-secret-key'
os.makedirs(app.instance_path, exist_ok=True)

# Önbellek: yoğun trafikte disk/Excel okumayı azaltır (TTL saniye)
_CACHE_TTL = 90
_cache = {'excel_files': (0, None), 'top5': (0, None, None)}

# Excel dosyalarının bulunduğu klasör (PythonAnywhere)
EXCEL_FOLDER = "/home/Savasky148/mysite"
UPLOAD_HISTORY_FILE = os.path.join(app.instance_path, 'uploads.json')
ACTIVE_WEEK_FILE = os.path.join(app.instance_path, 'active_week.json')
HIDDEN_WEEKS_FILE = os.path.join(app.instance_path, 'hidden_weeks.json')
UPLOAD_PASSWORD = os.environ.get('UPLOAD_PASSWORD', '186081')
app.config['KOMISYON_PASSWORD'] = os.environ.get('KOMISYON_PASSWORD', '186081')

# Sorumlu komisyon: /komisyon – şifre ile giriş (ana projeyi bozmaz)
from komisyon.bp import komisyon_bp
app.register_blueprint(komisyon_bp)

# Ödeme Takvimi 2026
ODEME_TAKVIMI = [
    {"calisma": "8 Aralık - 14 Aralık 2025 / 15 Aralık - 21 Aralık 2025", "odeme": "2 Ocak 2026 Cuma"},
    {"calisma": "22 Aralık - 28 Aralık 2025 / 29 Aralık 2025 - 4 Ocak 2026", "odeme": "15 Ocak 2026 Perşembe"},
    {"calisma": "5 Ocak - 11 Ocak 2026 / 12 Ocak - 18 Ocak 2026", "odeme": "29 Ocak 2026 Perşembe"},
    {"calisma": "19 Ocak - 25 Ocak 2026 / 26 Ocak - 1 Şubat 2026", "odeme": "12 Şubat 2026 Perşembe"},
    {"calisma": "2 Şubat - 8 Şubat 2026 / 9 Şubat - 15 Şubat 2026", "odeme": "26 Şubat 2026 Perşembe"},
    {"calisma": "16 Şubat - 22 Şubat 2026 / 23 Şubat - 1 Mart 2026", "odeme": "12 Mart 2026 Perşembe"},
    {"calisma": "2 Mart - 8 Mart 2026 / 9 Mart - 15 Mart 2026", "odeme": "26 Mart 2026 Perşembe"},
    {"calisma": "16 Mart - 22 Mart 2026 / 23 Mart - 29 Mart 2026", "odeme": "9 Nisan 2026 Perşembe"},
    {"calisma": "30 Mart - 5 Nisan 2026 / 6 Nisan - 12 Nisan 2026", "odeme": "22 Nisan 2026 Çarşamba"},
    {"calisma": "13 Nisan - 19 Nisan 2026 / 20 Nisan - 26 Nisan 2026", "odeme": "7 Mayıs 2026 Perşembe"},
    {"calisma": "27 Nisan - 3 Mayıs 2026 / 4 Mayıs - 10 Mayıs 2026", "odeme": "21 Mayıs 2026 Perşembe"},
    {"calisma": "11 Mayıs - 17 Mayıs 2026 / 18 Mayıs - 24 Mayıs 2026", "odeme": "4 Haziran 2026 Perşembe"},
    {"calisma": "25 Mayıs - 31 Mayıs 2026 / 1 Haziran - 7 Haziran 2026", "odeme": "18 Haziran 2026 Perşembe"},
    {"calisma": "8 Haziran - 14 Haziran 2026 / 15 Haziran - 21 Haziran 2026", "odeme": "2 Temmuz 2026 Perşembe"},
    {"calisma": "22 Haziran - 28 Haziran 2026 / 29 Haziran - 5 Temmuz 2026", "odeme": "16 Temmuz 2026 Perşembe"},
    {"calisma": "6 Temmuz - 12 Temmuz 2026 / 13 Temmuz - 19 Temmuz 2026", "odeme": "30 Temmuz 2026 Perşembe"},
    {"calisma": "20 Temmuz - 26 Temmuz 2026 / 27 Temmuz - 2 Ağustos 2026", "odeme": "13 Ağustos 2026 Perşembe"},
    {"calisma": "3 Ağustos - 9 Ağustos 2026 / 10 Ağustos - 16 Ağustos 2026", "odeme": "27 Ağustos 2026 Perşembe"},
    {"calisma": "17 Ağustos - 23 Ağustos 2026 / 24 Ağustos - 30 Ağustos 2026", "odeme": "10 Eylül 2026 Perşembe"},
    {"calisma": "31 Ağustos - 6 Eylül 2026 / 7 Eylül - 13 Eylül 2026", "odeme": "24 Eylül 2026 Perşembe"},
    {"calisma": "14 Eylül - 20 Eylül 2026 / 21 Eylül - 27 Eylül 2026", "odeme": "8 Ekim 2026 Perşembe"},
    {"calisma": "28 Eylül - 4 Ekim 2026 / 5 Ekim - 11 Ekim 2026", "odeme": "22 Ekim 2026 Perşembe"},
    {"calisma": "12 Ekim - 18 Ekim 2026 / 19 Ekim - 25 Ekim 2026", "odeme": "5 Kasım 2026 Perşembe"},
    {"calisma": "26 Ekim - 1 Kasım 2026 / 2 Kasım - 8 Kasım 2026", "odeme": "19 Kasım 2026 Perşembe"},
    {"calisma": "9 Kasım - 15 Kasım 2026 / 16 Kasım - 22 Kasım 2026", "odeme": "3 Aralık 2026 Perşembe"},
    {"calisma": "23 Kasım - 29 Kasım 2026 / 30 Kasım - 6 Aralık 2026", "odeme": "17 Aralık 2026 Perşembe"},
    {"calisma": "7 Aralık - 13 Aralık 2026 / 14 Aralık - 20 Aralık 2026", "odeme": "Ocak 2027"},
    {"calisma": "21 Aralık - 27 Aralık 2026 / 28 Aralık - 31 Aralık 2026", "odeme": "Ocak 2027"},
]

MONTHS_TR = {
    'ocak': 1,
    'subat': 2,
    'şubat': 2,
    'mart': 3,
    'nisan': 4,
    'mayis': 5,
    'mayıs': 5,
    'haziran': 6,
    'temmuz': 7,
    'agustos': 8,
    'ağustos': 8,
    'eylul': 9,
    'eylül': 9,
    'ekim': 10,
    'kasim': 11,
    'kasım': 11,
    'aralik': 12,
    'aralık': 12,
}

def get_excel_files(include_hidden: bool = False) -> List[Dict]:
    """mysite ve mysite/excel_files klasörlerindeki tüm Excel dosyalarını listeler.
    include_hidden=False iken gizlenen haftalar döndürülmez (kuryelerden saklanır).
    """
    excel_files: List[Dict] = []
    active_rel = get_active_week()
    hidden_set = set(get_hidden_weeks())
    # Ana klasör
    def clean_week_label(name: str) -> str:
        """19-25_Ocak_2026_Hakedis_Tablosu -> 19-25 Ocak 2026"""
        s = name.replace('_', ' ')
        for suffix in (' Hakedis Tablosu', ' Hakediş Tablosu', ' Hakedis', ' Hakediş'):
            if s.endswith(suffix):
                s = s[:-len(suffix)].strip()
                break
        return s

    if os.path.exists(EXCEL_FOLDER):
        for file in os.listdir(EXCEL_FOLDER):
            if file.endswith('.xlsx') and not file.startswith('~'):
                display_name = file.replace('.xlsx', '')
                rel = file
                is_hidden = rel in hidden_set
                if not include_hidden and is_hidden:
                    continue
                excel_files.append({
                    'filename': file,
                    'display_name': display_name,
                    'display_label': clean_week_label(display_name),
                    'group': extract_month_group(display_name),
                    'is_active': (rel == active_rel),
                    'is_hidden': is_hidden
                })
    # excel_files alt klasörü (PythonAnywhere'de Excel'ler burada olabilir)
    excel_sub = os.path.join(EXCEL_FOLDER, 'excel_files')
    if os.path.exists(excel_sub):
        for file in os.listdir(excel_sub):
            if file.endswith('.xlsx') and not file.startswith('~'):
                display_name = file.replace('.xlsx', '')
                rel = os.path.join('excel_files', file)
                is_hidden = rel in hidden_set
                if not include_hidden and is_hidden:
                    continue
                excel_files.append({
                    'filename': rel,
                    'display_name': display_name,
                    'display_label': clean_week_label(display_name),
                    'group': extract_month_group(display_name),
                    'is_active': (rel == active_rel),
                    'is_hidden': is_hidden
                })
    excel_files.sort(key=lambda x: x['display_name'], reverse=True)
    return excel_files

def get_kurye_data(kurye_adi, excel_file):
    """Seçilen Excel dosyasından kurye verilerini çeker"""
    try:
        excel_path = os.path.join(EXCEL_FOLDER, excel_file)
        df = pd.read_excel(excel_path)
        if df.empty or len(df.columns) == 0:
            return None, None
        ad_soyad_column = str(df.columns[0]).strip()
        df[ad_soyad_column] = df[ad_soyad_column].astype(str)
        kurye_verisi = df[df[ad_soyad_column].str.lower().str.strip() == kurye_adi.lower().strip()]
        if kurye_verisi.empty:
            return None, None
        # Sütun isimlerini düz metin yap (telefon/Excel farklılıkları için)
        columns = [str(c).strip() for c in df.columns.tolist()]
        # Satırları sütun sırasına göre listeye çevir (duplicate sütun adı olursa da güvenli)
        data = []
        for _, r in kurye_verisi.iterrows():
            row = []
            for i in range(len(columns)):
                try:
                    val = r.iloc[i]
                    row.append(val if pd.notna(val) else None)
                except (IndexError, KeyError):
                    row.append(None)
            data.append(row)
        return columns, data
    except FileNotFoundError:
        return None, "Excel dosyası bulunamadı!"
    except Exception as e:
        return None, f"Hata oluştu: {str(e)}"

def get_kuryeler_by_file(excel_file):
    """Belirli bir Excel dosyasındaki kurye isimlerini getirir"""
    try:
        excel_path = os.path.join(EXCEL_FOLDER, excel_file)
        df = pd.read_excel(excel_path)
        ad_soyad_column = df.columns[0]
        names = df[ad_soyad_column].dropna().unique().tolist()
        kuryeler = [str(name).strip() for name in names if str(name).strip()]
        return sorted(kuryeler)
    except:
        return []

def get_top5_couriers_3weeks(excel_files):
    """Son 2 haftanın verilerini toplayıp en iyi 5 kuryeyi bulur"""
    try:
        # Son 2 hafta
        last_3_weeks = excel_files[:2] if len(excel_files) >= 2 else excel_files
        
        if not last_3_weeks:
            return None
        
        # Tüm kuryelerin verilerini topla
        courier_totals = {}
        
        for week_file in last_3_weeks:
            excel_path = os.path.join(EXCEL_FOLDER, week_file['filename'])
            df = pd.read_excel(excel_path)
            columns = [str(c) for c in df.columns]

            # Sütunları isimle bul (Excel yapısı değişse de doğru sütun okunur)
            ad_soyad_column = find_column(columns, ['Ad-Soyad', 'Ad Soyad', 'Kurye'], 0)
            bolge_column = find_column(columns, ['Bölge', 'Bolge'], 1)
            # Eski dosyalarda: "Dropoff", yeni formatta: "Çoklu Paket"
            dropoff_column = find_column(
                columns,
                ['Dropoff', 'Dropoff Sayısı', 'Dropoff Adedi', 'Çoklu Paket', 'Coklu Paket'],
                3
            )
            hakedis_column = find_column(columns, ['Toplam Hakediş', 'Toplam Hakediş Tutarı'], 14)

            if not ad_soyad_column or not dropoff_column:
                continue

            # Her kurye için verileri topla
            for _, row in df.iterrows():
                name = str(row[ad_soyad_column]).strip()
                if not name or name == 'nan':
                    continue

                dropoff = pd.to_numeric(row[dropoff_column], errors='coerce')
                if pd.isna(dropoff):
                    dropoff = 0

                hakedis = 0
                if hakedis_column and hakedis_column in row.index:
                    hakedis = pd.to_numeric(row[hakedis_column], errors='coerce')
                    if pd.isna(hakedis):
                        hakedis = 0

                bolge = str(row[bolge_column]).strip() if bolge_column and bolge_column in row.index else '-'
                
                if name in courier_totals:
                    courier_totals[name]['dropoff'] += int(dropoff)
                    courier_totals[name]['hakedis'] += float(hakedis)
                else:
                    courier_totals[name] = {
                        'name': name,
                        'dropoff': int(dropoff),
                        'hakedis': float(hakedis),
                        'bolge': bolge
                    }
        
        # Dropoff'a göre sırala ve ilk 5'i al
        sorted_couriers = sorted(courier_totals.values(), key=lambda x: x['dropoff'], reverse=True)
        top5 = sorted_couriers[:5]
        
        # Sıralama ve ödül ekle
        for i, courier in enumerate(top5):
            courier['rank'] = i + 1
            courier['reward'] = 1000 if i == 0 else 500
        
        # Hafta bilgisi
        weeks_text = " + ".join([w['display_name'] for w in last_3_weeks])
        
        return {
            'couriers': top5,
            'weeks': weeks_text,
            'week_count': len(last_3_weeks)
        }
    except Exception:
        return None


def get_excel_files_cached() -> List[Dict]:
    """Excel listesini TTL süre cache'ler; yoğun trafikte disk okumayı azaltır."""
    now = time.time()
    if _cache['excel_files'][1] is not None and (now - _cache['excel_files'][0]) < _CACHE_TTL:
        return _cache['excel_files'][1]
    data = get_excel_files(include_hidden=False)
    _cache['excel_files'] = (now, data)
    return data


def get_top5_couriers_3weeks_cached(excel_files: List[Dict]):
    """Liderlik verisini TTL süre cache'ler (aynı dosya listesi için)."""
    now = time.time()
    key = tuple(ef['filename'] for ef in excel_files) if excel_files else ()
    cached_ts, cached_key, cached_val = _cache['top5']
    if cached_val is not None and cached_key == key and (now - cached_ts) < _CACHE_TTL:
        return cached_val
    data = get_top5_couriers_3weeks(excel_files)
    _cache['top5'] = (now, key, data)
    return data


def invalidate_cache() -> None:
    """Excel yükleme sonrası cache'i temizler; yeni dosya listesi hemen görünsün."""
    _cache['excel_files'] = (0, None)
    _cache['top5'] = (0, None, None)


def find_column(columns: List[str], candidates: List[str], fallback_index: Optional[int] = None) -> Optional[str]:
    """Verilen sütun isimleri arasında ilk eşleşmeyi döndürür, yoksa fallback index kullanır."""
    if not columns:
        return None
    for candidate in candidates:
        if candidate in columns:
            return candidate
    if fallback_index is not None and 0 <= fallback_index < len(columns):
        return columns[fallback_index]
    return None


def to_numeric(value) -> float:
    """NaN ve hataları sıfıra çevirerek numerik değer döndürür."""
    num = pd.to_numeric(value, errors='coerce')
    if pd.isna(num):
        return 0.0
    return float(num)


@app.template_filter('to_float')
def template_to_float(value):
    """Şablonda Excel'den gelen string/object değerleri sayıya çevirir (%.2f için)."""
    return to_numeric(value)


def get_courier_weekly_series(kurye_adi: str, excel_files: List[Dict], limit: int = 12) -> List[Dict]:
    """Kuryenin haftalık paket ve hakediş serisini döndürür."""
    if not kurye_adi or not excel_files:
        return []

    weekly_data = []
    normalized_name = kurye_adi.lower().strip()

    for idx, week_file in enumerate(excel_files[:limit]):
        excel_path = os.path.join(EXCEL_FOLDER, week_file['filename'])
        try:
            df = pd.read_excel(excel_path)
        except Exception:
            continue

        if df.empty:
            continue

        columns = df.columns.tolist()
        ad_soyad_column = columns[0]
        df[ad_soyad_column] = df[ad_soyad_column].astype(str)
        row = df[df[ad_soyad_column].str.lower().str.strip() == normalized_name]

        if row.empty:
            continue

        record = row.iloc[0]

        pickup_col = find_column(columns, ['Pickup', 'Pickup Sayısı', 'Pickup Adedi'], None)
        dropoff_col = find_column(columns, ['Dropoff', 'Dropoff Sayısı', 'Dropoff Adedi'], 3)
        total_earnings_col = find_column(columns, ['Toplam Hakediş', 'Toplam Hakediş Tutarı'], 14)
        payout_col = find_column(columns, ['Ödenecek Tutar', 'Odenecek Tutar', 'Net Ödeme'], None)

        weekly_data.append({
            'label': week_file['display_name'],
            'pickup': to_numeric(record.get(pickup_col)) if pickup_col else 0,
            'dropoff': to_numeric(record.get(dropoff_col)) if dropoff_col else 0,
            'total_earnings': to_numeric(record.get(total_earnings_col)) if total_earnings_col else 0,
            'payout': to_numeric(record.get(payout_col)) if payout_col else 0,
        })

    weekly_data.reverse()  # Eski haftadan yeni haftaya
    return weekly_data


def get_company_overview(excel_files: List[Dict]) -> Optional[Dict]:
    """Son haftaya ait genel istatistikleri döndürür."""
    if not excel_files:
        return None

    latest = excel_files[0]
    excel_path = os.path.join(EXCEL_FOLDER, latest['filename'])
    try:
        df = pd.read_excel(excel_path)
    except Exception:
        return None

    if df.empty:
        return None

    columns = df.columns.tolist()
    ad_soyad_column = columns[0]
    dropoff_col = find_column(columns, ['Dropoff', 'Dropoff Sayısı', 'Dropoff Adedi'], 3)
    total_earnings_col = find_column(columns, ['Toplam Hakediş', 'Toplam Hakediş Tutarı'], 14)
    payout_col = find_column(columns, ['Ödenecek Tutar', 'Odenecek Tutar', 'Net Ödeme'], None)

    def column_sum(col_name):
        if not col_name or col_name not in df:
            return 0.0
        numeric_series = pd.to_numeric(df[col_name], errors='coerce').fillna(0)
        return float(numeric_series.sum())

    total_dropoff = 0.0
    if dropoff_col and dropoff_col in df:
        total_dropoff = float(pd.to_numeric(df[dropoff_col], errors='coerce').fillna(0).sum())

    total_earnings = column_sum(total_earnings_col)
    total_payout = column_sum(payout_col)
    active_couriers = df[ad_soyad_column].dropna().astype(str).str.strip()
    active_courier_count = active_couriers[active_couriers != ''].nunique()

    average_payout = total_payout / active_courier_count if active_courier_count else 0.0

    return {
        'week_label': latest['display_name'],
        'total_dropoff': int(total_dropoff),
        'total_earnings': total_earnings,
        'total_payout': total_payout,
        'active_courier_count': int(active_courier_count),
        'average_payout': average_payout
    }


def normalize_text(value: str) -> str:
    if not value:
        return ''
    text = value.lower()
    replacements = {
        'hakediş tablosu': '',
        'hakediş': '',
        'tablosu': '',
        '.xlsx': '',
        '.xls': ''
    }
    for key, replacement in replacements.items():
        text = text.replace(key, replacement)
    text = text.replace('-', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize_month(month_name: str) -> str:
    mapping = {
        'ı': 'i',
        'İ': 'i',
        'ş': 's',
        'Ş': 's',
        'ğ': 'g',
        'Ğ': 'g',
        'ü': 'u',
        'Ü': 'u',
        'ö': 'o',
        'Ö': 'o',
        'ç': 'c',
        'Ç': 'c'
    }
    for src, target in mapping.items():
        month_name = month_name.replace(src, target)
    return month_name.lower()


def extract_month_group(display_name: str) -> str:
    if not display_name:
        return 'Diğer'
    # Alt çizgili dosya adları da ay/yıl çıksın: "19-25_Ocak_2026_Hakedis_Tablosu" -> "Ocak 2026"
    tokens = display_name.replace('_', ' ').replace('-', ' ').split()
    month_label = None
    year_label = None
    for token in tokens:
        normalized = normalize_month(token)
        if normalized in MONTHS_TR and not month_label:
            month_label = token.capitalize()
        elif token.isdigit() and len(token) == 4:
            year_label = token
    if month_label and year_label:
        return f"{month_label} {year_label}"
    if month_label:
        return month_label
    return 'Diğer'


def parse_turkish_date(date_text: str) -> Optional[datetime]:
    if not date_text:
        return None
    match = re.search(r'(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{4})', date_text)
    if not match:
        return None
    day = int(match.group(1))
    month_name = normalize_month(match.group(2))
    year = int(match.group(3))
    month = MONTHS_TR.get(month_name)
    if not month:
        return None
    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def _parse_week_from_display(display: str) -> Optional[tuple]:
    """'5-11 Ocak' veya 'excel_files/19-25_Ocak_2026_Hakedis_Tablosu' -> (19, 25, 'ocak')."""
    if not display:
        return None
    # Sadece dosya adı kısmını kullan (yol varsa); alt çizgi = boşluk say ki "19-25_Ocak" eşleşsin
    name = display.split('/')[-1].strip().replace('_', ' ')
    # "X-Y Ay" veya "X-Y Ay Yıl" formatı
    m = re.search(r'(\d{1,2})\s*-\s*(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)', name)
    if m:
        return (m.group(1), m.group(2), normalize_month(m.group(3)))
    return None


def _parse_calisma_ranges(calisma: str) -> list:
    """'5 Ocak - 11 Ocak 2026 / 12 Ocak - 18 Ocak 2026' -> [(5,11,'ocak'), (12,18,'ocak')]."""
    if not calisma:
        return []
    ranges = []
    for part in calisma.split('/'):
        part = part.strip()
        # "5 Ocak - 11 Ocak 2026" veya "29 Aralık 2025 - 4 Ocak 2026"
        m = re.search(r'(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s*-\s*(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)', part)
        if m:
            d1, ay1, d2, ay2 = m.group(1), normalize_month(m.group(2)), m.group(3), normalize_month(m.group(4))
            ranges.append((d1, d2, ay1))
            if ay1 != ay2:
                ranges.append((d1, d2, ay2))
    return ranges


def get_payment_reminder(selected_week: str) -> Optional[Dict]:
    if not selected_week or not ODEME_TAKVIMI:
        return None

    week_tup = _parse_week_from_display(selected_week)
    matched_entry = None

    if week_tup:
        start_day, end_day, month_norm = week_tup
        for entry in ODEME_TAKVIMI:
            ranges = _parse_calisma_ranges(entry.get('calisma', ''))
            for r in ranges:
                if r[0] == start_day and r[1] == end_day and r[2] == month_norm:
                    matched_entry = entry
                    break
            if matched_entry:
                break

    if not matched_entry:
        return {
            'week_range': selected_week.split('/')[-1].strip() if selected_week else selected_week,
            'payment_date': 'Ödeme tarihi bulunamadı',
            'days_remaining': None,
            'status': 'pending',
            'message': 'Ödeme tarihi bu dönem için duyurulacak.'
        }

    payment_text = matched_entry.get('odeme', '')
    payment_date = parse_turkish_date(payment_text)
    days_remaining = None
    if payment_date:
        days_remaining = (payment_date.date() - datetime.today().date()).days

    if days_remaining is None:
        message = "Ödeme tarihi bu dönem için duyurulacak."
        status = 'pending'
    elif days_remaining < 0:
        message = f"Bu tarihte ödendi 📅 {payment_text}"
        status = 'paid'
    elif days_remaining == 0:
        message = "Ödeme bugün hesabında!"
        status = 'today'
    elif days_remaining == 1:
        message = "Ödemeye 1 gün kaldı."
        status = 'soon'
    else:
        message = f"Ödemeye {days_remaining} gün kaldı."
        status = 'soon' if days_remaining <= 3 else 'scheduled'

    return {
        'week_range': matched_entry.get('calisma'),
        'payment_date': payment_text,
        'days_remaining': days_remaining,
        'status': status,
        'message': message
    }


def get_row_value(columns: List[str], row: List, column_name: str) -> float:
    if not columns or not row or not column_name:
        return 0.0
    try:
        index = columns.index(column_name)
    except (ValueError, AttributeError):
        return 0.0
    if index >= len(row):
        return 0.0
    try:
        return to_numeric(row[index])
    except (TypeError, ValueError):
        return 0.0


# Sadece bu kesinti kalemleri toplam kesintiye dahil edilir (Excel "Toplam Kesinti Tutarı" kullanılmaz)
# Eski format kolonları + yeni format kolonları birlikte desteklenir.
DEDUCTION_CATEGORIES = {
    'Vergi & Sigorta': [
        'Tevkifat Tutar',
        'Sigorta Kesintisi',
        'Ssk, İş Güvenlik Kesintisi',
        'Ssk Ve İş Güvenliği Kesintisi',
        'Yemeksepeti Sigorta Kesintisi',
    ],
    'Tahsilat Farkı': [
        'Nakit',
        'Kredi Kartı',
        'Nakit, Kredi Kartı Ve Sigorta Kesintisi Toplamı',
    ],
    'İadeler': [
        'İade Edilmesi Gereken Maaş Tutarı',
        'Yemeksepeti İade',
        'Yemeksepeti İade (YapıKredi)',
    ],
    'Ekipman': ['Ekipman Kesintisi'],
    'Saha': ['Saha Kesintileri'],
}

# Kazanç kalemleri (Excel'de toplam 0 olsa bile satırlardan hesaplanabilsin)
EARNING_COLUMNS = [
    'Pickup Tutar', 'Dropoff Tutar', 'Mesafe Tutarı', 'Garanti Bölge Tutarı',
    'Gece Mesaisi Tutarı', 'Bölge Kampanya Tutarı', 'Haftalık Ek Paket Tutarı',
    'Günlük Bonus', 'Hakediş Zam Ödemesi KDV Dahil', 'Bahşiş Tutar'
]


def build_financial_summary(columns: List[str], row: List) -> Dict:
    if not columns or not row:
        return {
            'total_earnings': 0.0, 'total_deductions': 0.0, 'total_deductions_display': 0.0,
            'net_balance': 0.0, 'status': 'neutral', 'deduction_breakdown': []
        }
    total_earnings = get_row_value(columns, row, 'Toplam Hakediş')
    total_deductions = get_row_value(columns, row, 'Toplam Kesinti Tutarı')
    yemeksepeti_iade = get_row_value(columns, row, 'Yemeksepeti İade') or \
        get_row_value(columns, row, 'Yemeksepeti İade (YapıKredi)')

    breakdown = []
    used_columns = set()

    # Yemeksepeti İade kuryeye geri yatan para; toplam kesintiye EKLENMEZ, sadece gösterimde düşülür (+ olarak yansır)
    YEMEKSEPETI_IADE_COLUMN = 'Yemeksepeti İade'

    # 1) Önce Excel'den doğrudan "Ödenecek Tutar" kolonu varsa onu baz alalım (yeni format desteği)
    net_from_excel = get_row_value(columns, row, 'Ödenecek Tutar')
    if net_from_excel:
        # Toplam hakediş boşsa detaylardan hesaplamayı dene
        calculated_earnings = sum(get_row_value(columns, row, col) for col in EARNING_COLUMNS if col in columns)
        if total_earnings == 0 and calculated_earnings != 0:
            total_earnings = calculated_earnings

        net_balance = net_from_excel
        total_deductions_display = max(0.0, total_earnings - net_balance)
        total_deductions = total_deductions_display
        breakdown = []  # Yeni tabloda kesintiler toplu olduğundan detayı boş bırakıyoruz
    else:
        # 2) Eski format: tek tek kesinti kolonlarından hesapla
        for label, names in DEDUCTION_CATEGORIES.items():
            total = 0.0
            for name in names:
                value = get_row_value(columns, row, name)
                if value and name != YEMEKSEPETI_IADE_COLUMN:
                    total += value
                used_columns.add(name)
            if total:
                breakdown.append({'label': label, 'amount': total})

        # Toplam kesinti = sadece gerçek kesintiler (Yemeksepeti İade dahil değil)
        calculated_deductions = sum(float(b.get('amount') or 0) for b in breakdown)
        total_deductions = calculated_deductions
        # Yemeksepeti İade kuryeye iade; net kesinti = toplam kesinti - Yemeksepeti İade (böylece + olarak yansır)
        total_deductions_display = total_deductions - yemeksepeti_iade

        # Toplam hakedişi detaylardan hesapla (Excel sütunu 0 olsa bile)
        calculated_earnings = sum(get_row_value(columns, row, col) for col in EARNING_COLUMNS if col in columns)
        if total_earnings == 0 and calculated_earnings != 0:
            total_earnings = calculated_earnings

        # Ödenecek tutar = Toplam Hakediş - Kesinti (eksi bakiye olabilir)
        net_balance = total_earnings - total_deductions_display

    if net_balance > 0:
        status = 'positive'
    elif net_balance < 0:
        status = 'negative'
    else:
        status = 'neutral'

    breakdown.sort(key=lambda item: float(item.get('amount') or 0), reverse=True)

    return {
        'total_earnings': float(total_earnings or 0),
        'total_deductions': float(total_deductions or 0),
        'total_deductions_display': float(total_deductions_display or 0),
        'net_balance': float(net_balance or 0),
        'status': status,
        'deduction_breakdown': [{'label': b['label'], 'amount': float(b.get('amount') or 0)} for b in breakdown]
    }


def load_upload_history() -> List[Dict]:
    """Yükleme geçmişini döndürür; artık var olmayan Excel dosyalarını filtreler."""
    if not os.path.exists(UPLOAD_HISTORY_FILE):
        return []
    try:
        with open(UPLOAD_HISTORY_FILE, 'r', encoding='utf-8') as history_file:
            data = json.load(history_file)
            if not isinstance(data, list):
                return []

            excel_dir = os.path.join(EXCEL_FOLDER, 'excel_files')
            entries: List[Dict] = []
            for entry in data:
                filename = entry.get('filename')
                if not filename:
                    continue
                excel_path = os.path.join(excel_dir, filename)
                if os.path.exists(excel_path):
                    entries.append(entry)
            return entries
    except (OSError, ValueError):
        return []


def save_upload_history(entries: List[Dict]) -> None:
    try:
        with open(UPLOAD_HISTORY_FILE, 'w', encoding='utf-8') as history_file:
            json.dump(entries, history_file, ensure_ascii=False, indent=2)
    except OSError:
        pass


def append_upload_history(entry: Dict) -> None:
    history = load_upload_history()
    history.insert(0, entry)
    history = history[:20]
    save_upload_history(history)


def enforce_excel_file_limit(max_files: int = 2) -> None:
    """
    excel_files klasöründe en fazla max_files adet Excel dosyası tutulur.
    En yeni dosyalar kalır, eskiler sessizce silinir.
    """
    excel_dir = os.path.join(EXCEL_FOLDER, 'excel_files')
    if not os.path.exists(excel_dir):
        return

    try:
        files = [
            f for f in os.listdir(excel_dir)
            if f.lower().endswith(('.xlsx', '.xls'))
        ]
    except OSError:
        return

    if len(files) <= max_files:
        return

    # Dosyaları son değiştirilme zamanına göre sırala (yeni → eski)
    files_with_mtime = []
    for name in files:
        path = os.path.join(excel_dir, name)
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = 0
        files_with_mtime.append((mtime, name))

    files_with_mtime.sort(reverse=True)  # en yeni başta

    # max_files adetten fazlasını sil
    for _, old_name in files_with_mtime[max_files:]:
        try:
            os.remove(os.path.join(excel_dir, old_name))
        except OSError:
            continue


def get_active_week() -> Optional[str]:
    """Aktif hafta olarak işaretlenen Excel'in relative yolunu döndürür (ör. excel_files/5-11...)."""
    if not os.path.exists(ACTIVE_WEEK_FILE):
        return None
    try:
        with open(ACTIVE_WEEK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get('filename') or None
    except (OSError, ValueError):
        return None
    return None


def set_active_week(filename: str) -> None:
    """Aktif haftayı kaydeder (relative path)."""
    try:
        with open(ACTIVE_WEEK_FILE, 'w', encoding='utf-8') as f:
            json.dump({'filename': filename}, f, ensure_ascii=False)
    except OSError:
        pass


def get_hidden_weeks() -> List[str]:
    """Gizlenen (kuryelerden saklanan) Excel dosyalarının relative yol listesini döndürür."""
    if not os.path.exists(HIDDEN_WEEKS_FILE):
        return []
    try:
        with open(HIDDEN_WEEKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return [str(x) for x in data]
    except (OSError, ValueError):
        return []
    return []


def set_hidden_weeks(weeks: List[str]) -> None:
    """Gizlenen haftaların listesini kaydeder."""
    try:
        with open(HIDDEN_WEEKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(weeks, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def get_uploaded_excels() -> List[Dict]:
    """
    upload sayfası için excel_files klasöründeki mevcut Excel dosyalarını
    (isim, boyut, tarih) ile birlikte döndürür.
    """
    excel_dir = os.path.join(EXCEL_FOLDER, 'excel_files')
    if not os.path.exists(excel_dir):
        return []

    entries: List[Dict] = []
    active_rel = get_active_week()  # ör: excel_files/5-11 Ocak...xlsx
    hidden_set = set(get_hidden_weeks())
    try:
        for name in os.listdir(excel_dir):
            if not name.lower().endswith(('.xlsx', '.xls')):
                continue
            path = os.path.join(excel_dir, name)
            try:
                stat = os.stat(path)
            except OSError:
                continue
            base = os.path.splitext(name)[0]
            group = extract_month_group(base)
            full_rel = os.path.join('excel_files', name)
            is_hidden = full_rel in hidden_set
            entries.append({
                'name': name,
                'size_kb': round(stat.st_size / 1024, 1),
                'mtime': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                'group': group,
                'is_active': (full_rel == active_rel),
                'is_hidden': is_hidden
            })
    except OSError:
        return []

    # Yeni dosyalar üstte görünsün
    entries.sort(key=lambda e: e['mtime'], reverse=True)
    return entries


def inspect_excel_dataframe(df: pd.DataFrame) -> Dict:
    columns = df.columns.tolist()
    row_count = len(df)

    column_checks = {
        'Dropoff': find_column(columns, ['Dropoff', 'Dropoff Sayısı', 'Dropoff Adedi'], 3),
        'Toplam Hakediş': find_column(columns, ['Toplam Hakediş', 'Toplam Hakediş Tutarı'], 14),
        'Ödenecek Tutar': find_column(columns, ['Ödenecek Tutar', 'Odenecek Tutar', 'Net Ödeme'], None)
    }

    missing = [label for label, column_name in column_checks.items() if column_name is None]

    return {
        'row_count': row_count,
        'column_count': len(columns),
        'missing_columns': missing
    }



@app.route('/api/kuryeler/<path:excel_file>')
def api_kuryeler(excel_file):
    """Seçilen haftanın kurye listesini döndürür (API)"""
    kuryeler = get_kuryeler_by_file(excel_file)
    return jsonify(kuryeler)

@app.route('/', methods=['GET', 'POST'])
def login():
    excel_files = get_excel_files_cached()
    top5_data = get_top5_couriers_3weeks_cached(excel_files) if excel_files else None
    
    if request.method == 'POST':
        kurye_adi = request.form.get('kurye_adi', '').strip()
        selected_file = request.form.get('excel_file', '')
        
        if not kurye_adi:
            flash('Lütfen adınızı giriniz!', 'error')
            return redirect(url_for('login'))
        
        if not selected_file:
            flash('Lütfen bir hafta seçiniz!', 'error')
            return redirect(url_for('login'))
        
        columns, data = get_kurye_data(kurye_adi, selected_file)
        
        if data == "Excel dosyası bulunamadı!":
            flash('Excel dosyası bulunamadı!', 'error')
            return redirect(url_for('login'))
        
        if isinstance(data, str):
            flash(data, 'error')
            return redirect(url_for('login'))
        
        if columns is None:
            flash('Bu isimde bir kurye bulunamadı!', 'error')
            return redirect(url_for('login'))

        try:
            selected_display = selected_file.replace('.xlsx', '').replace('.xls', '')
            # Dönem etiketi: excel_files/19-25_Ocak_2026_Hakedis_Tablosu → 19-25 Ocak 2026
            week_label = selected_display.split('/')[-1].replace('_', ' ')
            for suffix in (' Hakedis Tablosu', ' Hakediş Tablosu', ' Hakedis', ' Hakediş'):
                if week_label.endswith(suffix):
                    week_label = week_label[:-len(suffix)].strip()
                    break
            payment_reminder = get_payment_reminder(selected_display)
            first_row = list(data[0]) if data and len(data) > 0 else []
            financial_summary = build_financial_summary(columns, first_row)
            return render_template('dashboard.html',
                                 kurye_adi=kurye_adi,
                                 columns=columns,
                                 data=data,
                                 selected_week=week_label or selected_display,
                                 payment_reminder=payment_reminder,
                                 financial_summary=financial_summary)
        except Exception as e:
            flash('Hakediş sayfası yüklenirken hata oluştu. Excel yapısı beklenenden farklı olabilir.', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html',
                           excel_files=excel_files,
                           top5_data=top5_data,
                           odeme_takvimi=ODEME_TAKVIMI,
                           active_week=get_active_week())

@app.route('/upload', methods=['GET', 'POST'])
def upload_excel():
    history = load_upload_history()
    summary = None
    excels = get_uploaded_excels()
    groups = sorted({e['group'] for e in excels if e.get('group')})

    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        if password != UPLOAD_PASSWORD:
            flash('Geçersiz parola! Yükleme yapılamadı.', 'error')
            return render_template('upload.html', history=history, summary=summary, excels=excels, groups=groups)

        uploaded_file = request.files.get('file')
        if not uploaded_file or uploaded_file.filename == '':
            flash('Lütfen yüklemek için bir Excel dosyası seçin.', 'error')
            return render_template('upload.html', history=history, summary=summary, excels=excels, groups=groups)

        filename = secure_filename(uploaded_file.filename)
        if not filename.lower().endswith(('.xlsx', '.xls')):
            flash('Yalnızca .xlsx veya .xls uzantılı dosyalar kabul edilir.', 'error')
            return render_template('upload.html', history=history, summary=summary, excels=excels, groups=groups)

        file_bytes = uploaded_file.read()
        excel_stream = io.BytesIO(file_bytes)

        try:
            df = pd.read_excel(excel_stream)
        except Exception:
            flash('Excel dosyası okunamadı. Dosyanın bozulmadığından emin olun.', 'error')
            return render_template('upload.html', history=history, summary=summary, excels=excels, groups=groups)

        summary = inspect_excel_dataframe(df)
        summary['filename'] = filename

        if summary['missing_columns']:
            missing_text = ', '.join(summary['missing_columns'])
            flash(f"Excel dosyasında eksik sütunlar var: {missing_text}", 'error')
            return render_template('upload.html', history=history, summary=summary, excels=excels, groups=groups)

        excel_dir = os.path.join(EXCEL_FOLDER, 'excel_files')
        os.makedirs(excel_dir, exist_ok=True)
        destination_path = os.path.join(excel_dir, filename)

        try:
            with open(destination_path, 'wb') as destination_file:
                destination_file.write(file_bytes)
        except OSError:
            flash('Dosya diske kaydedilirken hata oluştu.', 'error')
            return render_template('upload.html', history=history, summary=summary, excels=excels, groups=groups)

        append_upload_history({
            'filename': filename,
            'saved_at': datetime.utcnow().isoformat(),
            'rows': summary['row_count'],
            'columns': summary['column_count']
        })

        flash('Dosya başarıyla yüklendi ve doğrulandı.', 'success')
        invalidate_cache()
        history = load_upload_history()
        excels = get_uploaded_excels()
        groups = sorted({e['group'] for e in excels if e.get('group')})

    return render_template('upload.html', history=history, summary=summary, excels=excels, groups=groups)

@app.route('/upload/delete', methods=['POST'])
def delete_excel():
    """Upload ekranından seçilen Excel dosyasını siler ve geçmişi günceller."""
    filename = request.form.get('filename', '').strip()
    if not filename:
        flash('Silinecek dosya bulunamadı.', 'error')
        return redirect(url_for('upload_excel'))

    # Güvenlik: sadece excel_files altındaki .xlsx/.xls dosyalarına izin ver
    if '/' in filename or '\\' in filename or not filename.lower().endswith(('.xlsx', '.xls')):
        flash('Geçersiz dosya adı.', 'error')
        return redirect(url_for('upload_excel'))

    excel_dir = os.path.join(EXCEL_FOLDER, 'excel_files')
    path = os.path.join(excel_dir, filename)

    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            flash('Dosya silinirken hata oluştu.', 'error')
            return redirect(url_for('upload_excel'))

    # Aktif hafta ise, aktif bilgisini sıfırla
    active_rel = get_active_week()
    rel = os.path.join('excel_files', filename)
    if active_rel and active_rel == rel:
        set_active_week('')

    # Gizli listesinde varsa çıkar
    hidden = set(get_hidden_weeks())
    if rel in hidden:
        hidden.remove(rel)
        set_hidden_weeks(sorted(hidden))

    # Yükleme geçmişinden de kaldır
    history = load_upload_history()
    history = [h for h in history if h.get('filename') != filename]
    save_upload_history(history)

    flash('Dosya ve geçmiş kaydı silindi.', 'success')
    invalidate_cache()

    return redirect(url_for('upload_excel'))


@app.route('/upload/set-active', methods=['POST'])
def set_active_excel():
    """Belirli bir Excel dosyasını aktif hafta olarak işaretler."""
    filename = request.form.get('filename', '').strip()
    if not filename:
        flash('Aktif yapılacak dosya bulunamadı.', 'error')
        return redirect(url_for('upload_excel'))

    if '/' in filename or '\\' in filename or not filename.lower().endswith(('.xlsx', '.xls')):
        flash('Geçersiz dosya adı.', 'error')
        return redirect(url_for('upload_excel'))

    excel_dir = os.path.join(EXCEL_FOLDER, 'excel_files')
    path = os.path.join(excel_dir, filename)
    if not os.path.exists(path):
        flash('Dosya bulunamadı.', 'error')
        return redirect(url_for('upload_excel'))

    rel = os.path.join('excel_files', filename)
    set_active_week(rel)
    flash('Aktif hafta olarak işaretlendi.', 'success')
    invalidate_cache()
    return redirect(url_for('upload_excel'))


@app.route('/upload/toggle-hidden', methods=['POST'])
def toggle_hidden_excel():
    """Seçilen Excel dosyasını kuryelerden gizler veya tekrar görünür yapar."""
    filename = request.form.get('filename', '').strip()
    if not filename:
        flash('Gizlenecek/gösterilecek dosya bulunamadı.', 'error')
        return redirect(url_for('upload_excel'))

    if '/' in filename or '\\' in filename or not filename.lower().endswith(('.xlsx', '.xls')):
        flash('Geçersiz dosya adı.', 'error')
        return redirect(url_for('upload_excel'))

    excel_dir = os.path.join(EXCEL_FOLDER, 'excel_files')
    path = os.path.join(excel_dir, filename)
    if not os.path.exists(path):
        flash('Dosya bulunamadı.', 'error')
        return redirect(url_for('upload_excel'))

    rel = os.path.join('excel_files', filename)
    hidden = set(get_hidden_weeks())

    if rel in hidden:
        hidden.remove(rel)
        flash('Hafta artık kuryelere GÖRÜNÜR.', 'success')
    else:
        hidden.add(rel)
        flash('Hafta kuryelerden GİZLENDİ.', 'success')

    set_hidden_weeks(sorted(hidden))
    invalidate_cache()
    return redirect(url_for('upload_excel'))


@app.route('/download_excel/<path:filename>')
def download_excel(filename):
    """Yüklü Excel dosyasını indirmek için endpoint."""
    # Sadece excel_files altındaki .xlsx/.xls dosyalarına izin ver
    if '..' in filename or filename.startswith('/') or not filename.lower().endswith(('.xlsx', '.xls')):
        flash('Geçersiz indirme isteği.', 'error')
        return redirect(url_for('upload_excel'))

    excel_dir = os.path.join(EXCEL_FOLDER, 'excel_files')
    path = os.path.join(excel_dir, filename)
    if not os.path.exists(path):
        flash('Dosya bulunamadı.', 'error')
        return redirect(url_for('upload_excel'))

    return send_file(path, as_attachment=True)


@app.route('/upload/rename', methods=['POST'])
def rename_excel():
    """Excel dosyasını yeniden adlandırır; geçmiş ve aktif hafta bilgisini günceller."""
    old_name = request.form.get('old_name', '').strip()
    new_name = request.form.get('new_name', '').strip()

    if not old_name or not new_name:
        flash('Yeniden adlandırmak için geçerli bir dosya adı girin.', 'error')
        return redirect(url_for('upload_excel'))

    if '/' in old_name or '\\' in old_name or '/' in new_name or '\\' in new_name:
        flash('Geçersiz dosya adı.', 'error')
        return redirect(url_for('upload_excel'))

    # Uzantı kontrolü: yeni isimde yoksa eskisinin uzantısını ekle
    root_old, ext_old = os.path.splitext(old_name)
    root_new, ext_new = os.path.splitext(new_name)
    if not ext_new:
        ext_new = ext_old or '.xlsx'
    new_name = root_new + ext_new

    if not new_name.lower().endswith(('.xlsx', '.xls')):
        flash('Yalnızca .xlsx veya .xls uzantılı isimlere izin verilir.', 'error')
        return redirect(url_for('upload_excel'))

    excel_dir = os.path.join(EXCEL_FOLDER, 'excel_files')
    old_path = os.path.join(excel_dir, old_name)
    new_path = os.path.join(excel_dir, new_name)

    if not os.path.exists(old_path):
        flash('Yeniden adlandırılacak dosya bulunamadı.', 'error')
        return redirect(url_for('upload_excel'))

    if os.path.exists(new_path):
        flash('Bu isimde bir dosya zaten var.', 'error')
        return redirect(url_for('upload_excel'))

    try:
        os.rename(old_path, new_path)
    except OSError:
        flash('Dosya yeniden adlandırılırken hata oluştu.', 'error')
        return redirect(url_for('upload_excel'))

    # Geçmişi güncelle
    history = load_upload_history()
    for h in history:
        if h.get('filename') == old_name:
            h['filename'] = new_name
    save_upload_history(history)

    # Aktif hafta / gizli hafta dosya adını güncelle
    active_rel = get_active_week()
    old_rel = os.path.join('excel_files', old_name)
    new_rel = os.path.join('excel_files', new_name)
    if active_rel and active_rel == old_rel:
        set_active_week(new_rel)

    hidden = set(get_hidden_weeks())
    if old_rel in hidden:
        hidden.remove(old_rel)
        hidden.add(new_rel)
        set_hidden_weeks(sorted(hidden))

    flash('Dosya adı güncellendi.', 'success')
    invalidate_cache()
    return redirect(url_for('upload_excel'))

@app.route('/dashboard')
def dashboard():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
