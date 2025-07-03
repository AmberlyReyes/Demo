from flask import flash, render_template, request, redirect, url_for, jsonify
from sisdental import db
from sisdental.controladores.PacienteControlador import PacienteControlador
from sisdental.controladores.citaControlador import citaControlador
from sisdental.controladores.ConsultaControlador import ConsultaControlador
from sisdental.controladores.usuarioControlador import UsuarioControlador
from sisdental.modelos import Persona
from datetime import datetime
from sisdental.modelos.Doctor import Doctor
from sisdental.modelos.Usuario import Usuario
from datetime import date, timedelta
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

def register_routes(app):
 

    # Ruta principal
    @app.route('/')
    def mainpage():
        return render_template('mainpage.html', user=current_user)
    
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
            
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            nombre = request.form['nombre']
            email = request.form['email']

            # Validaciones básicas
            if password != confirm_password:
                flash('Las contraseñas no coinciden', 'danger')
                return redirect(url_for('register'))

            if Usuario.query.filter_by(username=username).first():
                flash('Este nombre de usuario ya está en uso', 'danger')
                return redirect(url_for('register'))

        # Crear usuario

        try:
            data = {
                'username': username,
                'password': password,  # En producción deberías hashear la contraseña
                'administrador': False,  # Por defecto no es admin
                'doctor': False,
                'asistente': False,
            }
            print("Datos del usuario:", data)  # Log de datos recibidos
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
        
        consultas = ConsultaControlador.obtener_por_paciente(patient_id)
        
        return render_template('historialPaciente.html', paciente=paciente, consultas=consultas)
    
        
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
            Paci = PacienteControlador.obtener_por_cedula(request.form['paciente_cedula'])
            data = {
                'paciente_id': Paci.id,
                'doctor_id': request.form['doctor_id'],
                'fecha': request.form['fecha'],
                'hora': request.form['hora'],
            }

            # Verificar si la Cita choca con otra TO-DO
            #if PacienteControlador.obtener_por_cedula(data['cedula']):
            #    error = f"La cédula '{data['cedula']}' ya está registrada."
            #    return render_template('crear.html', error=error)

            try:
                citaControlador.crear_cita(data)
            except Exception as e:
                error = f"Error insertando cita: {e}"
                return render_template('crearCita.html', error=error)

            return redirect(url_for('indexCita'))

        return render_template('crearCita.html', error=error)
    
    #@app.route('/gestionPaciente')
    #def gestion_paciente():
    # return render_template('gestionPaciente.html')
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

        # Buscar la última consulta del paciente
        ultima_consulta = ConsultaControlador.obtener_por_paciente(patient_id)
        if ultima_consulta and len(ultima_consulta) > 0:
            # Tomar la fecha de la última consulta (la más reciente)
            fecha_ultima = ultima_consulta[0].fecha.strftime('%Y-%m-%d')
        else:
            # Si no hay consultas, usar la fecha de hoy
            from datetime import date
            fecha_ultima = date.today().strftime('%Y-%m-%d')

        return render_template('nuevaConsulta.html', ultima_consulta=fecha_ultima)

        


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
            'doctor_id': doctor.id,  # Se asigna el ID del doctor hallado por cédula
            'fecha': fecha,
            'presion_arterial': data.get('presion_arterial'),
            'ultima_consulta': ultima_consulta,
            'diagnostico': data.get('diagnostico'),
            'antecedentes_familiares': data.get('antecedentes_familiares'),
            'medicacion': data.get('medicacion'),
            'notas': data.get('notas'),
        }
        print("Datos a insertar en consulta:", consulta_data)

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

