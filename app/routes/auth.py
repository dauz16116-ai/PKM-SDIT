from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user import User
from app.models.siswa import Siswa
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if session.get('role') == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif session.get('role') in ('guru', 'admin'):
        return redirect(url_for('guru.dashboard'))
    elif session.get('role') == 'ortu':
        return redirect(url_for('ortu.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter(db.func.lower(User.username) == username.lower()).first()

        if user and user.password == password:
            if user.status == 'Tidak Aktif':
                flash('Akun Anda telah dinonaktifkan!', 'danger')
                return render_template('auth/login.html')

            session.permanent = True
            session['user_id'] = user.id
            session['user'] = user.nama or user.username
            session['username'] = user.username
            session['role'] = user.role
            session['kelas'] = user.kelas or '-'

            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'guru':
                return redirect(url_for('guru.dashboard'))
            elif user.role == 'ortu':
                siswa = Siswa.query.filter((Siswa.user_id_ortu == user.id) | (db.func.lower(Siswa.nama) == username.lower())).first()
                if siswa:
                    session['siswa_id'] = siswa.id
                    session['kelas'] = siswa.kelas
                return redirect(url_for('ortu.dashboard'))

        siswa = Siswa.query.filter(db.func.lower(Siswa.nama) == username.lower()).first()
        if siswa and password == '1234':
            ortu = User.query.filter_by(username=siswa.nama, role='ortu').first()
            if not ortu:
                ortu = User(username=siswa.nama, password='1234', role='ortu', nama=f"Wali {siswa.nama}", kelas=siswa.kelas, status='Aktif')
                db.session.add(ortu)
                db.session.flush()
                siswa.user_id_ortu = ortu.id
                db.session.commit()

            session.permanent = True
            session['user_id'] = ortu.id
            session['user'] = ortu.nama
            session['username'] = ortu.username
            session['role'] = 'ortu'
            session['kelas'] = siswa.kelas
            session['siswa_id'] = siswa.id
            return redirect(url_for('ortu.dashboard'))

        flash('Username atau Password salah!', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))