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

    return render_template(
        'komisyon_index.html',
        my_couriers_count=len(my_couriers),
        excel_files=excel_files,
        summary=summary,
        selected_file=selected_file,
        selected_file_2=selected_file_2,
    )


@komisyon_bp.route('/kuryeler', methods=['GET', 'POST'])
def kuryeler():
    """Kurye listesini düzenle – ekle/sil, kaydet. Excel atmadan buradan yönetirsin."""
    if request.method == 'POST':
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
