from sisdental import db

class Cita(db.Model):
    __tablename__ = "citas"

    id = db.Column(db.Integer, primary_key=True, index=True)

    #Todo esto de aqui hay que revisarlo cuando el import de la db funcione bien
    #tambien asignarle a ambos ID que sean foreign keys
    doctorId = db.Column(db.Integer, nullable=False)
    pacienteId = db.Column(db.Integer, db.ForeignKey('pacientes.id'),nullable=False)
    #paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'))
    #doctor_id = db.Column(db.Integer, db.ForeignKey('doctores.id'))
    fecha = db.Column(db.Date)
    hora = db.Column(db.Time(150))
    