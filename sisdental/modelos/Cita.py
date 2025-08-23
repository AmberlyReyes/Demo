from sisdental import db
from datetime import datetime

class Cita(db.Model):
    __tablename__ = 'citas'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    
    plan_tratamiento_id = db.Column(db.Integer, db.ForeignKey('plan_tratamientos.id'), nullable=True)
    
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    estado = db.Column(db.String(50), default='Programada') # Ej: Programada, Confirmada, Cancelada, Realizada
    paciente = db.relationship('Paciente', backref='citas', foreign_keys=[paciente_id])
    # Relación con el Doctor
    doctor = db.relationship('Doctor', backref='citas', foreign_keys=[doctor_id])
    plan = db.relationship('PlanTratamiento', back_populates='citas')
    def __repr__(self):
        return f'<Cita {self.id} del {self.fecha} a las {self.hora}>'
