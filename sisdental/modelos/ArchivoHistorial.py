from sisdental import db

class ArchivoHistorial(db.Model):
    __tablename__ = 'archivos_historial'
    id = db.Column(db.Integer, primary_key=True)
    historial_clinico_id = db.Column(
        db.Integer,
        db.ForeignKey('historiales_clinicos.id'),
        nullable=False
    )
    filename = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f'<ArchivoHistorial {self.filename}>'