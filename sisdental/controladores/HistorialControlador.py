from sisdental import db
from sisdental.modelos.HistorialClinico import HistorialClinico

class HistorialControlador:

    @staticmethod
    def obtener_por_paciente(paciente_id):
       
        return HistorialClinico.query.filter_by(paciente_id=paciente_id).first()

    @staticmethod
    def crear_historial(paciente_id):
       
        historial = HistorialClinico(paciente_id=paciente_id)
        db.session.add(historial)
        db.session.commit()
        return historial

    @staticmethod
    def actualizar_historial(historial_id, nuevos_datos):
        
        historial = db.session.get(HistorialClinico, historial_id)
        if not historial:
            return None
        for clave, valor in nuevos_datos.items():
            setattr(historial, clave, valor)
        db.session.commit()
        return historial

    @staticmethod
    def eliminar_historial(historial_id):
       
        historial = db.session.get(HistorialClinico, historial_id)
        if not historial:
            return False
        db.session.delete(historial)