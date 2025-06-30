from sisdental import db

class HistorialClinico(db.Model):
    __tablename__ = 'historiales_clinicos'
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), unique=True, nullable=False)

    # Relación: un historial tiene muchas consultas
    consultas = db.relationship('Consulta', backref='historial_clinico', lazy=True)