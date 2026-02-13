# -*- coding: utf-8 -*-
"""
Blueprint: /komisyon – Şifre ile giriş, ana projeyi bozmadan aynı sitede çalışır.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
import os

from . import logic

komisyon_bp = Blueprint(
    'komisyon_bp',
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    url_prefix='/komisyon'
)


@komisyon_bp.before_request
def require_komisyon_auth():
    """Şifre girişi yapılmamışsa sadece giriş sayfasına izin ver."""
    if request.endpoint and request.endpoint.startswith('komisyon_bp.'):
        if request.endpoint == 'komisyon_bp.giris':
            return None
        if session.get('komisyon_auth'):
            return None
        return redirect(url_for('komisyon_bp.giris'))


@komisyon_bp.route('/giris', methods=['GET', 'POST'])
def giris():
    """Şifre ile giriş; doğruysa session['komisyon_auth'] = True."""
    if request.method == 'POST':
        password = request.form.get('sifre', '').strip()
        expected = current_app.config.get('KOMISYON_PASSWORD', '186081')
        if password == expected:
            session['komisyon_auth'] = True
            return redirect(url_for('komisyon_bp.index'))
        flash('Geçersiz şifre.', 'error')
    return render_template('komisyon_giris.html')


@komisyon_bp.route('/')
def index():
    my_couriers = logic.load_my_couriers()
    excel_files = logic.get_excel_files()
    summary = None
    selected_file = None
    selected_file_2 = None

    # 1 hafta: excel=... veya excel1=...  |  2 hafta: excel1=... & excel2=...
    rel1 = request.args.get('excel1')
    rel2 = request.args.get('excel2')
    if rel1 and rel2:
        # 2 haftalık toplam
        summaries = []
        labels = []
        for rel in (rel1, rel2):
            full = logic.resolve_excel_path(rel)
            if full:
                s = logic.compute_period_summary(full, my_couriers)
                if s:
                    summaries.append(s)
                    labels.append(next((f['display_label'] for f in excel_files if f['rel'] == rel), rel))
            else:
                flash(f'Dosya bulunamadı: {rel}', 'error')
        if len(summaries) >= 2:
            summary = logic.merge_period_summaries(summaries, labels)
            selected_file = rel1
            selected_file_2 = rel2
        elif len(summaries) == 1:
            summary = summaries[0]
            summary['week_count'] = 1
            summary['week_labels'] = labels
            selected_file = rel1
    else:
        rel = rel1 or request.args.get('excel')
        if rel:
            full = logic.resolve_excel_path(rel)
            if full:
                summary = logic.compute_period_summary(full, my_couriers)
                if summary:
                    summary['week_count'] = 1
                    summary['week_labels'] = [next((f['display_label'] for f in excel_files if f['rel'] == rel), rel)]
                selected_file = rel
            else:
                flash('Seçilen dosya bulunamadı.', 'error')

    alt_ekipler_ozet = []
    if summary and summary.get('kurye_detay'):
        alt_ekipler_ozet = logic.compute_alt_ekipler_ozet(
            summary['kurye_detay'], logic.load_alt_ekipler()
        )

    return render_template(
        'komisyon_index.html',
        my_couriers_count=len(my_couriers),
        excel_files=excel_files,
        summary=summary,
        selected_file=selected_file,
        selected_file_2=selected_file_2,
        alt_ekipler_ozet=alt_ekipler_ozet,
    )


@komisyon_bp.route('/kuryeler', methods=['GET', 'POST'])
def kuryeler():
    """Kurye listesini düzenle – tek tek ekle veya toplu kaydet."""
    if request.method == 'POST':
        action = request.form.get('action', 'save')
        if action == 'add':
            yeni = request.form.get('yeni_isim', '').strip()
            if yeni:
                current = logic.load_my_couriers_list()
                if yeni not in current:
                    current.append(yeni)
                    logic.save_my_couriers(current)
                    flash(f'"{yeni}" eklendi.', 'success')
                else:
                    flash('Bu isim zaten listede.', 'info')
            return redirect(url_for('komisyon_bp.kuryeler'))
        raw = request.form.get('isimler', '')
        names = [s.strip() for s in raw.splitlines() if s.strip()]
        try:
            logic.save_my_couriers(names)
            flash(f'Liste kaydedildi. {len(names)} kurye.', 'success')
            return redirect(url_for('komisyon_bp.kuryeler'))
        except Exception as e:
            flash(f'Kayıt hatası: {e}', 'error')
    isimler = logic.load_my_couriers_list()
    return render_template('komisyon_kuryeler.html', isimler=isimler)


@komisyon_bp.route('/eski-kuryeler', methods=['GET', 'POST'])
def eski_kuryeler():
    """Eski / ayrılmış kurye listesi – aynı şifre ile erişilir."""
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'add':
            yeni = request.form.get('yeni_isim', '').strip()
            if yeni:
                current = logic.load_old_couriers_list()
                if yeni not in current:
                    current.append(yeni)
                    logic.save_old_couriers(current)
                    flash(f'"{yeni}" eski kurye listesine eklendi.', 'success')
                else:
                    flash('Bu isim zaten listede.', 'info')
            return redirect(url_for('komisyon_bp.eski_kuryeler'))
        if action == 'sil':
            sil_isim = request.form.get('sil_isim', '').strip()
            if sil_isim:
                current = logic.load_old_couriers_list()
                current = [n for n in current if n != sil_isim]
                logic.save_old_couriers(current)
                flash(f'"{sil_isim}" listeden çıkarıldı.', 'success')
            return redirect(url_for('komisyon_bp.eski_kuryeler'))
        raw = request.form.get('isimler', '')
        names = [s.strip() for s in raw.splitlines() if s.strip()]
        logic.save_old_couriers(names)
        flash(f'Eski kurye listesi kaydedildi. {len(names)} isim.', 'success')
        return redirect(url_for('komisyon_bp.eski_kuryeler'))
    isimler = logic.load_old_couriers_list()
    return render_template('komisyon_eski_kuryeler.html', isimler=isimler)


@komisyon_bp.route('/alt-ekipler', methods=['GET', 'POST'])
def alt_ekipler():
    """Profil düzenle – her profil (Barış vb.) için kurye listesi ve yüzde seçimi."""
    isimler = logic.load_my_couriers_list()
    data = logic.load_alt_ekipler()
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'grup_ekle':
            grup = request.form.get('grup_adi', '').strip()
            if grup and grup not in data:
                data[grup] = {'kuryeler': [], 'yuzde': 5}
                logic.save_alt_ekipler(data)
                flash(f'Profil eklendi: {grup}', 'success')
            elif grup in data:
                flash('Bu profil adı zaten var.', 'info')
            return redirect(url_for('komisyon_bp.alt_ekipler'))
        if action == 'grup_sil':
            grup = request.form.get('grup_adi', '').strip()
            if grup in data:
                del data[grup]
                logic.save_alt_ekipler(data)
                flash(f'Profil silindi: {grup}', 'success')
            return redirect(url_for('komisyon_bp.alt_ekipler'))
        if action == 'kaydet':
            for grup_adi in list(data.keys()):
                names = request.form.getlist('kuryeler_' + grup_adi)
                valid = [n.strip() for n in names if n and n.strip() in isimler]
                raw_yuzde = (request.form.get('yuzde_' + grup_adi) or '5').strip().replace(',', '.')
                try:
                    yuzde = float(raw_yuzde)
                    yuzde = max(0, min(100, yuzde))
                except (TypeError, ValueError):
                    yuzde = data.get(grup_adi, {}).get('yuzde', 5)
                data[grup_adi] = {'kuryeler': valid, 'yuzde': yuzde}
            logic.save_alt_ekipler(data)
            flash('Profil atamaları ve yüzdeler kaydedildi.', 'success')
            return redirect(url_for('komisyon_bp.alt_ekipler'))
    return render_template('komisyon_alt_ekipler.html', isimler=isimler, alt_ekipler=data)


@komisyon_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        if f and f.filename:
            name = secure_filename(f.filename)
            if name.lower().endswith(('.xlsx', '.xls')):
                path = os.path.join(logic.UPLOAD_FOLDER, name)
                f.save(path)
                flash(f'Dosya yüklendi: {name}', 'success')
                return redirect(url_for('komisyon_bp.index') + '?excel=uploads/' + name)
            flash('Sadece .xlsx veya .xls kabul edilir.', 'error')
        else:
            flash('Dosya seçin.', 'error')
    return render_template('komisyon_upload.html')


@komisyon_bp.route('/cikis')
def cikis():
    """Oturumu kapat."""
    session.pop('komisyon_auth', None)
    return redirect(url_for('komisyon_bp.giris'))
