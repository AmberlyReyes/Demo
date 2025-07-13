from sisdental import db

class HistorialClinico(db.Model):
    __tablename__ = 'historiales_clinicos'
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), unique=True, nullable=False)
    antecedentes_familiares = db.Column(db.Text)
    medicacion             = db.Column(db.Text)
    consultas = db.relationship('Consulta', backref='historial_clinico', lazy=True)
    # Relación con archivos adjuntos
    archivos  = db.relationship('ArchivoHistorial', backref='historial', lazy=True)