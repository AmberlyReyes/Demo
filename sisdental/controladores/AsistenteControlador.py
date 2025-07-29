from sisdental import db
#from sisdental.modelos import Paciente
from sisdental.modelos.Asistente import Asistente

class AsistenteControlador:

    @staticmethod
    def crear(data):
        try:
            # Obligatorio para que la fila sea de tipo 'asistente'
            data['tipo'] = 'asistente'
            nuevo = Asistente(**data)
            db.session.add(nuevo)
            db.session.commit()
            return nuevo
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear asistente: {e}")
            return None

    @staticmethod
    def obtener_todos():
        return Asistente.query.all()

    @staticmethod
    def obtener_por_id(asistente_id):
        return Asistente.query.get(asistente_id)
    
    @staticmethod
    def obtener_por_cedula(asistente_cedula):
         return Asistente.query.filter_by(cedula=asistente_cedula).first()

    @staticmethod
    def actualizar(asistente_id, nuevos_datos):
        doctor = Asistente.query.get(asistente_id)
        if not doctor:
            return None
        for clave, valor in nuevos_datos.items():
            setattr(doctor, clave, valor)
        db.session.commit()
        return doctor

    @staticmethod
    def eliminar(asistente_id):
        doctor = Asistente.query.get(asistente_id)
        if doctor:
            db.session.delete(doctor)
            db.session.commit()
            return True
        return False
