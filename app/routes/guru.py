from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.siswa import Siswa
from app.models.user import User
from app.models.record import RecordsTahsin, RecordsTahfidz
from app import db
from app.utils.decorators import role_required
from datetime import datetime
import pandas as pd

guru_bp = Blueprint('guru', __name__)

@guru_bp.route('/dashboard_guru')
@role_required('guru', 'admin')
def dashboard():
    q = request.args.get('q', '').strip().lower()
    query = Siswa.query

    if session.get('role') == 'guru':
        guru_kelas = session.get('kelas', '').strip()
        if guru_kelas and guru_kelas != '-':
            query = query.filter(db.func.lower(Siswa.kelas) == guru_kelas.lower())

    if q:
        query = query.filter(
            (db.func.lower(Siswa.nama).contains(q)) |
            (db.func.lower(Siswa.id).contains(q)) |
            (db.func.lower(Siswa.kelas).contains(q))
        )
    siswa_list = query.all()

    siswa_ids = [s.id for s in siswa_list]
    if siswa_ids:
        tahfidz_records = RecordsTahfidz.query.filter(RecordsTahfidz.siswa_id.in_(siswa_ids)).all()
        tahsin_records = RecordsTahsin.query.filter(RecordsTahsin.siswa_id.in_(siswa_ids)).all()
    else:
        tahfidz_records = []
        tahsin_records = []

    return render_template(
        'guru/dashboard_guru.html', 
        siswa_list=siswa_list, 
        now_date=datetime.now().strftime("%Y-%m-%d"),
        total_tahfidz_rec=len(tahfidz_records),
        total_tahsin_rec=len(tahsin_records)
    )

@guru_bp.route('/tambah_siswa', methods=['POST'])
@role_required('guru', 'admin')
def tambah_siswa():
    nama = request.form.get('nama', '').strip()
    kelas = session.get('kelas', '1A').strip() if session.get('role') == 'guru' else (request.form.get('kelas', '').strip() or '1A')
    custom_id = request.form.get('nisn', '').strip()

    if not custom_id:
        count = Siswa.query.count()
        custom_id = f"S{count + 1:03d}"
        idx = count + 1
        while Siswa.query.get(custom_id):
            idx += 1
            custom_id = f"S{idx:03d}"

    ortu = User.query.filter_by(username=nama, role='ortu').first()
    if not ortu:
        ortu = User(username=nama, password='1234', role='ortu', nama=f"Wali {nama}", kelas=kelas, status='Aktif')
        db.session.add(ortu)
        db.session.flush()

    new_siswa = Siswa(id=custom_id, nama=nama, kelas=kelas, poin=0, user_id_ortu=ortu.id)
    db.session.add(new_siswa)
    db.session.commit()

    flash(f'Data santri {nama} berhasil ditambahkan!', 'success')
    return redirect(request.referrer or url_for('guru.dashboard'))

@guru_bp.route('/catat_tahsin/<id_siswa>', methods=['POST'])
@role_required('guru', 'admin')
def catat_tahsin(id_siswa):
    s = Siswa.query.get_or_404(id_siswa)
    juz_pilihan = request.form.get('juz', '')
    surat_ayat = request.form.get('halaman_akhir', '-')
    gabungan_halaman = f"{juz_pilihan} - {surat_ayat}" if juz_pilihan else surat_ayat

    poin_bonus = int(request.form.get('poin_bonus', 10))
    s.poin += poin_bonus

    rec = RecordsTahsin(
        siswa_id=s.id,
        tanggal=request.form.get('tanggal') or datetime.now().strftime("%Y-%m-%d"),
        halaman_akhir=gabungan_halaman,
        catatan=request.form.get('catatan', ''),
        penilai=session.get('user', 'Musyrif')
    )
    db.session.add(rec)
    db.session.commit()

    flash(f'Setoran Tahsin disimpan & mendapat +{poin_bonus} poin!', 'success')
    return redirect(request.referrer or url_for('guru.dashboard'))

@guru_bp.route('/catat_tahfidz/<id_siswa>', methods=['POST'])
@role_required('guru', 'admin')
def catat_tahfidz(id_siswa):
    s = Siswa.query.get_or_404(id_siswa)
    juz_pilihan = request.form.get('juz', '')
    surat_ayat = request.form.get('hafalan_terakhir', '-')
    gabungan_hafalan = f"{juz_pilihan} - {surat_ayat}" if juz_pilihan else surat_ayat

    poin_bonus = int(request.form.get('poin_bonus', 10))
    s.poin += poin_bonus

    rec = RecordsTahfidz(
        siswa_id=s.id,
        tanggal=request.form.get('tanggal') or datetime.now().strftime("%Y-%m-%d"),
        hafalan_terakhir=gabungan_hafalan,
        catatan=request.form.get('catatan', ''),
        penilai=session.get('user', 'Musyrif')
    )
    db.session.add(rec)
    db.session.commit()

    flash(f'Setoran Tahfidz disimpan & mendapat +{poin_bonus} poin!', 'success')
    return redirect(request.referrer or url_for('guru.dashboard'))

@guru_bp.route('/import_excel', methods=['POST'])
@role_required('guru', 'admin')
def import_excel():
    file = request.files.get('file_excel')
    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            df = pd.read_excel(file)
            imported_count = 0
            default_kelas = session.get('kelas', '1A') if session.get('role') == 'guru' else '1A'
            
            for _, row in df.iterrows():
                nama = str(row.get('Nama', row.get('Nama_Siswa', ''))).strip()
                if not nama or nama.lower() == 'nan': continue
                
                kelas = str(row.get('Kelas', default_kelas)).strip()
                custom_id = str(row.get('NISN', row.get('NISN_ID', ''))).strip()

                if not custom_id or custom_id.lower() == 'nan':
                    count = Siswa.query.count()
                    custom_id = f"S{count + 1:03d}"
                    idx = count + 1
                    while Siswa.query.get(custom_id):
                        idx += 1
                        custom_id = f"S{idx:03d}"

                existing_siswa = Siswa.query.get(custom_id)
                if existing_siswa:
                    existing_siswa.nama = nama
                    existing_siswa.kelas = kelas
                else:
                    ortu = User.query.filter_by(username=nama, role='ortu').first()
                    if not ortu:
                        ortu = User(username=nama, password='1234', role='ortu', nama=f"Wali {nama}", kelas=kelas, status='Aktif')
                        db.session.add(ortu)
                        db.session.flush()

                    new_siswa = Siswa(id=custom_id, nama=nama, kelas=kelas, poin=0, user_id_ortu=ortu.id)
                    db.session.add(new_siswa)
                imported_count += 1

            db.session.commit()
            flash(f'Berhasil mengimpor {imported_count} data santri!', 'success')
        except Exception as e:
            flash(f'Gagal membaca file Excel: {str(e)}', 'danger')
    return redirect(request.referrer or url_for('guru.dashboard'))