from dateutil.relativedelta import relativedelta
from sisdental import db
from sisdental.modelos.PlanTratamiento import PlanTratamiento
from sisdental.modelos.PlanTratamientoDetalle import PlanTratamientoDetalle
from sisdental.modelos.Cuota import Cuota

class PlanTratamientoControlador:

    @staticmethod
    def crear_plan_completo(data):
        """
        Crea un plan de tratamiento completo con sus detalles y factura asociada.
        """
        try:
            # Crear el plan
            plan = PlanTratamiento(
                paciente_id = data['paciente_id'],
                doctor_id   = data['doctor_id'],
                nombre_plan = data['nombre_plan'],
                fecha_inicio= data['fecha_inicio'],
                numero_cuotas = data['numero_cuotas'],       
                costo_total = sum(d['costo']*d['cantidad'] for d in data['detalles']),
                estado      = 'Activo'
            )
            db.session.add(plan)
            db.session.flush()  
           
            for detalle in data['detalles']:
                db.session.add(PlanTratamientoDetalle(
                    plan_id       = plan.id,
                    tratamiento_id= detalle['tratamiento_id'],
                    costo         = detalle['costo'],
                    cantidad      = detalle['cantidad']
                ))

           
            # Crear la factura única para el plan
            from sisdental.modelos.Factura import Factura
            factura = Factura(
                paciente_id=plan.paciente_id,
                plan_id=plan.id,
                total=plan.costo_total,
                estado='Pendiente'
            )
            db.session.add(factura)
            db.session.flush()  # Para obtener el ID de la factura

            for i in range(1, plan.numero_cuotas+1):
                cuota = Cuota(
                    plan_id        = plan.id,
                    factura_id     = factura.id,  # Todas las cuotas apuntan a la misma factura
                    numero_cuota   = i,
                    monto          = round(plan.costo_total/plan.numero_cuotas, 2),
                    fecha_vencimiento = plan.fecha_inicio + relativedelta(months=i)
                )
                db.session.add(cuota)

            db.session.commit()
            return plan

        except Exception as e:
            db.session.rollback()
            print(f"Error al crear el plan completo: {e}")
            return None

    @staticmethod
    def obtener_por_paciente(paciente_id):
        return PlanTratamiento.query.filter_by(paciente_id=paciente_id).all()

    @staticmethod
    def obtener_por_id(plan_id):
        return db.session.get(PlanTratamiento, plan_id)

    @staticmethod
    def actualizar_plan(plan_id, datos):
        """
        Actualiza los campos básicos de un plan de tratamiento.
        """
        plan = db.session.get(PlanTratamiento, plan_id)
        if not plan:
            return None
        
        try:
            # Solo actualizar los campos básicos
            for k, v in datos.items():
                setattr(plan, k, v)
            
            db.session.commit()
            return plan
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar el plan: {e}")
            return None

    @staticmethod
    def eliminar_plan(plan_id):
        plan = db.session.get(PlanTratamiento, plan_id)
        if not plan:
            return False
        
        try:
            # Primero eliminar la factura asociada y sus pagos (si los hay)
            from sisdental.modelos.Factura import Factura
            from sisdental.modelos.Pago import Pago
            
            factura = db.session.query(Factura).filter(Factura.plan_id == plan_id).first()
            if factura:
                # Eliminar pagos de la factura
                pagos = db.session.query(Pago).filter(Pago.factura_id == factura.id).all()
                for pago in pagos:
                    db.session.delete(pago)
                
                # Eliminar la factura
                db.session.delete(factura)
            
            # Las cuotas y detalles se eliminan automáticamente por cascade
            db.session.delete(plan)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar el plan: {e}")
            return False

    @staticmethod
    def calcular_total_pagado(plan_id):
        """
        Calcula el total pagado en un plan de tratamiento.
        Suma todos los pagos realizados en la factura única del plan.
        """
        from sisdental.modelos.Pago import Pago
        from sisdental.modelos.Factura import Factura

        try:
            # Obtener la factura del plan
            factura = db.session.query(Factura).filter(Factura.plan_id == plan_id).first()
            
            if not factura:
                return 0.0
            
            # Sumar todos los pagos de la factura del plan
            total_pagado = db.session.query(
                db.func.coalesce(db.func.sum(Pago.monto), 0)
            ).filter(
                Pago.factura_id == factura.id
            ).scalar()
            
            return float(total_pagado)
        except Exception as e:
            print(f"Error al calcular el total pagado: {e}")
            return 0.0

    @staticmethod
    def calcular_balance(plan_id):
        """
        Calcula el balance del plan de tratamiento.
        Balance = Costo Total - Total Pagado
        """
        plan = db.session.get(PlanTratamiento, plan_id)
        if not plan:
            return {
                "total_pagado": 0.0,
                "saldo_pendiente": 0.0
            }

        total_pagado = PlanTratamientoControlador.calcular_total_pagado(plan_id)
        saldo_pendiente = plan.costo_total - total_pagado
        
        return {
            "total_pagado": total_pagado,
            "saldo_pendiente": saldo_pendiente
        }

    @staticmethod
    def obtener_todos_activos():
        return PlanTratamiento.query.filter_by(estado='Activo').all()
    
    @staticmethod
    def registrar_pago_cuota(cuota_id, monto, fecha_pago):
        """
        Registra un pago para una cuota específica con distribución inteligente.
        Si el pago excede el monto de la cuota, se distribuye en cuotas restantes.
        """
        try:
            from sisdental.modelos.Pago import Pago
            from sisdental.modelos.Factura import Factura
            
            cuota = db.session.get(Cuota, cuota_id)
            if not cuota:
                return {'success': False, 'error': 'Cuota no encontrada'}
            
            # Obtener la factura del plan
            factura = db.session.get(Factura, cuota.factura_id)
            if not factura:
                return {'success': False, 'error': 'Factura no encontrada'}
            
            # Registrar el pago en la factura
            pago = Pago(
                factura_id=factura.id,
                monto=monto,
                fecha_pago=fecha_pago
            )
            db.session.add(pago)
            
            # Actualizar estados de cuotas basado en pagos totales
            PlanTratamientoControlador._actualizar_estados_cuotas(cuota.plan_id)
            
            # Actualizar estado de la factura
            from sisdental.controladores.FacturacionControlador import FacturacionControlador
            FacturacionControlador._actualizar_estado_factura(factura.id)
            
            db.session.commit()
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al registrar pago de cuota: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _actualizar_estados_cuotas(plan_id):
        """
        Actualiza los estados de todas las cuotas de un plan basado en los pagos realizados.
        """
        try:
            from sisdental.modelos.Pago import Pago
            from sisdental.modelos.Factura import Factura
            
            # Obtener todas las cuotas del plan ordenadas por número
            cuotas = db.session.query(Cuota).filter(
                Cuota.plan_id == plan_id
            ).order_by(Cuota.numero_cuota).all()
            
            if not cuotas:
                return
            
            # Obtener total pagado en la factura del plan
            factura = db.session.query(Factura).filter(Factura.plan_id == plan_id).first()
            if not factura:
                return
                
            total_pagado = db.session.query(
                db.func.coalesce(db.func.sum(Pago.monto), 0)
            ).filter(Pago.factura_id == factura.id).scalar()
            
            # Distribuir el total pagado entre las cuotas en orden
            monto_restante = float(total_pagado)
            
            for cuota in cuotas:
                if monto_restante <= 0:
                    cuota.estado = 'Pendiente'
                elif monto_restante >= cuota.monto:
                    cuota.estado = 'Pagada'
                    monto_restante -= cuota.monto
                else:
                    cuota.estado = 'Parcial'
                    monto_restante = 0
            
        except Exception as e:
            print(f"Error al actualizar estados de cuotas: {e}")

