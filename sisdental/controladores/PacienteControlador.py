from . import db
from .modelos import Paciente

class PacienteControlador:

    @staticmethod
    def crear_paciente(data):
        nuevo = Paciente(**data)
        db.session.add(nuevo)
        db.session.commit()
        return nuevo

    @staticmethod
    def obtener_todos():
        return Paciente.query.all()

    @staticmethod
    def obtener_por_id(paciente_id):
        return Paciente.query.get(paciente_id)

    @staticmethod
    def actualizar_paciente(paciente_id, nuevos_datos):
        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            return None
        for clave, valor in nuevos_datos.items():
            setattr(paciente, clave, valor)
        db.session.commit()
        return paciente

    @staticmethod
    def eliminar_paciente(paciente_id):
        paciente = Paciente.query.get(paciente_id)
        if paciente:
            db.session.delete(paciente)
            db.session.commit()
            return True
        return False
