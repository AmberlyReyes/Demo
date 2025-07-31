from sisdental import db
from sisdental.modelos.Factura import Factura
from sisdental.modelos.Pago import Pago
from sisdental.modelos.Cuota import Cuota

class FacturacionControlador:

    @staticmethod
    def crear_factura_desde_cuota(cuota_id):
        """
        Crea una factura a partir de una cuota de un plan de tratamiento.
        Retorna la nueva factura o None si hay un error.
        """
        cuota = Cuota.query.get(cuota_id)
        if not cuota or cuota.estado != 'Pendiente':
            print("Error: La cuota no existe o ya no está pendiente.")
            return None

        try:
            nueva_factura = Factura(
                paciente_id=cuota.plan.paciente_id,
                total=cuota.monto,
                estado='Pendiente' # La factura nace pendiente de pago
            )
            db.session.add(nueva_factura)
            db.session.flush() # Para obtener el ID de la factura

            # Vincular la factura a la cuota
            cuota.factura_id = nueva_factura.id
            cuota.estado = 'Facturada' # un estado intermedio

            db.session.commit()
            return nueva_factura
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear factura desde cuota: {e}")
            return None

    @staticmethod
    def registrar_pago(factura_id, monto, fecha_pago):
        factura = Factura.query.get(factura_id)
        if not factura:
            # Devolvemos un mensaje de error específico
            return {'success': False, 'error': 'Factura no encontrada.'}

        total_ya_pagado = sum(p.monto for p in factura.pagos)
        saldo_pendiente = round(factura.total - total_ya_pagado, 2)

        # --- LÓGICA MEJORADA ---
        if monto > saldo_pendiente:
            # En lugar de corregir, devolvemos un error claro.
            error_msg = f"El monto a pagar (${monto}) excede el saldo pendiente (${saldo_pendiente})."
            return {'success': False, 'error': error_msg}

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

            # Actualizar el estado de la factura y la cuota asociada
            total_pagado = total_ya_pagado + monto
            if total_pagado >= factura.total:
                factura.estado = 'Pagada'
                # Si la factura está pagada, la cuota también
                if factura.cuota_asociada:
                    factura.cuota_asociada.estado = 'Pagada'

            db.session.commit()
            return {'success': True, 'pago': nuevo_pago}
        except Exception as e:
            db.session.rollback()
            print(f"Error al registrar pago: {e}")
            return None