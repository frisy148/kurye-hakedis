# -*- coding: utf-8 -*-
"""
Sorumlu komisyon – standalone çalıştırma (python app_komisyon.py).
Aynı mantık ana sitede /komisyon blueprint ile şifreli kullanılır.
"""
from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

try:
    from . import logic
except ImportError:
    import logic

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(PARENT_DIR, 'static'),
    static_url_path='/static')
app.secret_key = 'komisyon-standalone-secret'


@app.route('/')
def index():
    my_couriers = logic.load_my_couriers()
    excel_files = logic.get_excel_files()
    summary = None
    selected_file = None

    rel = request.args.get('excel')
    if rel:
        full = logic.resolve_excel_path(rel)
        if full:
            summary = logic.compute_period_summary(full, my_couriers)
            selected_file = rel
        else:
            flash('Seçilen dosya bulunamadı.', 'error')

    return render_template(
        'komisyon_index.html',
        my_couriers_count=len(my_couriers),
        excel_files=excel_files,
        summary=summary,
        selected_file=selected_file,
    )


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        if f and f.filename:
            name = secure_filename(f.filename)
            if name.lower().endswith(('.xlsx', '.xls')):
                path = os.path.join(logic.UPLOAD_FOLDER, name)
                f.save(path)
                flash(f'Dosya yüklendi: {name}', 'success')
                return redirect(url_for('index') + '?excel=uploads/' + name)
            flash('Sadece .xlsx veya .xls kabul edilir.', 'error')
        else:
            flash('Dosya seçin.', 'error')
    return render_template('komisyon_upload.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
