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

@app.route('/api/kuryeler/<excel_file>')
def api_kuryeler(excel_file):
    """Seçilen haftanın kurye listesini döndürür (API)"""
    kuryeler = get_kuryeler_by_file(excel_file)
    return jsonify(kuryeler)

@app.route('/', methods=['GET', 'POST'])
def login():
    excel_files = get_excel_files()
    
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
    
    return render_template('login.html', excel_files=excel_files)

@app.route('/dashboard')
def dashboard():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
