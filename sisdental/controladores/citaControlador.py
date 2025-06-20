from sisdental import db
from sisdental.modelos.Cita import Cita

class citaControlador:

    @staticmethod
    def crear_cita(data):
        try:
            nuevo = Cita(**data)
            db.session.add(nuevo)
            db.session.commit()
            return nuevo
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear Cita: {e}")
            return None

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
    
    @staticmethod
    def obtener_por_fecha(fecha):
        return Cita.query.filter_by(fecha=fecha)
    @staticmethod
    def obtener_por_paciente(paciente_id):
        return Cita.query.filter_by(paciente_id=paciente_id).all()

    @staticmethod
    def obtener_por_paciente_y_fecha(paciente_id, fecha):
        return Cita.query.filter_by(paciente_id=paciente_id, fecha=fecha).all()

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
