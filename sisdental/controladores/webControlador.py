from flask import flash, render_template, request, redirect, url_for, jsonify, current_app
from sisdental import db
from sisdental.controladores.PacienteControlador import PacienteControlador
from sisdental.controladores.citaControlador import citaControlador
from sisdental.controladores.ConsultaControlador import ConsultaControlador
from sisdental.controladores.usuarioControlador import UsuarioControlador
from sisdental.controladores.DoctorControlador import DoctorControlador
from sisdental.controladores.HistorialControlador import HistorialControlador
from sisdental.controladores.TratamientoControlador import TratamientoControlador
from sisdental.modelos import Persona
from datetime import datetime
from sisdental.modelos.Doctor import Doctor
from sisdental.modelos.Usuario import Usuario
from datetime import date, timedelta
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import extract
from sisdental.modelos.ArchivoHistorial import ArchivoHistorial
import os
from werkzeug.utils import secure_filename
from functools import wraps


def register_routes(app):
 

    # Ruta principal
    @app.route('/')
    def mainpage():
        return render_template('mainpage.html', user=current_user)
    
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

            # Verificación básica (deberías usar hash en producción)
        if user and user.password == password:
            login_user(user)
            
            # Redirección según rol
            if user.administrador:
                return redirect(url_for('mainpage'))
            elif user.doctor:
                return redirect(url_for('index'))
            elif user.asistente:
                return redirect(url_for('indexCita'))
            else:
                return redirect(url_for('mainpage'))  # Redirigir a una página por defecto si no es admin, doctor o asistente
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Has cerrado sesión correctamente', 'info')
        return redirect(url_for('mainpage'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            nombre = request.form.get('nombre')
            email = request.form.get('email')

            # Validaciones básicas
            if password != confirm_password:
                flash('Las contraseñas no coinciden', 'danger')
                return redirect(url_for('register'))

            if Usuario.query.filter_by(username=username).first():
                flash('Este nombre de usuario ya está en uso', 'danger')
                return redirect(url_for('register'))

            try:
                data = {
                    'username': username,
                    'password': password,  # En producción deberías hashear la contraseña
                    'administrador': False,
                    'doctor': False,
                    'asistente': False,
                }
                print("Datos del usuario:", data)
                UsuarioControlador.crear_usuario(data)
                db.session.commit()
                flash('Registro exitoso. Ahora puedes iniciar sesión', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('Error al registrar el usuario: ' + str(e), 'danger')

        return render_template('register.html')

    # Paciente historial
    @app.route('/historial', methods=['GET'])
    def historial():
        patient_id = request.args.get('patientId')
        paciente = PacienteControlador.obtener_por_id(patient_id)
        if not paciente:
            return "Paciente no encontrado", 404

        # 1) Obtener o crear el historial clínico
        historial = HistorialControlador.obtener_por_paciente(patient_id)
        if not historial:
            historial = HistorialControlador.crear_historial(patient_id)

        # 2) Obtener las consultas para lista de “Consultas”
        consultas = ConsultaControlador.obtener_por_paciente(patient_id)

        # 3) Pasar ambas variables al template
        return render_template(
            'historialPaciente.html',
            paciente=paciente,
            historial=historial,
            consultas=consultas
        )
    
        
    # Listar todos los pacientes
    @app.route('/pacientes')
    def index():
        pacientes = PacienteControlador.obtener_todos()
        return render_template('index.html', pacientes=pacientes)
    
    
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
                    return redirect(url_for('indexCita'))
            else:
                citas = citaControlador.obtener_todos()

        return render_template('indexCita.html', pacientes=citas)
   

    # Crear nuevo paciente
    @app.route('/crear', methods=('GET', 'POST'))
    def crear():
        if request.method == 'GET':
            fecha_maxima = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('crear.html', fecha_maxima=fecha_maxima)

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
                return render_template('crear.html', error=error)
            
            try:
                PacienteControlador.crear_paciente(data)
            except Exception as e:
                error = f"Error insertando paciente: {e}"
                return render_template('crear.html', error=error)

            return redirect(url_for('index'))

        return render_template('crear.html', error=error)

    # Crear nuevo Cita
    @app.route('/crearCita', methods=('GET', 'POST'))
    def crearCita():
        error = None

        if request.method == 'POST':
            try:
                # 1. Verificar que el paciente existe
                Paci = PacienteControlador.obtener_por_cedula(request.form['paciente_cedula'])
                if not Paci:
                    error = "El paciente no existe"
                    return render_template('crearCita.html', error=error)

                # 2. Verificar que el doctor existe
                doctor_id = request.form['doctor_id']
                doctor = DoctorControlador.obtener_por_id(doctor_id)  # Necesitarás implementar este método
                if not doctor:
                    error = "El doctor especificado no existe"
                    return render_template('crearCita.html', error=error)

                # Preparar datos de la cita
                data = {
                    'paciente_id': Paci.id,
                    'doctor_id': doctor_id,
                    'fecha': request.form['fecha'],
                    'hora': request.form['hora'],
                }

                # 3. Verificar disponibilidad del doctor (fecha y hora única)
                if citaControlador.check_cita_doctor(data['doctor_id'], data['fecha'], data['hora']):
                    error = "El doctor ya tiene una cita programada en esa fecha y hora"
                    return render_template('crearCita.html', error=error)

                # 4. Verificar que el paciente no tenga otra cita a la misma hora
                if citaControlador.check_cita_paciente(data['paciente_id'], data['fecha'], data['hora']):
                    error = "El paciente ya tiene una cita programada en esa fecha y hora"
                    return render_template('crearCita.html', error=error)

                # Si pasa todas las validaciones, crear la cita
                citaControlador.crear_cita(data)
                return redirect(url_for('indexCita'))

            except Exception as e:
                error = f"Error al procesar la cita: {str(e)}"
                return render_template('crearCita.html', error=error)

        return render_template('crearCita.html', error=error)

    @app.route('/gestionPaciente')
    def gestion_paciente():
        patient_id = request.args.get('patientId')
        paciente = PacienteControlador.obtener_por_id(patient_id)
        if not paciente:
            return "Paciente no encontrado", 404
        return render_template('gestionPaciente.html', paciente=paciente)
    
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

        return render_template('editar.html', pacientes=paciente)

    # Editar Cita
    @app.route('/<int:id>/editarCita', methods=('GET', 'POST'))
    def editarCita(id):
        paciente = citaControlador.obtener_por_id(id)
        if not paciente:
            return "Cita no encontrado", 404

        if request.method == 'POST':
            fecha_original = request.form['fecha']  # Ej. "31/01/2025"
            # Separa por '/'
            dia, mes, anio = fecha_original.split('/')

            # Ajusta al formato "YYYY-MM-DD" (si es el que usas en DB)
            fecha_formateada = f"{anio}-{mes}-{dia}"

            # Convierte la hora en objeto time
            hora_str = request.form['hora']  # Ej. "13:30"
            hora_python = datetime.strptime(hora_str, '%H:%M').time()
            hora_formateada = hora_python.strftime("%H:%M")

            nuevos_datos = {
                'paciente_cedula': request.form['paciente_cedula'],
                'doctor_id': request.form['doctor_id'],
                'fecha': fecha_formateada,  # Ahora en "YYYY-MM-DD"
                'hora': hora_formateada
            }
            citaControlador.actualizar_cita(id, nuevos_datos)
            return redirect(url_for('indexCita'))

        return render_template('editarCita.html', pacientes=paciente)

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
    @app.route('/paciente/<int:id>')
    def detalle_paciente(id):
        paciente = PacienteControlador.obtener_por_id(id)
        if not paciente:
            return "Paciente no encontrado", 404
        return render_template('detalle.html', paciente=paciente)
    
    # Detalle de Cita
    @app.route('/cita/<int:id>')
    def detalle_cita(id):
        paciente = citaControlador.obtener_por_id(id)
        if not paciente:
            return "Cita no encontrada", 404
        return render_template('detalleCita.html', paciente=paciente)

    @app.route('/buscarPaciente', methods=['GET', 'POST'])
    def buscarPaciente():
        if request.method == 'GET':
            # Muestra solo la plantilla vacía
            return render_template('buscarPaciente.html', pacientes=None)

        
        valor = request.form.get('valor', '').strip()
        if not valor:
            
            return render_template('buscarPaciente.html', pacientes=[])

       
        personas = Persona.query.filter(
            (Persona.nombre.ilike(f"%{valor}%") | Persona.cedula.ilike(f"%{valor}%")),
            Persona.tipo == 'paciente'
        ).all()

        return render_template('buscarPaciente.html', pacientes=personas)

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
    def nueva_consulta():
        patient_id = request.args.get('patientId')
        if not patient_id:
            return "Paciente no especificado", 400

        # Obtener lista de consultas ordenada por fecha descendente
        consultas = ConsultaControlador.obtener_por_paciente(patient_id)
        if consultas and len(consultas) > 0:
            fecha_ultima = consultas[0].fecha.strftime('%Y-%m-%d')
            ultima_id   = consultas[0].id
        else:
            from datetime import date
            fecha_ultima = date.today().strftime('%Y-%m-%d')
            ultima_id    = None

        return render_template(
            'nuevaConsulta.html',
            ultima_consulta=fecha_ultima,
            ultima_consulta_id=ultima_id
        )

        


    @app.route('/api/consulta', methods=['POST'])
    def api_crear_consulta():
        data = request.get_json()
        print("Datos recibidos:", data)  # Log de datos recibidos

        if not data:
            error_msg = 'No se enviaron datos'
            print("Error:", error_msg)
            return jsonify({'error': error_msg}), 400

        if 'paciente_id' not in data:
            error_msg = 'Falta paciente_id en los datos'
            print("Error:", error_msg)
            return jsonify({'error': error_msg}), 400

        from sisdental.modelos.HistorialClinico import HistorialClinico

        # Procesar fechas
        try:
            fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date() if data.get('fecha') else None
            ultima_consulta = datetime.strptime(data['ultima_consulta'], '%Y-%m-%d').date() if data.get('ultima_consulta') else None
        except Exception as exc:
            error_msg = f'Formato de fecha inválido: {exc}'
            print("Error:", error_msg)
            return jsonify({'error': error_msg}), 400

        # Buscar o crear el Historial
        historial = HistorialClinico.query.filter_by(paciente_id=data['paciente_id']).first()
        if not historial:
            historial = HistorialClinico(paciente_id=data['paciente_id'])
            db.session.add(historial)
            db.session.commit()
            print("Historial clínico creado con id:", historial.id)
        else:
            print("Historial clínico existente id:", historial.id)

        # Usar la cédula del doctor para la prueba
        doctor = Doctor.query.filter_by(cedula='402-12345678').first()
        if not doctor:
            error_msg = 'El doctor con cédula tal no existe'
            print("Error:", error_msg)
            return jsonify({'error': error_msg}), 400

        consulta_data = {
            'paciente_id': data['paciente_id'],
            'historial_clinico_id': historial.id,
            'doctor_id': doctor.id,
            'fecha': fecha,
            'presion_arterial': data.get('presion_arterial'),
            'ultima_consulta': ultima_consulta,
            'diagnostico': data.get('diagnostico'),
            'notas': data.get('notas'),
        }
       

        try:
            ConsultaControlador.crear_consulta(consulta_data)
            return jsonify({'success': True}), 201
        except Exception as e:
            error_msg = f'Ocurrió un error al guardar la consulta: {e}'
            print("Error:", error_msg)
            return jsonify({'error': error_msg}), 500
        

    @app.route('/consulta/<int:consulta_id>', methods=['GET'])
    def ver_consulta(consulta_id):
        consulta = ConsultaControlador.obtener_por_id(consulta_id)
        if not consulta:
            return "Consulta no encontrada", 404
        return render_template('verConsulta.html', consulta=consulta)
    
    @app.route('/calendario')
    @login_required
    def calendario():
        # Obtener la fecha de la URL, si no se provee, usar la fecha de hoy.
        fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
        
        try:
            # Convertir el string de la fecha a un objeto date de Python
            fecha_seleccionada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Formato de fecha inválido. Usando fecha de hoy.", 'warning')
            fecha_seleccionada = date.today()

        # Usar el controlador para obtener las citas de esa fecha
        citas_del_dia = citaControlador.obtener_por_fecha(fecha=fecha_seleccionada).all()

        # Calcular fechas para los botones "Anterior" y "Siguiente"
        fecha_anterior = (fecha_seleccionada - timedelta(days=1)).strftime('%Y-%m-%d')
        fecha_siguiente = (fecha_seleccionada + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Renderizar la nueva plantilla del calendario
        return render_template('calendario.html', 
                               citas=citas_del_dia, 
                               fecha_mostrada=fecha_seleccionada,
                               fecha_anterior=fecha_anterior,
                               fecha_siguiente=fecha_siguiente)

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
            fn = secure_filename(file.filename)
            folder = current_app.config['UPLOAD_FOLDER']
            path = os.path.join(folder, fn)
            file.save(path)
            nuevo = ArchivoHistorial(historial_clinico_id=historial_id, filename=fn, file_url=path)
            db.session.add(nuevo); db.session.commit()

        # redirigir al historial del paciente
        h = HistorialControlador.obtener_por_paciente(request.form.get('paciente_id'))
        return redirect(url_for('historial', patientId=h.paciente_id))

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

    @app.route('/tratamientos')
    @login_required
    @admin_required
    def listar_tratamientos():
        tratamientos = TratamientoControlador.obtener_todos()
        
        return render_template('listarTratamiento.html', tratamientos=tratamientos)

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
        return render_template('crearTratamiento.html')

