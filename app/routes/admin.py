from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.user import User
from app import db
from app.utils.decorators import role_required
import pandas as pd

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    guru_list = User.query.filter_by(role='guru').all()
    return render_template('admin/dashboard_admin.html', guru_list=guru_list)

@admin_bp.route('/tambah_guru', methods=['POST'])
@role_required('admin')
def tambah_guru():
    nama = request.form.get('nama', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    kelas = request.form.get('kelas', '-').strip()
    status = request.form.get('status', 'Aktif')

    if User.query.filter_by(username=username).first():
        flash(f'Username "{username}" sudah digunakan!', 'danger')
    else:
        new_guru = User(nama=nama, username=username, password=password, role='guru', kelas=kelas, status=status)
        db.session.add(new_guru)
        db.session.commit()
        flash(f'Guru {nama} berhasil ditambahkan!', 'success')

    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/edit_guru/<int:guru_id>', methods=['POST'])
@role_required('admin')
def edit_guru(guru_id):
    guru = User.query.get_or_404(guru_id)
    guru.nama = request.form.get('nama', '').strip()
    guru.username = request.form.get('username', '').strip()
    guru.kelas = request.form.get('kelas', '-').strip()
    guru.status = request.form.get('status', 'Aktif')

    password_baru = request.form.get('password', '').strip()
    if password_baru:
        guru.password = password_baru

    db.session.commit()
    flash(f'Data guru {guru.nama} berhasil diperbarui!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/hapus_guru/<int:guru_id>')
@role_required('admin')
def hapus_guru(guru_id):
    guru = User.query.get_or_404(guru_id)
    nama = guru.nama
    db.session.delete(guru)
    db.session.commit()
    flash(f'Akun guru {nama} berhasil dihapus!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/import_guru', methods=['POST'])
@role_required('admin')
def import_guru():
    file = request.files.get('file_excel_guru')
    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            df = pd.read_excel(file)
            imported_count = 0
            for _, row in df.iterrows():
                nama = str(row.get('Nama Lengkap', row.get('Nama', ''))).strip()
                username = str(row.get('Username', '')).strip()
                password = str(row.get('Password', '123456')).strip()
                kelas = str(row.get('Kelas', '-')).strip()

                if nama and username and not User.query.filter_by(username=username).first():
                    new_guru = User(nama=nama, username=username, password=password, role='guru', kelas=kelas, status='Aktif')
                    db.session.add(new_guru)
                    imported_count += 1

            db.session.commit()
            flash(f'Berhasil mengimpor {imported_count} data guru!', 'success')
        except Exception as e:
            flash(f'Gagal mengimpor file Excel: {str(e)}', 'danger')
    return redirect(url_for('admin.dashboard'))