from sisdental import db

class Consulta(db.Model):
    __tablename__ = 'consultas'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctores.id'))
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'))
    fecha = db.Column(db.Date)
    diagnostico = db.Column(db.String(200))
    notas = db.Column(db.Text)