from sisdental import db

class Enfermedad(db.Model):
    __tablename__ = 'enfermedades'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    comentarios = db.Column(db.Text)