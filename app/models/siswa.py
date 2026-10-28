from app import db

class Siswa(db.Model):
    __tablename__ = 'siswa'
    id = db.Column(db.String(50), primary_key=True)
    nama = db.Column(db.String(150), nullable=False)
    kelas = db.Column(db.String(50), nullable=False)
    poin = db.Column(db.Integer, default=0)
    user_id_ortu = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    catatan = db.relationship('RecordsPoin', backref='siswa', lazy=True, cascade="all, delete-orphan", order_by="RecordsPoin.id.asc()")
    tahsin = db.relationship('RecordsTahsin', backref='siswa', lazy=True, cascade="all, delete-orphan", order_by="RecordsTahsin.id.asc()")
    tahfidz = db.relationship('RecordsTahfidz', backref='siswa', lazy=True, cascade="all, delete-orphan", order_by="RecordsTahfidz.id.asc()")

    def to_dict(self):
        return {
            "id": self.id,
            "nama": self.nama,
            "kelas": self.kelas,
            "poin": self.poin,
            "catatan": [c.to_dict() for c in self.catatan],
            "tahsin": [t.to_dict() for t in self.tahsin],
            "tahfidz": [f.to_dict() for f in self.tahfidz]
        }

    def __getitem__(self, key):
        if key == 'catatan': return [c.to_dict() for c in self.catatan]
        if key == 'tahsin': return [t.to_dict() for t in self.tahsin]
        if key == 'tahfidz': return [f.to_dict() for f in self.tahfidz]
        return getattr(self, key)