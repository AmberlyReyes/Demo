from sisdental import db
from sisdental.modelos.Factura import Factura
from sisdental.modelos.Pago import Pago
from sisdental.modelos.Cuota import Cuota
from sisdental.modelos.PlanTratamiento import PlanTratamiento

class FacturacionControlador:

    @staticmethod
    def obtener_factura_del_plan(plan_id):
        """
        Obtiene la factura única asociada a un plan de tratamiento.
        """
        factura = Factura.query.filter_by(plan_id=plan_id).first()
        return factura

    @staticmethod
    def actualizar_estado_cuota_por_pago(plan_id):
        """
        Actualiza el estado de las cuotas basado en los pagos realizados.
        """
        plan = PlanTratamiento.query.get(plan_id)
        if not plan:
            return False

        factura = Factura.query.filter_by(plan_id=plan_id).first()
        if not factura:
            return False

        # Calcular total pagado
        total_pagado = sum(p.monto for p in factura.pagos)
        
        # Obtener cuotas ordenadas por fecha de vencimiento
        cuotas = Cuota.query.filter_by(plan_id=plan_id).order_by(Cuota.fecha_vencimiento).all()
        
        monto_restante = total_pagado
        
        try:
            for cuota in cuotas:
                if monto_restante >= cuota.monto:
                    cuota.estado = 'Pagada'
                    monto_restante -= cuota.monto
                elif monto_restante > 0:
                    cuota.estado = 'Parcial'
                    monto_restante = 0
                else:
                    cuota.estado = 'Pendiente'
            
            # Actualizar estado de la factura
            if total_pagado >= factura.total:
                factura.estado = 'Pagada'
            elif total_pagado > 0:
                factura.estado = 'Parcial'
            else:
                factura.estado = 'Pendiente'
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar estado de cuotas: {e}")
            return False

    @staticmethod
    def crear_factura_para_plan(plan_id):
        """
        Crea una factura para un plan de tratamiento.
        """
        plan = PlanTratamiento.query.get(plan_id)
        if not plan:
            print("Error: El plan no existe.")
            return None

        try:
            # Crear la factura asociada al plan
            nueva_factura = Factura(
                paciente_id=plan.paciente_id,
                plan_id=plan.id,
                total=plan.costo_total,
                estado='Pendiente'
            )
            db.session.add(nueva_factura)
            db.session.commit()
            return nueva_factura
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear factura para el plan: {e}")
            return None

    @staticmethod
    def registrar_pago(factura_id, monto, fecha_pago):
        """
        Registra un pago en una factura.
        """
        factura = Factura.query.get(factura_id)
        if not factura:
            return {'success': False, 'error': 'Factura no encontrada.'}

        total_ya_pagado = sum(p.monto for p in factura.pagos)
        saldo_pendiente = round(factura.total - total_ya_pagado, 2)

        if monto > saldo_pendiente:
            return {'success': False, 'error': f"El monto a pagar (${monto}) excede el saldo pendiente (${saldo_pendiente})."}

        if monto <= 0:
            return {'success': False, 'error': 'El monto a pagar debe ser mayor a cero.'}

        try:
            # Crear el registro del pago
            nuevo_pago = Pago(
                factura_id=factura.id,
                monto=monto,
                fecha_pago=fecha_pago
            )
            db.session.add(nuevo_pago)

            # Actualizar el estado de la factura
            total_pagado = total_ya_pagado + monto
            if total_pagado >= factura.total:
                factura.estado = 'Pagada'
            elif total_pagado > 0:
                factura.estado = 'Parcial'

            db.session.commit()
            
            # Actualizar estado de cuotas si la factura pertenece a un plan
            if factura.plan_id:
                FacturacionControlador.actualizar_estado_cuota_por_pago(factura.plan_id)
            
            return {'success': True, 'pago': nuevo_pago}
        except Exception as e:
            db.session.rollback()
            print(f"Error al registrar pago: {e}")
            return {'success': False, 'error': 'Error al registrar el pago.'}