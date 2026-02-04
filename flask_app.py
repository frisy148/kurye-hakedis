# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import os
import re
import json
import io
from datetime import datetime
from typing import List, Dict, Optional
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'kurye-hakedis-secret-key'
os.makedirs(app.instance_path, exist_ok=True)

# Excel dosyalarının bulunduğu klasör (PythonAnywhere)
EXCEL_FOLDER = "/home/Savasky148/mysite"
UPLOAD_HISTORY_FILE = os.path.join(app.instance_path, 'uploads.json')
UPLOAD_PASSWORD = os.environ.get('UPLOAD_PASSWORD', 'kurye2026!')

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

def get_excel_files():
    """mysite ve mysite/excel_files klasörlerindeki tüm Excel dosyalarını listeler"""
    excel_files = []
    # Ana klasör
    if os.path.exists(EXCEL_FOLDER):
        for file in os.listdir(EXCEL_FOLDER):
            if file.endswith('.xlsx') and not file.startswith('~'):
                display_name = file.replace('.xlsx', '')
                excel_files.append({
                    'filename': file,
                    'display_name': display_name,
                    'group': extract_month_group(display_name)
                })
    # excel_files alt klasörü (PythonAnywhere'de Excel'ler burada olabilir)
    excel_sub = os.path.join(EXCEL_FOLDER, 'excel_files')
    if os.path.exists(excel_sub):
        for file in os.listdir(excel_sub):
            if file.endswith('.xlsx') and not file.startswith('~'):
                display_name = file.replace('.xlsx', '')
                excel_files.append({
                    'filename': os.path.join('excel_files', file),
                    'display_name': display_name,
                    'group': extract_month_group(display_name)
                })
    excel_files.sort(key=lambda x: x['display_name'], reverse=True)
    return excel_files

def get_kurye_data(kurye_adi, excel_file):
    """Seçilen Excel dosyasından kurye verilerini çeker"""
    try:
        excel_path = os.path.join(EXCEL_FOLDER, excel_file)
        df = pd.read_excel(excel_path)
        ad_soyad_column = df.columns[0]
        df[ad_soyad_column] = df[ad_soyad_column].astype(str)
        kurye_verisi = df[df[ad_soyad_column].str.lower().str.strip() == kurye_adi.lower().strip()]
        
        if kurye_verisi.empty:
            return None, None
        
        columns = df.columns.tolist()
        data = kurye_verisi.values.tolist()
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
            
            # Sütunları index ile al (daha güvenilir)
            # 0: Ad-Soyad, 1: Bölge, 2: Pickup, 3: Dropoff, 14: Toplam Hakediş
            ad_soyad_column = df.columns[0]
            bolge_column = df.columns[1] if len(df.columns) > 1 else None
            dropoff_column = df.columns[3] if len(df.columns) > 3 else None
            hakedis_column = df.columns[14] if len(df.columns) > 14 else None
            
            if dropoff_column is None:
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
                if hakedis_column:
                    hakedis = pd.to_numeric(row[hakedis_column], errors='coerce')
                    if pd.isna(hakedis):
                        hakedis = 0
                
                bolge = str(row[bolge_column]) if bolge_column else '-'
                
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
    tokens = display_name.replace('-', ' ').split()
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


def get_payment_reminder(selected_week: str) -> Optional[Dict]:
    if not selected_week or not ODEME_TAKVIMI:
        return None

    normalized_week = normalize_text(selected_week)
    matched_entry = None

    for entry in ODEME_TAKVIMI:
        normalized_entry = normalize_text(entry.get('calisma', ''))
        if normalized_week and normalized_week in normalized_entry:
            matched_entry = entry
            break

    if not matched_entry:
        # Yıl içermeyen hafta adları için gün/aralık eşleştir
        range_match = re.search(r'(\d{1,2})\s*-\s*(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)', selected_week)
        if range_match:
            start_day = range_match.group(1)
            end_day = range_match.group(2)
            month_name = normalize_month(range_match.group(3))
            range_key = f"{start_day}-{end_day} {month_name}"

            for entry in ODEME_TAKVIMI:
                entry_text = entry.get('calisma', '')
                entry_matches = re.findall(r'(\d{1,2})\s*-\s*(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)', entry_text)
                for entry_match in entry_matches:
                    entry_key = f"{entry_match[0]}-{entry_match[1]} {normalize_month(entry_match[2])}"
                    if entry_key == range_key:
                        matched_entry = entry
                        break
                if matched_entry:
                    break

    if not matched_entry:
        return {
            'week_range': selected_week,
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
        message = f"Ödeme {abs(days_remaining)} gün gecikti."
        status = 'overdue'
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
    if column_name in columns:
        try:
            index = columns.index(column_name)
        except ValueError:
            return 0.0
        if index < len(row):
            return to_numeric(row[index])
    return 0.0


DEDUCTION_CATEGORIES = {
    'Vergi & Sigorta': ['Tevkifat Tutar', 'Sigorta Kesintisi', 'Ssk, İş Güvenlik Kesintisi'],
    'Tahsilat Farkı': ['Nakit', 'Kredi Kartı'],
    'İadeler': ['İade Edilmesi Gereken Maaş Tutarı', 'Yemeksepeti İade'],
    'Ekipman': ['Ekipman Kesintisi'],
}


def build_financial_summary(columns: List[str], row: List) -> Dict:
    total_earnings = get_row_value(columns, row, 'Toplam Hakediş')
    total_deductions = get_row_value(columns, row, 'Toplam Kesinti Tutarı')
    yemeksepeti_iade = get_row_value(columns, row, 'Yemeksepeti İade')
    # Yemeksepeti İade kuryeye geri yatan para; toplam kesinti gösteriminden düşülür
    total_deductions_display = total_deductions - yemeksepeti_iade
    net_balance = get_row_value(columns, row, 'Ödenecek Tutar')

    if net_balance > 0:
        status = 'positive'
    elif net_balance < 0:
        status = 'negative'
    else:
        status = 'neutral'

    breakdown = []
    used_columns = set()

    for label, names in DEDUCTION_CATEGORIES.items():
        total = 0.0
        for name in names:
            value = get_row_value(columns, row, name)
            if value:
                total += value
                used_columns.add(name)
        if total:
            breakdown.append({'label': label, 'amount': total})

    other_total = 0.0
    for idx, column_name in enumerate(columns):
        if column_name in used_columns or idx == 0:
            continue
        if any(keyword in column_name for keyword in ['Kesinti', 'İade', 'Tutar']) or column_name in ['Nakit', 'Kredi Kartı']:
            value = to_numeric(row[idx])
            if value:
                other_total += value

    if other_total:
        breakdown.append({'label': 'Diğer', 'amount': other_total})

    breakdown.sort(key=lambda item: item['amount'], reverse=True)

    return {
        'total_earnings': total_earnings,
        'total_deductions': total_deductions,
        'total_deductions_display': total_deductions_display,
        'net_balance': net_balance,
        'status': status,
        'deduction_breakdown': breakdown
    }


def load_upload_history() -> List[Dict]:
    if not os.path.exists(UPLOAD_HISTORY_FILE):
        return []
    try:
        with open(UPLOAD_HISTORY_FILE, 'r', encoding='utf-8') as history_file:
            data = json.load(history_file)
            if isinstance(data, list):
                return data
    except (OSError, ValueError):
        pass
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
    excel_files = get_excel_files()
    
    # Son 3 haftanın en iyi 5 kuryesini bul
    top5_data = None
    if excel_files:
        top5_data = get_top5_couriers_3weeks(excel_files)
    
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
        
        selected_display = selected_file.replace('.xlsx', '')
        payment_reminder = get_payment_reminder(selected_display)
        financial_summary = build_financial_summary(columns, data[0] if data else [])
        return render_template('dashboard.html', 
                             kurye_adi=kurye_adi, 
                             columns=columns, 
                             data=data,
                             selected_week=selected_display,
                             payment_reminder=payment_reminder,
                             financial_summary=financial_summary)
    
    return render_template('login.html', excel_files=excel_files, top5_data=top5_data, odeme_takvimi=ODEME_TAKVIMI)

@app.route('/upload', methods=['GET', 'POST'])
def upload_excel():
    history = load_upload_history()
    summary = None

    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        if password != UPLOAD_PASSWORD:
            flash('Geçersiz parola! Yükleme yapılamadı.', 'error')
            return render_template('upload.html', history=history, summary=summary)

        uploaded_file = request.files.get('file')
        if not uploaded_file or uploaded_file.filename == '':
            flash('Lütfen yüklemek için bir Excel dosyası seçin.', 'error')
            return render_template('upload.html', history=history, summary=summary)

        filename = secure_filename(uploaded_file.filename)
        if not filename.lower().endswith(('.xlsx', '.xls')):
            flash('Yalnızca .xlsx veya .xls uzantılı dosyalar kabul edilir.', 'error')
            return render_template('upload.html', history=history, summary=summary)

        file_bytes = uploaded_file.read()
        excel_stream = io.BytesIO(file_bytes)

        try:
            df = pd.read_excel(excel_stream)
        except Exception:
            flash('Excel dosyası okunamadı. Dosyanın bozulmadığından emin olun.', 'error')
            return render_template('upload.html', history=history, summary=summary)

        summary = inspect_excel_dataframe(df)
        summary['filename'] = filename

        if summary['missing_columns']:
            missing_text = ', '.join(summary['missing_columns'])
            flash(f"Excel dosyasında eksik sütunlar var: {missing_text}", 'error')
            return render_template('upload.html', history=history, summary=summary)

        excel_dir = os.path.join(EXCEL_FOLDER, 'excel_files')
        os.makedirs(excel_dir, exist_ok=True)
        destination_path = os.path.join(excel_dir, filename)

        try:
            with open(destination_path, 'wb') as destination_file:
                destination_file.write(file_bytes)
        except OSError:
            flash('Dosya diske kaydedilirken hata oluştu.', 'error')
            return render_template('upload.html', history=history, summary=summary)

        append_upload_history({
            'filename': filename,
            'saved_at': datetime.utcnow().isoformat(),
            'rows': summary['row_count'],
            'columns': summary['column_count']
        })

        flash('Dosya başarıyla yüklendi ve doğrulandı.', 'success')
        history = load_upload_history()

    return render_template('upload.html', history=history, summary=summary)

@app.route('/dashboard')
def dashboard():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
