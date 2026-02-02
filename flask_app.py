# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'kurye-hakedis-secret-key'

# Excel dosyalarının bulunduğu klasör (PythonAnywhere)
EXCEL_FOLDER = "/home/Savasky148/mysite"

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

def get_excel_files():
    """Klasördeki tüm Excel dosyalarını listeler"""
    excel_files = []
    if not os.path.exists(EXCEL_FOLDER):
        return []
    for file in os.listdir(EXCEL_FOLDER):
        if file.endswith('.xlsx') and not file.startswith('~'):
            display_name = file.replace('.xlsx', '')
            excel_files.append({
                'filename': file,
                'display_name': display_name
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
    except Exception as e:
        print(f"Hata: {e}")
        return None

@app.route('/api/kuryeler/<excel_file>')
def api_kuryeler(excel_file):
    """Seçilen haftanın kurye listesini döndürür (API)"""
    kuryeler = get_kuryeler_by_file(excel_file)
    return jsonify(kuryeler)

@app.route('/api/debug/columns')
def debug_columns():
    """Excel dosyasındaki sütun isimlerini gösterir (debug için)"""
    excel_files = get_excel_files()
    if not excel_files:
        return jsonify({'error': 'Excel dosyası bulunamadı'})
    
    # İlk Excel dosyasının sütunlarını oku
    excel_path = os.path.join(EXCEL_FOLDER, excel_files[0]['filename'])
    try:
        df = pd.read_excel(excel_path)
        columns = [str(col) for col in df.columns.tolist()]
        # İlk satırı da göster (tüm değerleri string'e çevir)
        first_row = [str(val) for val in df.iloc[0].tolist()] if len(df) > 0 else []
        return jsonify({
            'filename': excel_files[0]['filename'],
            'columns': columns,
            'first_row_sample': first_row
        })
    except Exception as e:
        return jsonify({'error': str(e)})

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
        
        return render_template('dashboard.html', 
                             kurye_adi=kurye_adi, 
                             columns=columns, 
                             data=data,
                             selected_week=selected_display)
    
    return render_template('login.html', excel_files=excel_files, top5_data=top5_data, odeme_takvimi=ODEME_TAKVIMI)

@app.route('/dashboard')
def dashboard():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
