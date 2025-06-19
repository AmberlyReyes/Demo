from sisdental import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    administrador = db.Column(db.Boolean, default=False)
    doctor = db.Column(db.Boolean, default=False)
    asistente = db.Column(db.Boolean, default=False)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'))
    persona = db.relationship('Persona', backref='usuario', uselist=False)