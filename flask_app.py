# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'kurye-hakedis-secret-key'

# Excel dosyalarının bulunduğu klasör (PythonAnywhere)
EXCEL_FOLDER = "/home/Savasky148/mysite"

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
            
            ad_soyad_column = df.columns[0]
            
            # Sütunları bul
            dropoff_column = None
            hakedis_column = None
            bolge_column = None
            
            for col in df.columns:
                if 'dropoff' in col.lower():
                    dropoff_column = col
                if 'toplam hakediş' in col.lower() or 'toplam hakedis' in col.lower():
                    hakedis_column = col
                if 'bölge' in col.lower() or 'bolge' in col.lower():
                    bolge_column = col
            
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
    
    return render_template('login.html', excel_files=excel_files, top5_data=top5_data)

@app.route('/dashboard')
def dashboard():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
