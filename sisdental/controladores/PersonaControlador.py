from sisdental import db
from sisdental.modelos.Persona import Persona

class PersonaControlador:
    @staticmethod
    def crear_persona(data):
        p = Persona(**data)
        db.session.add(p)
        db.session.commit()
        return p

    @staticmethod
    def obtener_por_id(id):
        return Persona.query.get(id)

    @staticmethod
    def actualizar_persona(id, datos):
        p = Persona.query.get(id)
        for k, v in datos.items():
            setattr(p, k, v)
        db.session.commit()
        return p

    @staticmethod
    def eliminar_persona(id):
        p = Persona.query.get(id)
        db.session.delete(p)
        db.session.commit()
        return True