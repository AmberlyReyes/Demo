from flask import flash, render_template, request, redirect, url_for, jsonify, current_app, send_from_directory, abort
from sisdental import db
from sisdental.controladores.PacienteControlador import PacienteControlador
from sisdental.controladores.citaControlador import citaControlador
from sisdental.controladores.ConsultaControlador import ConsultaControlador
from sisdental.controladores.usuarioControlador import UsuarioControlador
from sisdental.controladores.PersonaControlador import PersonaControlador
from sisdental.controladores.DoctorControlador import DoctorControlador
from sisdental.controladores.HistorialControlador import HistorialControlador
from sisdental.controladores.TratamientoControlador import TratamientoControlador
from sisdental.controladores.PlanTratamientoControlador import PlanTratamientoControlador
from sisdental.controladores.FacturacionControlador import FacturacionControlador
from sisdental.controladores.AsistenteControlador import AsistenteControlador
from sisdental.modelos.Factura import Factura
from sisdental.modelos.PlanTratamiento import PlanTratamiento
from sisdental.modelos.Pago import Pago
from sisdental.modelos import Persona
from datetime import datetime
from sisdental.modelos.Doctor import Doctor
from sisdental.modelos.Usuario import Usuario
from sisdental.modelos.Cuota import Cuota
from sisdental.modelos.Paciente import Paciente
from datetime import date, timedelta
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import extract, or_, func, cast, String
from sisdental.modelos.ArchivoHistorial import ArchivoHistorial
import os
from werkzeug.utils import secure_filename
from functools import wraps
from sisdental.modelos.Paciente import Paciente
import calendar
import locale
from datetime import date

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def register_routes(app):

    @app.route('/')
    @login_required
    def mainpage():
        
        fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
        try:
            fecha_seleccionada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_seleccionada = date.today()

        matriz_mes = calendar.monthcalendar(fecha_seleccionada.year, fecha_seleccionada.month)
        citas_del_mes = citaControlador.obtener_por_mes_y_ano(fecha_seleccionada.month, fecha_seleccionada.year)
        dias_con_citas = {cita.fecha.day for cita in citas_del_mes}

        citas_del_dia_seleccionado = citaControlador.obtener_por_fecha(fecha=fecha_seleccionada).all()

        citas_hoy_num = citaControlador.obtener_por_fecha(fecha=date.today()).count() 
        facturas_pendientes = Factura.query.filter(Factura.estado == 'Pendiente').all()
        
        # Calcular ganancias solo del mes actual
        hoy = date.today()
        ganancias = db.session.query(func.sum(Pago.monto)).filter(
            extract('month', Pago.fecha_pago) == hoy.month,
            extract('year', Pago.fecha_pago) == hoy.year
        ).scalar() or 0
        
        mes_anterior = (fecha_seleccionada.replace(day=1) - timedelta(days=1))
        mes_siguiente = (fecha_seleccionada.replace(day=28) + timedelta(days=4)).replace(day=1)

        return render_template('mainpage.html',
            user=current_user,
            matriz_mes=matriz_mes,
            hoy=fecha_seleccionada,
            mes_actual_nombre=fecha_seleccionada.strftime('%B').capitalize(),
            ano_actual=fecha_seleccionada.year,
            dias_con_citas=dias_con_citas,
            citas_del_dia=citas_del_dia_seleccionado, 
            citas_hoy=citas_hoy_num,
            facturas=len(facturas_pendientes),
            faturas_sum=sum(f.total for f in facturas_pendientes),
            ganancias=ganancias,
            mes_anterior=mes_anterior,
            mes_siguiente=mes_siguiente
        )


        
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.administrador:
                flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
                return redirect(url_for('mainpage'))
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        return render_template('adminDashboard.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('mainpage'))

        user = None

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
        
            user = Usuario.query.filter_by(username=username).first()

            if user is None:
                flash('Usuario no encontrado', 'danger')
                return render_template('login.html')

            # Verificación usando el método check_password
            if user and user.check_password(password):
                login_user(user)
                
                # Redirección según rol
                if user.administrador:
                    return redirect(url_for('mainpage'))
                elif user.doctor:
                    return redirect(url_for('mainpage'))
                elif user.asistente:
                    return redirect(url_for('indexCita'))
                else:
                    return redirect(url_for('mainpage'))  
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
    
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Has cerrado sesión correctamente', 'info')
        return redirect(url_for('mainpage'))

    @app.route('/register', methods=['GET','POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            pwd      = request.form['password']
            conf     = request.form['confirm_password']
            if pwd != conf:
                flash('Las contraseñas no coinciden','danger')
                return redirect(url_for('register'))
            if Usuario.query.filter_by(username=username).first():
                flash('Usuario ya registrado','warning')
                return redirect(url_for('register'))

            # Creación de usuario con hash
            nuevo = Usuario(username=username,
                            administrador=False,
                            doctor=False,
                            asistente=False)
            nuevo.set_password(pwd)
            db.session.add(nuevo)
            db.session.commit()
            flash('Registro exitoso','success')
            return redirect(url_for('login'))

        return render_template('register.html')


    # Listar todos los pacientes
    
    # Listar Citas
    @app.route('/citas')
    def indexCita():
        fecha_str = request.args.get('fecha')
        patient_id = request.args.get('patientId')

        # 1 Si hay patient_id, filtra solo por ese paciente
        # 2 Si también hay fecha, filtra adicionalmente por la fecha
        # 3 Si no hay patient_id, muestra todas las citas
        if patient_id:
            if fecha_str:
                citas = citaControlador.obtener_por_paciente_y_fecha(patient_id, fecha_str)
            else:
                citas = citaControlador.obtener_por_paciente(patient_id)
        else:
            if fecha_str:
                try:
                    citas = citaControlador.obtener_por_fecha(fecha=fecha_str).all()
                except ValueError:
                    flash("Formato de fecha inválido. Use YYYY-MM-DD", 'error')
                    return redirect(url_for('citas/indexCita'))
            else:
                citas = citaControlador.obtener_todos()

        return render_template('citas/indexCita.html', pacientes=citas)
   
    # Crear nuevo paciente
    @app.route('/crear', methods=('GET', 'POST'))
    def crear():
        if request.method == 'GET':
            fecha_maxima = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('pacientes/crear.html', fecha_maxima=fecha_maxima)

        error = None

        if request.method == 'POST':
            data = {
                'nombre': request.form['nombre'],
                'cedula': request.form['cedula'],
                'telefono': request.form['telefono'],
                'direccion': request.form['direccion'],
                'email': request.form['email'],
                'aseguradora': request.form['aseguradora'],
                'num_aseguradora': request.form['num_aseguradora'],
                'nacimiento': request.form['nacimiento']
            }

            # Verificar si la cédula existe
            if PacienteControlador.obtener_por_cedula(data['cedula']):
                error = f"La cédula '{data['cedula']}' ya está registrada."
                return render_template('pacientes/crear.html', error=error)
            
            try:
                PacienteControlador.crear_paciente(data)
            except Exception as e:
                error = f"Error insertando paciente: {e}"
                return render_template('pacientes/crear.html', error=error)

            return redirect(url_for('listar_pacientes'))

        return render_template('pacientes/crear.html', error=error)

    # Crear nuevo Cita
    @app.route('/crearCita', methods=('GET', 'POST'))
    def crearCita():
        error = None
        planes_activos = PlanTratamientoControlador.obtener_todos_activos()
        doctores= DoctorControlador.obtener_todos()

        if request.method == 'POST':
            cedula = request.form['paciente_cedula']
            cedula_limpia = cedula.strip() 
            # 1) Buscar paciente por cédula
            Paci = PacienteControlador.obtener_por_cedula(cedula_limpia)
            if not Paci:
                error = f"No existe paciente con cédula {cedula}"
                return render_template(
                    'citas/crearCita.html',
                    error=error,
                    planes_activos=planes_activos
                )

            doctor_id = request.form['doctor_id']
            plan_id   = request.form.get('plan_tratamiento_id') or None

            data = {
                'paciente_id': Paci.id,
                'doctor_id': doctor_id,
                'fecha': request.form['fecha'],
                'hora': request.form['hora'],
                'plan_tratamiento_id': plan_id
            }

            citaControlador.crear_cita(data)
            return redirect(url_for('indexCita'))

        # GET
        return render_template(
            'citas/crearCita.html',
            error=error,
            planes_activos=planes_activos, 
            doctores=doctores
        )


    @app.route('/<int:id>/editarCita', methods=('GET', 'POST'))
    def editarCita(id):
        cita = citaControlador.obtener_por_id(id)
        if not cita:
            return "Cita no encontrada", 404

        planes_activos = PlanTratamientoControlador.obtener_por_paciente(cita.paciente_id)

        if request.method == 'POST':
            # validar fecha/hora…
            plan_id = request.form.get('plan_tratamiento_id') or None
            nuevos_datos = {
                'fecha': request.form['fecha'],
                'hora': request.form['hora'],
                'plan_tratamiento_id': plan_id,
                'estado': request.form['estado']  # Estado editable
            }
            citaControlador.actualizar_cita(id, nuevos_datos)
            return redirect(url_for('indexCita'))
        
        doctores = DoctorControlador.obtener_todos()

        return render_template(
            'citas/editarCita.html',
            pacientes=cita,
            planes_activos=planes_activos, 
            doctores=doctores,
            docSelected=DoctorControlador.obtener_por_id(cita.doctor_id)
        )

    @app.route('/gestionPaciente')
    def gestion_paciente():
        patient_id = request.args.get('patientId')
        paciente = PacienteControlador.obtener_por_id(patient_id)
        if not paciente:
            return "Paciente no encontrado", 404
        return render_template('pacientes/gestionPaciente.html', paciente=paciente)
    
    # Editar pacientes
    @app.route('/<int:id>/editar', methods=('GET', 'POST'))
    def editar(id):
        paciente = PacienteControlador.obtener_por_id(id)
        if not paciente:
            return "Paciente no encontrado", 404

        if request.method == 'POST':
            nuevos_datos = {
                'nombre': request.form['nombre'],
                'cedula': request.form['cedula'],
                'telefono': request.form['telefono'],
                'direccion': request.form['direccion'],
                'email': request.form['email'],
                'aseguradora': request.form['aseguradora'],
                'num_aseguradora': request.form['num_aseguradora'],
                'nacimiento': request.form['nacimiento']
            }
            PacienteControlador.actualizar_paciente(id, nuevos_datos)
            return redirect(url_for('gestion_paciente',patientId=id))

        return render_template('pacientes/editar.html', pacientes=paciente)

    # Eliminar pacientes
    @app.route('/<int:id>/eliminar', methods=('POST',))
    def eliminar(id):
        PacienteControlador.eliminar_paciente(id)

        return redirect(url_for('index'))
    
    # Eliminar cita
    @app.route('/<int:id>/eliminarCita', methods=('POST',))
    def eliminarCita(id):
        citaControlador.eliminar_paciente(id)
        return redirect(url_for('indexCita'))

    # Detalle de un paciente
    @app.route('/paciente/<identificador>')
    def detalle_paciente(identificador):
        identificador = identificador.strip()
        paciente = None

        # 1) Intentar como ID entero (ignorando guiones)
        numero = identificador.replace('-', '')
        if numero.isdigit():
            paciente = PacienteControlador.obtener_por_id(int(numero))

        # 2) Si no hay paciente o no era numérico, buscar por cédula
        if not paciente:
            paciente = PacienteControlador.obtener_por_cedula(identificador)

        if not paciente:
            return "Paciente no encontrado", 404

        return render_template('pacientes/detalle.html', paciente=paciente)
    
    # Detalle de Cita
    @app.route('/cita/<int:id>')
    def detalle_cita(id):
        paciente = citaControlador.obtener_por_id(id)
        if not paciente:
            return "Cita no encontrada", 404
        return render_template('citas/detalleCita.html', paciente=paciente)
    
    # webControlador.py

    @app.route('/pacientes')
    @login_required
    def listar_pacientes():
        query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        PER_PAGE = 6

    # Asegurarnos de filtrar solo pacientes
        pacientes_query = Paciente.query.filter(Paciente.tipo == 'paciente')

        if query:
            search_term_nombre = f"%{query}%"
            cedula_sin_guiones = query.replace('-', '')
            search_term_cedula = f"%{cedula_sin_guiones}%"
            pacientes_query = pacientes_query.filter(
                or_(
                    Paciente.nombre.ilike(search_term_nombre),
                    func.replace(Paciente.cedula, '-', '').ilike(search_term_cedula)
                )
            )
    
        pacientes_paginados = pacientes_query.order_by(Paciente.nombre).paginate(
            page=page, per_page=PER_PAGE, error_out=False
        )
    
        return render_template('pacientes/listar_pacientes.html', 
                        pacientes_paginados=pacientes_paginados, 
                        search_query=query)

    
    @app.route('/api/paciente/<int:paciente_id>', methods=['GET'])
    def get_paciente_api(paciente_id):
        paciente = PacienteControlador.obtener_por_id(paciente_id)
        if not paciente:
            return {"error": "Paciente no encontrado"}, 404

        return {
            "id": paciente.id,
            "nombre": paciente.nombre,
            "cedula": paciente.cedula,
            "telefono": paciente.telefono,
            "email": paciente.email,
            "direccion": paciente.direccion,
            "aseguradora": paciente.aseguradora,
            "nacimiento": paciente.nacimiento
        }, 200

    @app.route('/nuevaConsulta', methods=['GET'])
    @login_required
    def nueva_consulta():
        patient_id = request.args.get('patientId')
        if not patient_id:
            return "Paciente no especificado", 400

        #  Traer paciente
        paciente = PacienteControlador.obtener_por_id(patient_id)
        if not paciente:
            flash("Paciente no encontrado", "danger")
            return redirect(url_for('gestion_paciente', patientId=patient_id))

        # Traer o crear historial
        historial = HistorialControlador.obtener_por_paciente(patient_id) \
                   or HistorialControlador.crear_historial(patient_id)

        # Última consulta
        consultas = ConsultaControlador.obtener_por_paciente(patient_id)
        if consultas:
            fecha_ultima = consultas[0].fecha.strftime('%Y-%m-%d')
            ultima_id    = consultas[0].id
        else:
            from datetime import date
            fecha_ultima = date.today().strftime('%Y-%m-%d')
            ultima_id    = None

        return render_template(
            'consultas/nuevaConsulta.html',
            paciente=paciente,
            historial=historial,
            ultima_consulta=fecha_ultima,
            ultima_consulta_id=ultima_id
        )

    @app.route('/api/consulta', methods=['POST'])
    def api_crear_consulta():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400

        # Campos obligatorios
        required = ['paciente_id', 'historial_clinico_id', 'doctor_id', 'fecha']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'error': f'Faltan campos: {", ".join(missing)}'}), 400

        # Parseo de fechas
        try:
            fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
            ultima_consulta = (
                datetime.strptime(data['ultima_consulta'], '%Y-%m-%d').date()
                if data.get('ultima_consulta') else None
            )
        except ValueError as e:
            return jsonify({'error': f'Formato de fecha inválido: {e}'}), 400

        consulta_data = {
            'paciente_id': data['paciente_id'],
            'historial_clinico_id': data['historial_clinico_id'],
            'doctor_id': data['doctor_id'],
            'fecha': fecha,
            'presion_arterial': data.get('presion_arterial'),
            'ultima_consulta': ultima_consulta,
            'diagnostico': data.get('diagnostico'),
            'notas': data.get('notas'),
        }

        try:
            nueva_consulta = ConsultaControlador.crear_consulta(consulta_data)
            return jsonify({
                'success': True,
                'consulta_id': nueva_consulta.id
            }), 201

        except Exception as e:
            error_msg = f'Ocurrió un error al guardar la consulta: {e}'
            return jsonify({'error': error_msg}), 500

   
    @app.route('/uploads/<path:filename>')
    @login_required
    def ver_archivo(filename):
        """Sirve los archivos desde la carpeta UPLOAD_FOLDER."""
        upload_folder = current_app.config['UPLOAD_FOLDER']
        return send_from_directory(upload_folder, filename)
    

    @app.route('/consulta/<int:consulta_id>', methods=['GET'])
    def ver_consulta(consulta_id):
        consulta = ConsultaControlador.obtener_por_id(consulta_id)
        if not consulta:
            return "Consulta no encontrada", 404
        return render_template('consultas/verConsulta.html', consulta=consulta)
    
    @app.route('/calendario')
    @login_required
    def calendario():

        data = procesar_calendario()
        return render_template('calendario.html', 
                               citas=data.get('citas'),
                               fecha_mostrada=data.get('fecha_mostrada'),
                               fecha_anterior=data.get('fecha_anterior'),
                               fecha_siguiente=data.get('fecha_siguiente'))

    def procesar_calendario():
        # Obtener la fecha de la URL, si no se provee, usar la fecha de hoy.
        fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
        
        try:
            fecha_seleccionada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Formato de fecha inválido. Usando fecha de hoy.", 'warning')
            fecha_seleccionada = date.today()

        citas_del_dia = citaControlador.obtener_por_fecha(fecha=fecha_seleccionada).all()

        fecha_anterior = (fecha_seleccionada - timedelta(days=1)).strftime('%Y-%m-%d')
        fecha_siguiente = (fecha_seleccionada + timedelta(days=1)).strftime('%Y-%m-%d')

        data = {
            'citas': citas_del_dia,
            'fecha_mostrada': fecha_seleccionada,
            'fecha_anterior': fecha_anterior,
            'fecha_siguiente': fecha_siguiente
        }
        return data


    @app.route('/historial/<int:historial_id>/update', methods=['POST'])
    def actualizar_historial(historial_id):
        antecedentes = request.form.get('antecedentes')
        medicacion   = request.form.get('medicacion')
        HistorialControlador.actualizar_historial(historial_id, {
            'antecedentes_familiares': antecedentes,
            'medicacion': medicacion
        })

        # Subida de archivo opcional
        file = request.files.get('file')
        if file and file.filename:
            # 1) Sanitizar nombre
            filename = secure_filename(file.filename)

            # 2) Ruta física donde se guarda
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            file.save(save_path)

            # 3) Guardar sólo el filename en BD (file_url será relativo)
            HistorialControlador.guardar_archivo(historial_id, filename, filename)

        return redirect(url_for('historial', patientId=request.form.get('paciente_id')))

    @app.route('/historial/<int:historial_id>/file/<int:file_id>', methods=['DELETE'])
    def delete_file(historial_id, file_id):
        archivo = ArchivoHistorial.query.get(file_id)
        if not archivo:
            return jsonify({'error':'No encontrado'}),404
        try:
            os.remove(archivo.file_url)
        except:
            pass
        db.session.delete(archivo); db.session.commit()
        return jsonify({'success':True})

    #@app.route('/tratamientos')
    @app.route('/admin/tratamientos')
    @login_required
    @admin_required
    def listar_tratamientos():
        tratamientos = TratamientoControlador.obtener_todos()
        
        return render_template('tratamientos/listarTratamiento.html', tratamientos=tratamientos)

    @app.route('/tratamientosCrear', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def crear_tratamiento():
        if request.method == 'POST':
            data = {
                'nombre': request.form['nombre'],
                'descripcion': request.form['descripcion'],
                'costo': float(request.form['costo'])
            }
            TratamientoControlador.crear(data)
            flash('Tratamiento creado con éxito.', 'success')
            return redirect(url_for('listar_tratamientos'))
        return render_template('tratamientos/crearTratamiento.html')
    

    @app.route('/historial', methods=['GET'])
    def historial():
        patient_id = request.args.get('patientId')
        paciente   = PacienteControlador.obtener_por_id(patient_id)
        if not paciente:
            return "Paciente no encontrado", 404

        historial = HistorialControlador.obtener_por_paciente(patient_id) \
                or HistorialControlador.crear_historial(patient_id)

        consultas = ConsultaControlador.obtener_por_paciente(patient_id)
        archivos = HistorialControlador.listar_archivos(historial.id)

        
        # Obtenemos el ID de la consulta a resaltar desde la URL.
        last_consulta_id_str = request.args.get('last_consulta_id')
        last_consulta_id = int(last_consulta_id_str) if last_consulta_id_str else None

        return render_template(
            'historialPaciente.html',
            paciente=paciente,
            historial=historial,
            consultas=consultas,
            archivos=archivos,
            # Pasamos el ID a la plantilla.
            last_consulta_id=last_consulta_id
        )
        

    @app.route('/paciente/<int:paciente_id>/planes')
    @login_required
    def listar_planes_paciente(paciente_id):
        paciente = PacienteControlador.obtener_por_id(paciente_id)
        planes=PlanTratamientoControlador.obtener_por_paciente(paciente_id)
        return render_template('planes/listar_planes.html', paciente=paciente, planes=planes)

    @app.route('/paciente/<int:paciente_id>/planes/crear', methods=['GET','POST'])
    @login_required
    def crear_plan_paciente(paciente_id):
        if request.method == 'POST':
            nombre_plan   = request.form['nombre_plan']
            doctor_id     = int(request.form['doctor_id'])
            fecha_inicio  = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date()
            numero_cuotas = int(request.form['numero_cuotas'])
            ids        = request.form.getlist('detalle_tratamiento_id')
            costos     = request.form.getlist('detalle_costo')
            cantidades = request.form.getlist('detalle_cantidad')
            detalles = [
                {'tratamiento_id': int(tid), 'costo': float(c), 'cantidad': int(q)}
                for tid, c, q in zip(ids, costos, cantidades)
            ]

            # VALIDACIÓN: Debe haber al menos un tratamiento
            if not detalles or len(detalles) == 0:
                flash('Debes agregar al menos un tratamiento al plan.', 'danger')
                return redirect(request.url)

            data = {
                'paciente_id': paciente_id,
                'doctor_id': doctor_id,
                'nombre_plan': nombre_plan,
                'fecha_inicio': fecha_inicio,
                'numero_cuotas': numero_cuotas,
                'detalles': detalles
            }
            plan = PlanTratamientoControlador.crear_plan_completo(data)
            flash('Plan creado.' if plan else 'Error al crear plan', 'success' if plan else 'danger')
            return redirect(url_for('listar_planes_paciente', paciente_id=paciente_id))

        paciente     = PacienteControlador.obtener_por_id(paciente_id)
        tratamientos = TratamientoControlador.obtener_todos()
        doctores     = DoctorControlador.obtener_todos()
        return render_template(
            'planes/crear_plan.html',
            paciente=paciente,
            tratamientos=tratamientos,
            doctores=doctores
        )


    @app.route('/paciente/<int:paciente_id>/planes/<int:plan_id>/eliminar', methods=['POST'])
    @login_required
    def eliminar_plan_paciente(paciente_id, plan_id):
        if PlanTratamientoControlador.eliminar_plan(plan_id):
            flash('Plan de tratamiento eliminado correctamente.', 'success')
        else:
            flash('Error al eliminar el plan de tratamiento.', 'danger')
        return redirect(url_for('listar_planes_paciente', paciente_id=paciente_id))
    
    @app.route('/paciente/<int:paciente_id>/planes/<int:plan_id>')
    @login_required
    def ver_plan_paciente(paciente_id, plan_id):
        plan = PlanTratamientoControlador.obtener_por_id(plan_id)
        if not plan:
            abort(404)

        balance = PlanTratamientoControlador.calcular_balance(plan_id)
        total_pagado = balance["total_pagado"]
        saldo_pendiente = balance["saldo_pendiente"]

        return render_template(
            'planes/ver_plan.html',
            plan=plan,
            total_pagado=total_pagado,
            saldo_pendiente=saldo_pendiente
        )
    
    @app.route('/admin/tratamientos/<int:id>/editar', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def editar_tratamiento(id):
        """Muestra el formulario para editar un tratamiento y procesa los cambios."""
        tratamiento = TratamientoControlador.obtener_por_id(id)
        if not tratamiento:
            flash("Tratamiento no encontrado.", "danger")
            return redirect(url_for('listar_tratamientos'))

        if request.method == 'POST':
            data = {
                'nombre': request.form['nombre'],
                'descripcion': request.form['descripcion'],
                'costo': float(request.form['costo'])
            }
            TratamientoControlador.actualizar(id, data)
            flash('Tratamiento actualizado con éxito.', 'success')
            return redirect(url_for('listar_tratamientos'))

        return render_template('tratamientos/editarTratamiento.html', tratamiento=tratamiento)

    @app.route('/admin/tratamientos/<int:id>/eliminar', methods=['POST'])
    @login_required
    @admin_required
    def eliminar_tratamiento(id):
        
        if TratamientoControlador.eliminar(id):
            flash('Tratamiento eliminado correctamente.', 'success')
        else:
            flash('Error al eliminar el tratamiento.', 'danger')
        return redirect(url_for('listar_tratamientos'))
    
    @app.route('/admin/usuarios')
    @login_required
    @admin_required
    def listar_usuarios():
        usuarios = UsuarioControlador.obtener_todos()
        return render_template('usuarios/listar_usuarios.html', usuarios=usuarios)

    @app.route('/admin/usuarios/crear', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def crear_usuario():
        if request.method == 'POST':
            # Lógica para crear el usuario
            nuevo_usuario = Usuario(
                username=request.form['username'],
                persona_id=request.form.get('persona_id') or None,
                administrador='administrador' in request.form,
                doctor='doctor' in request.form,
                asistente='asistente' in request.form
                 #return redirect(url_for('listar_usuarios'))
            )

            nuevo_usuario.set_password(request.form['password'])
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Usuario creado con éxito.', 'success')
            return redirect(url_for('listar_usuarios'))

        # GET: obtenemos el ID de la persona si viene por query param
        persona_vinculada = request.args.get('persona_id', type=int)

        # Listar personas sin usuario y que no sean pacientes
        personas_sin_usuario = Persona.query.filter(
            Persona.usuario == None,
            Persona.tipo != 'paciente'
        ).all()

        return render_template(
            'usuarios/crear_editarU.html',
            usuario=None,  
            personas=personas_sin_usuario,
            persona_a_vincular_id=persona_vinculada
        )
    


    @app.route('/admin/usuarios/<int:id>/editar', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def editar_usuario(id):
        usuario = UsuarioControlador.obtener_por_id(id)
        if not usuario:
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('listar_usuarios'))

        if request.method == 'POST':
            # Lógica para actualizar el usuario
            usuario.username = request.form['username']
            usuario.persona_id = request.form.get('persona_id') or None
            usuario.administrador = 'administrador' in request.form
            usuario.doctor = 'doctor' in request.form
            usuario.asistente = 'asistente' in request.form

            # Opcional: actualizar contraseña si se cambió
            if request.form.get('password'):
                usuario.set_password(request.form['password'])
            
            db.session.commit()
            flash('Usuario actualizado con éxito.', 'success')
            return redirect(url_for('listar_usuarios'))

        personas_sin_usuario = Persona.query.filter(Persona.usuario == None).all()
        return render_template('usuarios/crear_editarU.html', usuario=usuario, personas=personas_sin_usuario)


    @app.route('/admin/usuarios/<int:id>/eliminar', methods=['POST'])
    @login_required
    @admin_required
    def eliminar_usuario(id):
        # Evitar que un admin se elimine a sí mismo
        if id == current_user.id:
            flash('No puedes eliminar tu propia cuenta de administrador.', 'danger')
            return redirect(url_for('listar_usuarios'))
        

        
        UsuarioControlador.eliminar_usuario(id)
        flash('Usuario eliminado con éxito.', 'info')
        return redirect(url_for('listar_usuarios'))
    
    @app.route('/admin/personas')
    @login_required
    @admin_required
    def listar_personas():
        # Esta simple consulta obtiene todas las personas gracias a la herencia
        todas_las_personas = Persona.query.order_by(Persona.nombre).all()
        return render_template('personas/listar_personas.html', personas=todas_las_personas)

    @app.route('/admin/personas/crear', methods=['GET','POST'])
    @login_required
    @admin_required
    def crear_persona():
        if request.method == 'POST':
            tipo = request.form['tipo']
            data = {
                'nombre':   request.form['nombre'],
                'cedula':   request.form['cedula'],
                'telefono': request.form['telefono'],
                'direccion':request.form['direccion'],
                'email':    request.form['email'],
            }
            #PersonaControlador.crear_persona(data)
            #person = PersonaControlador.obtener_por_cedula(data['cedula'])

            if tipo == 'paciente':
                PacienteControlador.crear_paciente(data)
            elif tipo == 'doctor':
                DoctorControlador.crear_doctor(data)
            elif tipo == 'asistente':
                AsistenteControlador.crear(data)

            flash('Persona creada.', 'success')

            return redirect(url_for('listar_personas'))
        return render_template('personas/crear_persona.html')

    @app.route('/admin/personas/<int:id>/editar', methods=['GET','POST'])
    @login_required
    @admin_required
    def editar_persona(id):
        persona = PersonaControlador.obtener_por_id(id)
        if not persona:
            flash('Persona no encontrada.', 'danger')
            return redirect(url_for('listar_personas'))
        if request.method == 'POST':
            datos = {
                'nombre':   request.form['nombre'],
                'cedula':   request.form['cedula'],
                'telefono': request.form['telefono'],
                'direccion':request.form['direccion'],
                'email':    request.form['email'],
                'tipo':     request.form['tipo']
            }
            PersonaControlador.actualizar_persona(id, datos)
            flash('Persona actualizada.', 'success')
            return redirect(url_for('listar_personas'))
        return render_template('personas/editar_persona.html', persona=persona)

    @app.route('/admin/personas/<int:id>/eliminar', methods=['POST'])
    @login_required
    @admin_required
    def eliminar_persona(id):

        persona = PersonaControlador.obtener_por_id(id)
        if persona is Paciente:
            #Manejar borrado de tratamientos y planes
            flash('No puedes eliminar un paciente directamente. Usa el módulo de pacientes.', 'danger')
        
        PersonaControlador.eliminar_persona(id)
        flash('Persona eliminada.', 'info')
        return redirect(url_for('listar_personas'))


    @app.route('/factura/<int:factura_id>/registrar_pago', methods=['POST'])
    @login_required
    def registrar_pago(factura_id):
        factura = db.session.get(Factura, factura_id)
        if not factura:
            flash("Factura no encontrada.", "danger")
            return redirect(url_for('admin_dashboard'))

        monto = float(request.form['monto'])
        fecha_pago_str = request.form['fecha_pago']
        fecha_pago = datetime.strptime(fecha_pago_str, '%Y-%m-%d').date()
        cuota_id = request.form.get('cuota_id', type=int)
        
        # Importar Cuota si no está definido
        from sisdental.modelos.Cuota import Cuota

        # Si se especifica una cuota, usar el registro de pago específico para cuotas
        if cuota_id:
            cuota = db.session.get(Cuota, cuota_id)
            if cuota and cuota.factura_id == factura_id:
                # Usar el controlador de plan para registrar el pago con distribución
                resultado = PlanTratamientoControlador.registrar_pago_cuota(cuota_id, monto, fecha_pago)
                
                if resultado['success']:
                    flash(f"Pago de ${monto:.2f} registrado exitosamente.", "success")
                    # Regresar al plan después del pago de cuota
                    return redirect(url_for('ver_plan_paciente', 
                                          paciente_id=cuota.plan.paciente_id, 
                                          plan_id=cuota.plan_id))
                else:
                    flash(f"Error al registrar el pago: {resultado['error']}", "danger")
                    return redirect(url_for('ver_factura', factura_id=factura_id))
            else:
                flash("Cuota no válida para esta factura.", "danger")
                return redirect(url_for('ver_factura', factura_id=factura_id))
        else:
            # Registro de pago normal para toda la factura
            resultado = FacturacionControlador.registrar_pago(factura_id, monto, fecha_pago)
            
            if resultado['success']:
                flash(f"Pago de ${monto:.2f} registrado exitosamente.", "success")
            else:
                flash(f"Error al registrar el pago: {resultado['error']}", "danger")
        
        # Regresar a la vista de la factura para pagos normales
        return redirect(url_for('ver_factura', factura_id=factura_id))

    @app.route('/factura/<int:factura_id>/comprobante')
    @login_required
    def comprobante_pago(factura_id):
        factura = Factura.query.get_or_404(factura_id)
        
        # Obtener el último pago realizado
        ultimo_pago = factura.pagos.order_by(Pago.fecha_pago.desc()).first()
        if not ultimo_pago:
            flash("No hay pagos registrados para esta factura.", "warning")
            return redirect(url_for('ver_factura', factura_id=factura_id))
        
        # Obtener información del usuario que atendió
        atendido_por = "No disponible"
        if current_user and hasattr(current_user, 'persona'):
            atendido_por = current_user.persona.nombre
        
        return render_template('facturas/comprobante_pago.html',
                             factura=factura,
                             ultimo_pago=ultimo_pago,
                             atendido_por=atendido_por,
                             fecha_hoy=datetime.now().date(),
                             hora_actual=datetime.now().strftime('%H:%M'))

    @app.route('/paciente/<int:paciente_id>/estado-cuenta')
    @login_required # Accesible para admin y asistente
    def estado_cuenta_paciente(paciente_id):
        paciente = PacienteControlador.obtener_por_id(paciente_id)
        if not paciente:
            flash("Paciente no encontrado.", "danger")
            return redirect(url_for('mainpage'))

        facturas = Factura.query.filter_by(paciente_id=paciente_id) \
                                .order_by(Factura.fecha_emision.desc()).all()
        planes   = PlanTratamientoControlador.obtener_por_paciente(paciente_id)

        total_facturado = sum(f.total for f in facturas)
        total_pagado    = sum(p.monto for f in facturas for p in f.pagos)
        balance         = total_facturado - total_pagado

        return render_template('estado_cuenta.html',
                               paciente=paciente,
                               facturas=facturas,
                               planes=planes,
                               total_facturado=total_facturado,
                               total_pagado=total_pagado,
                               balance=balance)
    
    @app.route('/admin/facturas')
    @login_required
    @admin_required
    def listar_facturas():
        query = request.args.get('q', '').strip()
        estado_filtro = request.args.get('estado', '').strip()
        page = request.args.get('page', 1, type=int)
        PER_PAGE = 15

        facturas_query = Factura.query.order_by(Factura.fecha_emision.desc())

        # Filtro por estado
        if estado_filtro:
            facturas_query = facturas_query.filter(Factura.estado == estado_filtro)
        
        # Filtro por búsqueda
        if query:
            facturas_query = facturas_query.join(Factura.paciente).filter(
                (cast(Factura.id, String).ilike(f'%{query}%')) |
                (Persona.nombre.ilike(f'%{query}%'))
            )
        
        facturas_paginadas = facturas_query.paginate(page=page, per_page=PER_PAGE, error_out=False)

        return render_template('facturas/listar_facturas.html', 
                               facturas_paginacion=facturas_paginadas, 
                               query=query,
                               estado_filtro=estado_filtro)
    

    @app.route('/factura/<int:factura_id>')
    @login_required
    def ver_factura(factura_id):
        factura = Factura.query.get_or_404(factura_id)
        cuota_id = request.args.get('cuota_id', type=int)
        
        # Si se especifica una cuota, calcular el saldo pendiente para esa cuota específica
        if cuota_id:
            cuota = db.session.get(Cuota, cuota_id)
            if cuota and cuota.factura_id == factura_id:
                # Calcular cuánto falta por pagar de esa cuota específica
                total_pagado_factura = sum(pago.monto for pago in factura.pagos)
                
                # Obtener todas las cuotas del plan ordenadas
                cuotas_plan = db.session.query(Cuota).filter(
                    Cuota.plan_id == cuota.plan_id
                ).order_by(Cuota.numero_cuota).all()
                
                # Calcular cuánto se debe de la cuota específica
                monto_restante = total_pagado_factura
                saldo_pendiente = cuota.monto
                
                for c in cuotas_plan:
                    if c.numero_cuota < cuota.numero_cuota:
                        if monto_restante >= c.monto:
                            monto_restante -= c.monto
                        else:
                            monto_restante = 0
                    elif c.numero_cuota == cuota.numero_cuota:
                        saldo_pendiente = max(0, cuota.monto - monto_restante)
                        break
                
                cuota_enfoque = cuota
            else:
                # Si la cuota no existe o no pertenece a esta factura, usar cálculo normal
                total_pagado = sum(pago.monto for pago in factura.pagos)
                saldo_pendiente = factura.total - total_pagado
                cuota_enfoque = None
        else:
            # Cálculo normal para toda la factura
            total_pagado = sum(pago.monto for pago in factura.pagos)
            saldo_pendiente = factura.total - total_pagado
            cuota_enfoque = None
        
        total_pagado = sum(pago.monto for pago in factura.pagos)
        now = datetime.now()
        return render_template('facturas/ver_factura.html', 
                            factura=factura,
                            total_pagado=total_pagado,
                            saldo_pendiente=max(0, saldo_pendiente),  # No mostrar negativos
                            cuota_enfoque=cuota_enfoque,
                            now=now)

    
    @app.route('/plan/<int:plan_id>/pagar', methods=['GET', 'POST'])
    @login_required
    def pagar_plan(plan_id):
        plan = PlanTratamientoControlador.obtener_por_id(plan_id)
        if not plan:
            abort(404)

        if request.method == 'POST':
            # Procesaremos los pagos aquí en el futuro
            flash("Funcionalidad de procesamiento de pago múltiple en desarrollo.", "info")
            return redirect(url_for('ver_plan_paciente', paciente_id=plan.paciente_id, plan_id=plan.id))
        
        # Obtenemos solo las cuotas que no están completamente pagadas
        cuotas_pendientes = Cuota.query.filter(
            Cuota.plan_id == plan_id,
            Cuota.estado != 'Pagada'
        ).order_by(Cuota.fecha_vencimiento).all()

        return render_template('planes/pagar_plan.html', plan=plan, cuotas=cuotas_pendientes)
    # En webControlador.py

    @app.route('/planes-activos')
    @login_required
    def listar_planes_activos():
        page = request.args.get('page', 1, type=int)
        PER_PAGE = 10

        # Query sólo activos, ordenados por creación descendente
        from sisdental.modelos.PlanTratamiento import PlanTratamiento
        planes_query = PlanTratamiento.query.filter(
            PlanTratamiento.estado == 'Activo'
        ).order_by(PlanTratamiento.id.desc())

        planes_paginados = planes_query.paginate(
            page=page, per_page=PER_PAGE, error_out=False
        )

        return render_template(
            'planes/listar_planes_activos.html',
            planes_paginados=planes_paginados
        )

    @app.route('/cuota/<int:cuota_id>/facturar', methods=['GET'])
    @login_required
    def facturar_cuota(cuota_id):
        cuota = db.session.get(Cuota, cuota_id)
        if not cuota:
            flash("Cuota no encontrada.", "danger")
            return redirect(url_for('listar_planes_activos'))

        # Obtener la factura única del plan
        factura = FacturacionControlador.obtener_factura_del_plan(cuota.plan_id)
        if not factura:
            flash("No se encontró la factura del plan.", "danger")
            return redirect(url_for('listar_planes_activos'))

        flash(f"Redirigiendo a la factura del plan para registrar el pago de la cuota #{cuota.numero_cuota}.", "info")
        return redirect(url_for('ver_factura', factura_id=factura.id, cuota_id=cuota_id))

    @app.route('/paciente/<int:paciente_id>/planes/<int:plan_id>/editar', methods=['GET','POST'])
    @login_required
    def editar_plan_paciente(paciente_id, plan_id):
        plan = PlanTratamientoControlador.obtener_por_id(plan_id)
        if not plan:
            flash('Plan no encontrado.', 'danger')
            return redirect(url_for('listar_planes_paciente', paciente_id=paciente_id))
        
        if request.method == 'POST':
            # Solo actualizar campos básicos del plan
            datos = {
                'nombre_plan': request.form['nombre_plan'],
                'doctor_id': int(request.form['doctor_id']),
                'fecha_inicio': datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date(),
                'numero_cuotas': int(request.form['numero_cuotas']),
                'estado': request.form['estado']
            }
            
            plan_actualizado = PlanTratamientoControlador.actualizar_plan(plan_id, datos)
            if plan_actualizado:
                flash('Plan actualizado correctamente.', 'success')
            else:
                flash('Error al actualizar el plan.', 'danger')
            
            return redirect(url_for('listar_planes_paciente', paciente_id=paciente_id))

        return render_template(
            'planes/editar_plan.html',
            paciente_id=paciente_id,
            plan=plan,
            doctores=DoctorControlador.obtener_todos(),
            tratamientos=TratamientoControlador.obtener_todos()
        )

    @app.route('/admin/reportes/ingresos')
    @login_required
    @admin_required
    def reporte_ingresos():
            """Muestra un reporte de ingresos del mes actual con un gráfico y una tabla."""
            hoy = date.today()
            
            
            pagos_del_mes = Pago.query.filter(
                extract('month', Pago.fecha_pago) == hoy.month,
                extract('year', Pago.fecha_pago) == hoy.year
            ).order_by(Pago.fecha_pago.desc()).all()

            
            chart_data = {}
            for pago in pagos_del_mes:
                dia = pago.fecha_pago.day
                
                chart_data[dia] = chart_data.get(dia, 0) + pago.monto
            
           
            sorted_chart_data = sorted(chart_data.items())
            
            
            chart_labels = [f"Día {dia}" for dia, monto in sorted_chart_data]
            chart_values = [monto for dia, monto in sorted_chart_data]

            return render_template('reporte_ingresos.html',
                                pagos=pagos_del_mes,
                                chart_labels=chart_labels,
                                chart_values=chart_values,
                                mes_actual=hoy.strftime('%B').capitalize())

    @app.route('/api/paciente/por_cedula')
    def api_paciente_por_cedula():
        cedula = request.args.get('cedula','').strip()
        paciente = PacienteControlador.obtener_por_cedula(cedula)
        if not paciente:
            return jsonify({'error':'Paciente no encontrado'}), 404
        return jsonify({'id': paciente.id})

    @app.route('/api/paciente/<int:paciente_id>/planes', methods=['GET'])
    @login_required
    def api_planes_paciente(paciente_id):
        planes = PlanTratamientoControlador.obtener_por_paciente(paciente_id)
        return jsonify([{'id': p.id, 'nombre_plan': p.nombre_plan} for p in planes])
    

    @app.route('/plan/<int:plan_id>/facturar', methods=['GET'])
    @login_required
    def facturar_plan(plan_id):
        """
        Redirige a la factura asociada al plan.
        """
        plan = PlanTratamiento.query.get(plan_id)
        if not plan or not plan.factura:
            flash('El plan no tiene una factura asociada.', 'warning')
            return redirect(url_for('listar_planes_activos'))

        return redirect(url_for('ver_factura', factura_id=plan.factura.id))

    @app.route('/plan/<int:plan_id>/imprimir/<tipo>')
    @login_required
    def imprimir_plan(plan_id, tipo):
        """
        Genera una vista de impresión del plan de tratamiento.
        Tipos: 'completo' (con precios) o 'simple' (sin precios)
        """
        from datetime import datetime
        
        plan = PlanTratamiento.query.get_or_404(plan_id)
        
        # Calcular totales y balance
        balance = PlanTratamientoControlador.calcular_balance(plan_id)
        total_pagado = balance['total_pagado']
        saldo_pendiente = balance['saldo_pendiente']
        
        # Verificar el tipo de impresión
        if tipo not in ['completo', 'simple']:
            flash('Tipo de impresión no válido.', 'error')
            return redirect(url_for('ver_plan_paciente', 
                                  paciente_id=plan.paciente_id, 
                                  plan_id=plan_id))
        
        # Usar un solo template con parámetro para incluir precios
        incluir_precios = (tipo == 'completo')
        
        return render_template('planes/imprimir_plan.html',
                             plan=plan,
                             total_pagado=total_pagado,
                             saldo_pendiente=saldo_pendiente,
                             fecha_actual=datetime.now(),
                             incluir_precios=incluir_precios)