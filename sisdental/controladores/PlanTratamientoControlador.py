from sisdental import db
from sisdental.modelos.PlanTratamiento import PlanTratamiento
from sisdental.modelos.PlanTratamientoDetalle import PlanTratamientoDetalle
from sisdental.modelos.Cuota import Cuota
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class PlanTratamientoControlador:
    @staticmethod
    def crear_plan_completo(data):
        try:
            # 1. Crear el Plan de Tratamiento principal
            plan = PlanTratamiento(
                paciente_id=data['paciente_id'],
                doctor_id=data['doctor_id'],
                nombre_plan=data['nombre_plan'],
                fecha_inicio=data['fecha_inicio'],
                estado='Activo' # O 'none' si necesita aprobación
            )
            db.session.add(plan)
            db.session.flush() # flush() para obtener el ID del plan antes del commit

            # 2. Añadir los detalles (tratamientos) y calcular costo total
            costo_total_calculado = 0
            for detalle_data in data['detalles']:
                detalle = PlanTratamientoDetalle(
                    plan_id=plan.id,
                    tratamiento_id=detalle_data['tratamiento_id'],
                    cantidad=detalle_data['cantidad'],
                    costo_aplicado=detalle_data['costo']
                )
                costo_total_calculado += detalle_data['costo'] * detalle_data['cantidad']
                db.session.add(detalle)
            
            plan.costo_total = costo_total_calculado
            
            # 3. Generar las cuotas de pago
            if data['numero_cuotas'] > 0:
                monto_cuota = round(costo_total_calculado / data['numero_cuotas'], 2)
                for i in range(data['numero_cuotas']):
                    fecha_vencimiento = data['fecha_inicio'] + relativedelta(months=i)
                    cuota = Cuota(
                        plan_id=plan.id,
                        numero_cuota=i + 1,
                        monto=monto_cuota,
                        fecha_vencimiento=fecha_vencimiento,
                        estado='Pendiente'
                    )
                    db.session.add(cuota)

            db.session.commit()
            return plan

        except Exception as e:
            db.session.rollback()
            print(f"Error creando plan de tratamiento: {e}")
            return None

    @staticmethod
    def obtener_por_paciente(paciente_id):
        return PlanTratamiento.query.filter_by(paciente_id=paciente_id).all()

    @staticmethod
    def obtener_por_id(plan_id):
        return db.session.get(PlanTratamiento, plan_id)

    @staticmethod
    def actualizar_plan(plan_id, datos):
        plan = db.session.get(PlanTratamiento, plan_id)
        if not plan:
            return None
        for k, v in datos.items():
            setattr(plan, k, v)
        db.session.commit()
        return plan

    @staticmethod
    def eliminar_plan(plan_id):
        plan = db.session.get(PlanTratamiento, plan_id)
        if not plan:
            return False
        db.session.delete(plan)
        db.session.commit()
        return True

    @staticmethod
    def calcular_total_pagado(plan_id):
        
       # Suma el monto de todas las cuotas marcadas como 'Pagada' para el plan dado.
        
        from sisdental.modelos.Cuota import Cuota
        total = db.session.query(db.func.sum(Cuota.monto)) \
                 .filter_by(plan_id=plan_id, estado='Pagada') \
                 .scalar()
        return float(total or 0)
    
    @staticmethod
    def obtener_todos_activos():
    
        return PlanTratamiento.query.filter_by(estado='Activo').all()

