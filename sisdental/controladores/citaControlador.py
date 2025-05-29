from . import db
from sisdental.modelos import Cita

class citaControlador:

    @staticmethod
    def crear_cita(data):
        nuevo = Cita(**data)
        db.session.add(nuevo)
        db.session.commit()
        return nuevo

    @staticmethod
    def obtener_todos():
        return Cita.query.all()

    @staticmethod
    def obtener_por_id(paciente_id):
        return Cita.query.get(paciente_id)
    
    @staticmethod
    def obtener_por_paciente(paciente_cedula):
        return Cita.query.get(paciente_cedula)
    
    @staticmethod
    def obtener_por_doctor(paciente_cedula):
        return Cita.query.get(paciente_cedula)
    
    #estos 3 podrian ser algo como "obtener_por_dato" 
    #en lugar de tener el mismo codigo repetido varias veces
    #Puede ser mas confuso pero hace este codigo mas limpio

    @staticmethod
    def actualizar_cita(paciente_id, nuevos_datos):
        paciente = Cita.query.get(paciente_id)
        if not paciente:
            return None
        for clave, valor in nuevos_datos.items():
            setattr(paciente, clave, valor)
        db.session.commit()
        return paciente

    @staticmethod
    def eliminar_paciente(paciente_id):
        paciente = Cita.query.get(paciente_id)
        if paciente:
            db.session.delete(paciente)
            db.session.commit()
            return True
        return False
