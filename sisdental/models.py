
import sqlite3
import os

DB_NAME = 'database.db'

def get_db_connection():
    """Obtiene la conexión con la base de datos."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea la tabla 'pacientes' si no existe."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT NOT NULL UNIQUE,
            telefono TEXT,
            direccion TEXT,
            email TEXT,
            aseguradora TEXT,
            num_aseguradora TEXT,
            nacimiento TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_paciente(nombre, cedula, telefono, direccion, email, aseguradora, num_aseguradora, nacimiento):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO pacientes (nombre, cedula, telefono, direccion, email, aseguradora, num_aseguradora, nacimiento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, cedula, telefono, direccion, email, aseguradora, num_aseguradora, nacimiento))
    conn.commit()
    conn.close()

def get_all_pacientes():
    conn = get_db_connection()
    pacientes = conn.execute('SELECT * FROM pacientes').fetchall()
    conn.close()
    return pacientes

def get_paciente_by_id(paciente_id):
    conn = get_db_connection()
    paciente = conn.execute('SELECT * FROM pacientes WHERE id = ?', (paciente_id,)).fetchone()
    conn.close()
    return paciente

def get_paciente_by_cedula(cedula):
    conn = get_db_connection()
    paciente = conn.execute('SELECT * FROM pacientes WHERE cedula = ?', (cedula,)).fetchone()
    conn.close()
    return paciente

def update_paciente(id, nombre, cedula, telefono, direccion, email, aseguradora, num_aseguradora, nacimiento):
    conn = get_db_connection()
    conn.execute('''
        UPDATE pacientes
        SET nombre = ?,
            cedula = ?,
            telefono = ?,
            direccion = ?,
            email = ?,
            aseguradora = ?,
            num_aseguradora = ?,
            nacimiento = ?
        WHERE id = ?
    ''', (nombre, cedula, telefono, direccion, email, aseguradora, num_aseguradora, nacimiento, id))
    conn.commit()
    conn.close()

def delete_paciente(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM pacientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
