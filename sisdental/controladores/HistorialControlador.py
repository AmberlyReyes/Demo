from sisdental import db
from sisdental.modelos.HistorialClinico import HistorialClinico
from sisdental.modelos.ArchivoHistorial import ArchivoHistorial

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
    def listar_archivos(historial_id):
        return ArchivoHistorial.query.filter_by(historial_clinico_id=historial_id).all()

    @staticmethod
    def guardar_archivo(historial_id, filename, file_url):
        archivo = ArchivoHistorial(
            historial_clinico_id=historial_id,
            filename=filename,
            file_url=file_url
        )
        db.session.add(archivo)
        db.session.commit()
        return archivo

    @staticmethod
    def eliminar_archivo(file_id):
        archivo = db.session.get(ArchivoHistorial, file_id)
        if archivo:
            db.session.delete(archivo)
            db.session.commit()
            return True
        return False