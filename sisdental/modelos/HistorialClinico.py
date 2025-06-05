from sisdental import db

class HistorialClinico(db.Model):
    __tablename__ = 'historiales_clinicos'
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'))
    comentarios = db.Column(db.Text)
    # Relaciones con enfermedades y consultas se pueden agregar después