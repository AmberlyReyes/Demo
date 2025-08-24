from sisdental import db
#from sisdental.modelos import Paciente
from sisdental.modelos.Paciente import Paciente

class PacienteControlador:

    @staticmethod
    def crear_paciente(data):
        try:
            # Obligatorio para que la fila sea de tipo 'paciente'
            data['tipo'] = 'paciente'
            nuevo = Paciente(**data)
            db.session.add(nuevo)
            db.session.commit()
            return nuevo
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear paciente: {e}")
            return None


    @staticmethod
    def obtener_todos():
        return Paciente.query.all()

    @staticmethod
    def obtener_por_id(paciente_id):
        return Paciente.query.get(paciente_id)
    
    
    @staticmethod
    def obtener_por_cedula(paciente_cedula):
         return Paciente.query.filter_by(cedula=paciente_cedula).first()

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
    
