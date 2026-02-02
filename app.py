# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import pandas as pd
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'kurye-hakedis-secret-key'

# SQLite veritabanı yapılandırması
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///couriers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Excel dosyalarının bulunduğu klasör (PythonAnywhere)
EXCEL_FOLDER = "/home/Savasky148/mysite"

# Çeviriler
TRANSLATIONS = {
    'tr': {
        'lang_code': 'tr',
        'lang_name': 'Türkçe',
        'dir': 'ltr',
        'site_title': 'Kurye Hakediş Sistemi',
        'login_subtitle': 'Hakediş bilgilerinizi görüntülemek için bilgileri girin',
        'select_week': 'Hafta Seçin',
        'select_week_placeholder': '-- Hafta Seçiniz --',
        'select_name': 'İsminizi Yazın veya Seçin',
        'search_placeholder': 'İsim aramak için yazın...',
        'search_another': 'Başka isim aramak için yazın...',
        'select_name_placeholder': '-- İsminizi Seçiniz --',
        'no_result': 'Sonuç bulunamadı',
        'name_not_found_note': 'Listede isminiz yoksa, seçtiğiniz haftada kaydınız bulunmuyor olabilir.',
        'login_btn': 'Giriş Yap',
        'loading': 'Kuryeler yükleniyor...',
        'welcome': 'Hoş geldiniz',
        'period': 'Dönem',
        'back': 'Geri Dön',
        'earnings_title': 'Hakediş Bilgileri',
        'total_earnings': 'Toplam Hakediş',
        'amount_to_pay': 'Ödenecek Tutar',
        'total_deduction': 'Toplam Kesinti',
        'region': 'Bölge',
        'detailed_info': 'Detaylı Hakediş Bilgileri',
        'earnings': 'Kazançlar',
        'deductions': 'Kesintiler',
        'summary': 'Özet',
        'pickup': 'Pickup',
        'dropoff': 'Dropoff',
        'pickup_amount': 'Pickup Tutar',
        'dropoff_amount': 'Dropoff Tutar',
        'distance_amount': 'Mesafe Tutarı',
        'guaranteed_region': 'Garanti Bölge Tutarı',
        'night_shift': 'Gece Mesaisi Tutarı',
        'region_campaign': 'Bölge Kampanya Tutarı',
        'weekly_package': 'Haftalık Ek Paket Tutarı',
        'daily_bonus': 'Günlük Bonus',
        'vat_payment': 'Hakediş Zam Ödemesi (KDV Dahil)',
        'tip_amount': 'Bahşiş Tutar',
        'withholding': 'Tevkifat Tutar',
        'cash': 'Nakit',
        'credit_card': 'Kredi Kartı',
        'insurance': 'Sigorta Kesintisi',
        'ssk_safety': 'SSK, İş Güvenlik Kesintisi',
        'field_deductions': 'Saha Kesintileri',
        'equipment': 'Ekipman Kesintisi',
        'salary_refund': 'İade Edilmesi Gereken Maaş',
        'yemeksepeti_refund': 'Yemeksepeti İade',
        'no_data': 'Veri bulunamadı.',
        'copyright': '© 2026 Kurye Hakediş Sistemi',
        'error_no_name': 'Lütfen adınızı giriniz!',
        'error_no_week': 'Lütfen bir hafta seçiniz!',
        'error_file_not_found': 'Excel dosyası bulunamadı!',
        'error_courier_not_found': 'Bu isimde bir kurye bulunamadı!',
        'alert_select_name': 'Lütfen listeden isminizi seçin!',
        'language': 'Dil',
        'manage_couriers': 'Kuryeleri Yönet',
        'courier_list': 'Kurye Listesi',
        'add_new_courier': 'Yeni Kurye Ekle',
        'courier_name': 'Kurye Adı',
        'phone_number': 'Telefon Numarası',
        'courier_region': 'Bölge',
        'courier_status': 'Durum',
        'active': 'Aktif',
        'inactive': 'Pasif',
        'add_courier_btn': 'Kurye Ekle',
        'edit_courier_btn': 'Düzenle',
        'delete_courier_btn': 'Sil',
        'save_changes': 'Değişiklikleri Kaydet',
        'cancel': 'İptal',
        'import_from_excel': "Excel'den İçe Aktar",
        'export_to_excel': "Excel'e Aktar",
        'upload_excel_file': 'Excel Dosyası Yükle',
        'choose_file': 'Dosya Seç',
        'upload_btn': 'Yükle',
        'search_courier': 'Kurye Ara...'
    },
    'en': {
        'lang_code': 'en',
        'lang_name': 'English',
        'dir': 'ltr',
        'site_title': 'Courier Earnings System',
        'login_subtitle': 'Enter your information to view your earnings',
        'select_week': 'Select Week',
        'select_week_placeholder': '-- Select Week --',
        'select_name': 'Type or Select Your Name',
        'search_placeholder': 'Type to search name...',
        'search_another': 'Type to search another name...',
        'select_name_placeholder': '-- Select Your Name --',
        'no_result': 'No results found',
        'name_not_found_note': 'If your name is not in the list, you may not have a record for the selected week.',
        'login_btn': 'Login',
        'loading': 'Loading couriers...',
        'welcome': 'Welcome',
        'period': 'Period',
        'back': 'Go Back',
        'earnings_title': 'Earnings Information',
        'total_earnings': 'Total Earnings',
        'amount_to_pay': 'Amount to Pay',
        'total_deduction': 'Total Deduction',
        'region': 'Region',
        'detailed_info': 'Detailed Earnings Information',
        'earnings': 'Earnings',
        'deductions': 'Deductions',
        'summary': 'Summary',
        'pickup': 'Pickup',
        'dropoff': 'Dropoff',
        'pickup_amount': 'Pickup Amount',
        'dropoff_amount': 'Dropoff Amount',
        'distance_amount': 'Distance Amount',
        'guaranteed_region': 'Guaranteed Region Amount',
        'night_shift': 'Night Shift Amount',
        'region_campaign': 'Region Campaign Amount',
        'weekly_package': 'Weekly Package Amount',
        'daily_bonus': 'Daily Bonus',
        'vat_payment': 'VAT Included Payment',
        'tip_amount': 'Tip Amount',
        'withholding': 'Withholding Amount',
        'cash': 'Cash',
        'credit_card': 'Credit Card',
        'insurance': 'Insurance Deduction',
        'ssk_safety': 'SSK, Safety Deduction',
        'field_deductions': 'Field Deductions',
        'equipment': 'Equipment Deduction',
        'salary_refund': 'Salary Refund',
        'yemeksepeti_refund': 'Yemeksepeti Refund',
        'no_data': 'No data found.',
        'copyright': '© 2026 Courier Earnings System',
        'error_no_name': 'Please enter your name!',
        'error_no_week': 'Please select a week!',
        'error_file_not_found': 'Excel file not found!',
        'error_courier_not_found': 'Courier not found!',
        'alert_select_name': 'Please select your name from the list!',
        'language': 'Language',
        'manage_couriers': 'Manage Couriers',
        'courier_list': 'Courier List',
        'add_new_courier': 'Add New Courier',
        'courier_name': 'Courier Name',
        'phone_number': 'Phone Number',
        'courier_region': 'Region',
        'courier_status': 'Status',
        'active': 'Active',
        'inactive': 'Inactive',
        'add_courier_btn': 'Add Courier',
        'edit_courier_btn': 'Edit',
        'delete_courier_btn': 'Delete',
        'save_changes': 'Save Changes',
        'cancel': 'Cancel',
        'import_from_excel': 'Import from Excel',
        'export_to_excel': 'Export to Excel',
        'upload_excel_file': 'Upload Excel File',
        'choose_file': 'Choose File',
        'upload_btn': 'Upload',
        'search_courier': 'Search Courier...'
    },
    'ar': {
        'lang_code': 'ar',
        'lang_name': 'العربية',
        'dir': 'rtl',
        'site_title': 'نظام أرباح المندوب',
        'login_subtitle': 'أدخل معلوماتك لعرض أرباحك',
        'select_week': 'اختر الأسبوع',
        'select_week_placeholder': '-- اختر الأسبوع --',
        'select_name': 'اكتب أو اختر اسمك',
        'search_placeholder': 'اكتب للبحث عن الاسم...',
        'search_another': 'اكتب للبحث عن اسم آخر...',
        'select_name_placeholder': '-- اختر اسمك --',
        'no_result': 'لم يتم العثور على نتائج',
        'name_not_found_note': 'إذا لم يكن اسمك في القائمة، فقد لا يكون لديك سجل للأسبوع المحدد.',
        'login_btn': 'تسجيل الدخول',
        'loading': 'جاري تحميل المندوبين...',
        'welcome': 'مرحباً',
        'period': 'الفترة',
        'back': 'رجوع',
        'earnings_title': 'معلومات الأرباح',
        'total_earnings': 'إجمالي الأرباح',
        'amount_to_pay': 'المبلغ المستحق',
        'total_deduction': 'إجمالي الخصم',
        'region': 'المنطقة',
        'detailed_info': 'معلومات الأرباح التفصيلية',
        'earnings': 'الأرباح',
        'deductions': 'الخصومات',
        'summary': 'الملخص',
        'pickup': 'الاستلام',
        'dropoff': 'التسليم',
        'pickup_amount': 'مبلغ الاستلام',
        'dropoff_amount': 'مبلغ التسليم',
        'distance_amount': 'مبلغ المسافة',
        'guaranteed_region': 'مبلغ المنطقة المضمونة',
        'night_shift': 'مبلغ الوردية الليلية',
        'region_campaign': 'مبلغ حملة المنطقة',
        'weekly_package': 'مبلغ الحزمة الأسبوعية',
        'daily_bonus': 'المكافأة اليومية',
        'vat_payment': 'الدفع شامل الضريبة',
        'tip_amount': 'مبلغ البقشيش',
        'withholding': 'مبلغ الاستقطاع',
        'cash': 'نقداً',
        'credit_card': 'بطاقة ائتمان',
        'insurance': 'خصم التأمين',
        'ssk_safety': 'خصم الضمان والسلامة',
        'field_deductions': 'خصومات الميدان',
        'equipment': 'خصم المعدات',
        'salary_refund': 'استرداد الراتب',
        'yemeksepeti_refund': 'استرداد يميك سبتي',
        'no_data': 'لم يتم العثور على بيانات.',
        'copyright': '© 2026 نظام أرباح المندوب',
        'error_no_name': 'الرجاء إدخال اسمك!',
        'error_no_week': 'الرجاء اختيار أسبوع!',
        'error_file_not_found': 'ملف Excel غير موجود!',
        'error_courier_not_found': 'لم يتم العثور على المندوب!',
        'alert_select_name': 'الرجاء اختيار اسمك من القائمة!',
        'language': 'اللغة',
        'manage_couriers': 'إدارة المندوبين',
        'courier_list': 'قائمة المندوبين',
        'add_new_courier': 'إضافة مندوب جديد',
        'courier_name': 'اسم المندوب',
        'phone_number': 'رقم الهاتف',
        'courier_region': 'المنطقة',
        'courier_status': 'الحالة',
        'active': 'نشط',
        'inactive': 'غير نشط',
        'add_courier_btn': 'إضافة مندوب',
        'edit_courier_btn': 'تعديل',
        'delete_courier_btn': 'حذف',
        'save_changes': 'حفظ التغييرات',
        'cancel': 'إلغاء',
        'import_from_excel': 'استيراد من Excel',
        'export_to_excel': 'تصدير إلى Excel',
        'upload_excel_file': 'رفع ملف Excel',
        'choose_file': 'اختر ملف',
        'upload_btn': 'رفع',
        'search_courier': 'بحث عن مندوب...'
    }
}

# Courier modeli
class Courier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    region = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='Aktif') # Aktif/Pasif

    def __repr__(self):
        return f'<Courier {self.name}>'

def get_translations(lang='tr'):
    return TRANSLATIONS.get(lang, TRANSLATIONS['tr'])

def get_excel_files():
    """Klasördeki tüm Excel dosyalarını listeler"""
    excel_files = []
    # EXCEL_FOLDER'ın var olup olmadığını kontrol et
    if not os.path.exists(EXCEL_FOLDER):
        # Klasör yoksa boş liste döndür ve hata vermesini engelle
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

@app.before_request
def create_tables():
    db.create_all()

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in TRANSLATIONS:
        session['lang'] = lang
    return redirect(request.referrer or url_for('login'))

@app.route('/api/kuryeler/<excel_file>')
def api_kuryeler(excel_file):
    """Seçilen haftanın kurye listesini döndürür (API)"""
    kuryeler = get_kuryeler_by_file(excel_file)
    return jsonify(kuryeler)

@app.route('/', methods=['GET', 'POST'])
def login():
    lang = session.get('lang', 'tr')
    t = get_translations(lang)
    excel_files = get_excel_files()
    
    if request.method == 'POST':
        kurye_adi = request.form.get('kurye_adi', '').strip()
        selected_file = request.form.get('excel_file', '')
        
        if not kurye_adi:
            flash(t['error_no_name'], 'error')
            return redirect(url_for('login'))
        
        if not selected_file:
            flash(t['error_no_week'], 'error')
            return redirect(url_for('login'))
        
        columns, data = get_kurye_data(kurye_adi, selected_file)
        
        if data == "Excel dosyası bulunamadı!":
            flash(t['error_file_not_found'], 'error')
            return redirect(url_for('login'))
        
        if isinstance(data, str):
            flash(data, 'error')
            return redirect(url_for('login'))
        
        if columns is None:
            flash(t['error_courier_not_found'], 'error')
            return redirect(url_for('login'))
        
        selected_display = selected_file.replace('.xlsx', '')
        
        return render_template('dashboard.html', 
                             kurye_adi=kurye_adi, 
                             columns=columns, 
                             data=data,
                             selected_week=selected_display,
                             t=t,
                             current_lang=lang,
                             languages=TRANSLATIONS)
    
    return render_template('login.html', excel_files=excel_files, t=t, current_lang=lang, languages=TRANSLATIONS)

@app.route('/dashboard')
def dashboard():
    return redirect(url_for('login'))

# Kurye Yönetim Sayfası
@app.route('/manage_couriers', methods=['GET', 'POST'])
def manage_couriers():
    lang = session.get('lang', 'tr')
    t = get_translations(lang)
    couriers = Courier.query.all()
    
    return render_template('manage_couriers.html', 
                           couriers=couriers, 
                           t=t, 
                           current_lang=lang, 
                           languages=TRANSLATIONS)

# Yeni Kurye Ekleme
@app.route('/add_courier', methods=['POST'])
def add_courier():
    lang = session.get('lang', 'tr')
    t = get_translations(lang)
    if request.method == 'POST':
        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        region = request.form['region'].strip()
        status = request.form['status'].strip()

        if not name:
            flash(t['error_no_name'], 'error')
            return redirect(url_for('manage_couriers'))

        new_courier = Courier(name=name, phone=phone, region=region, status=status)
        db.session.add(new_courier)
        db.session.commit()
        flash('Kurye başarıyla eklendi!', 'success')
    return redirect(url_for('manage_couriers'))

# Kurye Düzenleme
@app.route('/edit_courier/<int:id>', methods=['GET', 'POST'])
def edit_courier(id):
    lang = session.get('lang', 'tr')
    t = get_translations(lang)
    courier = Courier.query.get_or_404(id)
    if request.method == 'POST':
        courier.name = request.form['name'].strip()
        courier.phone = request.form['phone'].strip()
        courier.region = request.form['region'].strip()
        courier.status = request.form['status'].strip()
        db.session.commit()
        flash('Kurye bilgileri başarıyla güncellendi!', 'success')
        return redirect(url_for('manage_couriers'))
    return render_template('edit_courier.html', 
                           courier=courier, 
                           t=t, 
                           current_lang=lang, 
                           languages=TRANSLATIONS)

# Kurye Silme
@app.route('/delete_courier/<int:id>', methods=['POST'])
def delete_courier(id):
    lang = session.get('lang', 'tr')
    t = get_translations(lang)
    courier = Courier.query.get_or_404(id)
    db.session.delete(courier)
    db.session.commit()
    flash('Kurye başarıyla silindi!', 'success')
    return redirect(url_for('manage_couriers'))

# Excel'den İçe Aktarma
@app.route('/import_excel', methods=['POST'])
def import_excel():
    lang = session.get('lang', 'tr')
    t = get_translations(lang)
    if 'file' not in request.files:
        flash('Dosya seçilmedi!', 'error')
        return redirect(url_for('manage_couriers'))
    file = request.files['file']
    if file.filename == '':
        flash('Dosya seçilmedi!', 'error')
        return redirect(url_for('manage_couriers'))
    if file:
        try:
            df = pd.read_excel(file)
            for index, row in df.iterrows():
                # Sütun isimlerini Excel dosyanıza göre ayarlayın
                name = row.get('Kurye Adı', '').strip()
                phone = row.get('Telefon', '').strip()
                region = row.get('Bölge', '').strip()
                status = row.get('Durum', 'Aktif').strip()

                if name:
                    # Mevcut kuryeyi güncelle veya yeni ekle
                    existing_courier = Courier.query.filter_by(name=name).first()
                    if existing_courier:
                        existing_courier.phone = phone
                        existing_courier.region = region
                        existing_courier.status = status
                    else:
                        new_courier = Courier(name=name, phone=phone, region=region, status=status)
                        db.session.add(new_courier)
            db.session.commit()
            flash('Kuryeler Excel dosyasından başarıyla içe aktarıldı!', 'success')
        except Exception as e:
            flash(f'Excel dosyası içe aktarılırken bir hata oluştu: {str(e)}', 'error')
    return redirect(url_for('manage_couriers'))

# Excel'e Aktarma
@app.route('/export_excel')
def export_excel():
    couriers = Courier.query.all()
    data = []
    for courier in couriers:
        data.append({
            'Kurye Adı': courier.name,
            'Telefon': courier.phone,
            'Bölge': courier.region,
            'Durum': courier.status
        })
    df = pd.DataFrame(data)
    
    output_path = os.path.join(EXCEL_FOLDER, 'kuryeler_export.xlsx')
    # EXCEL_FOLDER'ın var olup olmadığını kontrol et
    if not os.path.exists(EXCEL_FOLDER):
        os.makedirs(EXCEL_FOLDER)
    df.to_excel(output_path, index=False)
    
    flash("Kuryeler başarıyla Excel'e aktarıldı!", 'success')
    return redirect(url_for('manage_couriers'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Uygulama ilk çalıştığında tabloları oluştur
    app.run(debug=True, host='0.0.0.0', port=5000)
