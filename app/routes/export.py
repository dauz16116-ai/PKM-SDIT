from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, Response
from app.models.siswa import Siswa
from app.utils.decorators import login_required
from datetime import datetime
import pandas as pd
import io, os

export_bp = Blueprint('export', __name__)

@export_bp.route('/cetak_hafalan/<id_siswa>')
@export_bp.route('/riwayat_poin/<id_siswa>')
@login_required
def cetak_hafalan_siswa(id_siswa):
    siswa = Siswa.query.get_or_404(id_siswa)
    return render_template('reports/lembar_hafalan.html', siswa=siswa)

@export_bp.route('/export_excel')
@login_required
def export_excel():
    try:
        query = Siswa.query
        if session.get('role') == 'guru':
            guru_kelas = session.get('kelas', '').strip()
            if guru_kelas and guru_kelas != '-':
                query = query.filter(db.func.lower(Siswa.kelas) == guru_kelas.lower())

        siswa_list = query.all()
        data_export = [{"ID / NISN": s.id, "Nama Santri": s.nama, "Kelas": s.kelas, "Akumulasi Poin": s.poin} for s in siswa_list]
        df = pd.DataFrame(data_export)
        
        os.makedirs('data/exports', exist_ok=True)
        export_path = os.path.join('data/exports', 'Laporan_Siswa_SDIT.xlsx')
        df.to_excel(export_path, index=False, engine='openpyxl')
        return send_file(export_path, as_attachment=True, download_name='Laporan_Siswa_SDIT.xlsx')
    except Exception as e:
        flash(f'Export Excel gagal: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('guru.dashboard'))

@export_bp.route('/export_csv')
@login_required
def export_csv():
    try:
        query = Siswa.query
        if session.get('role') == 'guru':
            guru_kelas = session.get('kelas', '').strip()
            if guru_kelas and guru_kelas != '-':
                query = query.filter(db.func.lower(Siswa.kelas) == guru_kelas.lower())

        siswa_list = query.all()
        data_export = [{"ID / NISN": s.id, "Nama Santri": s.nama, "Kelas": s.kelas, "Akumulasi Poin": s.poin} for s in siswa_list]
        df = pd.DataFrame(data_export)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        return Response(buffer.getvalue().encode('utf-8-sig'), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=Laporan_Siswa_SDIT.csv"})
    except Exception as e:
        flash(f'Export CSV gagal: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('guru.dashboard'))

@export_bp.route('/export_pdf')
@login_required
def export_pdf():
    query = Siswa.query
    if session.get('role') == 'guru':
        guru_kelas = session.get('kelas', '').strip()
        if guru_kelas and guru_kelas != '-':
            query = query.filter(db.func.lower(Siswa.kelas) == guru_kelas.lower())

    siswa_list = query.all()
    return render_template('reports/laporansemua.html', siswa_list=siswa_list, tanggal=datetime.now().strftime("%d %B %Y"))