from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
DATABASE = 'asistencia_profesores.db'

def init_db():
    """Inicializar la base de datos con las tablas necesarias"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Tabla de profesores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profesores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telefono TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de materias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT
        )
    ''')
    
    # Tabla de cursos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            año INTEGER NOT NULL CHECK (año >= 1 AND año <= 6),
            division TEXT DEFAULT 'A'
        )
    ''')
    
    # Tabla de asignaciones (profesor-materia-curso)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asignaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profesor_id INTEGER,
            materia_id INTEGER,
            curso_id INTEGER,
            FOREIGN KEY (profesor_id) REFERENCES profesores (id),
            FOREIGN KEY (materia_id) REFERENCES materias (id),
            FOREIGN KEY (curso_id) REFERENCES cursos (id)
        )
    ''')
    
    # Tabla de horarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hora_inicio TIME NOT NULL,
            hora_fin TIME NOT NULL,
            descripcion TEXT
        )
    ''')
    
    # Tabla de asistencias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profesor_id INTEGER,
            materia_id INTEGER,
            curso_id INTEGER,
            horario_id INTEGER,
            fecha DATE NOT NULL,
            presente BOOLEAN NOT NULL DEFAULT 1,
            observaciones TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profesor_id) REFERENCES profesores (id),
            FOREIGN KEY (materia_id) REFERENCES materias (id),
            FOREIGN KEY (curso_id) REFERENCES cursos (id),
            FOREIGN KEY (horario_id) REFERENCES horarios (id)
        )
    ''')
    
    # Insertar datos iniciales
    # Horarios predefinidos
    horarios_iniciales = [
        ('08:30:00', '09:30:00', '1ra hora'),
        ('09:30:00', '10:30:00', '2da hora'),
        ('10:30:00', '11:00:00', 'Recreo'),
        ('11:00:00', '12:00:00', '3ra hora'),
        ('12:00:00', '13:00:00', '4ta hora'),
        ('13:00:00', '14:00:00', 'Almuerzo'),
        ('14:00:00', '15:00:00', '5ta hora'),
        ('15:00:00', '16:00:00', '6ta hora')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO horarios (hora_inicio, hora_fin, descripcion)
        VALUES (?, ?, ?)
    ''', horarios_iniciales)
    
    # Cursos (1ro a 6to año)
    for año in range(1, 7):
        cursor.execute('INSERT OR IGNORE INTO cursos (año, division) VALUES (?, ?)', (año, 'A'))
        cursor.execute('INSERT OR IGNORE INTO cursos (año, division) VALUES (?, ?)', (año, 'B'))
    
    # Materias básicas
    materias_iniciales = [
        ('Matemática', 'Matemática general'),
        ('Lengua y Literatura', 'Lengua castellana y literatura'),
        ('Historia', 'Historia argentina y universal'),
        ('Geografía', 'Geografía argentina y mundial'),
        ('Ciencias Naturales', 'Biología, física y química'),
        ('Física', 'Física general'),
        ('Química', 'Química general'),
        ('Biología', 'Biología general'),
        ('Educación Física', 'Educación física y deportes'),
        ('Inglés', 'Idioma inglés'),
        ('Arte', 'Educación artística'),
        ('Música', 'Educación musical'),
        ('Tecnología', 'Educación tecnológica'),
        ('Informática', 'Informática y computación')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO materias (nombre, descripcion)
        VALUES (?, ?)
    ''', materias_iniciales)
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/profesores')
def listar_profesores():
    """Listar todos los profesores"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM profesores ORDER BY apellido, nombre')
    profesores = cursor.fetchall()
    conn.close()
    return render_template('profesores.html', profesores=profesores)

@app.route('/registrar_asistencia')
def registrar_asistencia():
    """Página para registrar asistencia"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Obtener profesores
    cursor.execute('SELECT id, nombre, apellido FROM profesores ORDER BY apellido, nombre')
    profesores = cursor.fetchall()
    
    # Obtener horarios
    cursor.execute('SELECT id, hora_inicio, hora_fin, descripcion FROM horarios ORDER BY hora_inicio')
    horarios = cursor.fetchall()
    
    conn.close()
    return render_template('registrar_asistencia.html', profesores=profesores, horarios=horarios)

@app.route('/api/profesor_asignaciones/<int:profesor_id>')
def obtener_asignaciones_profesor(profesor_id):
    """Obtener las asignaciones (materias y cursos) de un profesor"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.id, m.nombre as materia, c.año, c.division, m.id as materia_id, c.id as curso_id
        FROM asignaciones a
        JOIN materias m ON a.materia_id = m.id
        JOIN cursos c ON a.curso_id = c.id
        WHERE a.profesor_id = ?
        ORDER BY c.año, c.division, m.nombre
    ''', (profesor_id,))
    asignaciones = cursor.fetchall()
    conn.close()
    
    resultado = []
    for asig in asignaciones:
        resultado.append({
            'id': asig[0],
            'materia': asig[1],
            'curso': f"{asig[2]}° {asig[3]}",
            'materia_id': asig[4],
            'curso_id': asig[5]
        })
    
    return jsonify(resultado)

@app.route('/api/registrar_asistencia', methods=['POST'])
def api_registrar_asistencia():
    """API para registrar asistencia"""
    data = request.json
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO asistencias (profesor_id, materia_id, curso_id, horario_id, fecha, presente, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['profesor_id'],
            data['materia_id'],
            data['curso_id'],
            data['horario_id'],
            data['fecha'],
            data.get('presente', True),
            data.get('observaciones', '')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Asistencia registrada correctamente'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/gestionar_profesores')
def gestionar_profesores():
    """Página para gestionar profesores"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Obtener profesores
    cursor.execute('SELECT * FROM profesores ORDER BY apellido, nombre')
    profesores = cursor.fetchall()
    
    # Obtener materias
    cursor.execute('SELECT * FROM materias ORDER BY nombre')
    materias = cursor.fetchall()
    
    # Obtener cursos
    cursor.execute('SELECT * FROM cursos ORDER BY año, division')
    cursos = cursor.fetchall()
    
    conn.close()
    return render_template('gestionar_profesores.html', profesores=profesores, materias=materias, cursos=cursos)

@app.route('/api/crear_profesor', methods=['POST'])
def crear_profesor():
    """API para crear un nuevo profesor"""
    data = request.json
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO profesores (nombre, apellido, email, telefono)
            VALUES (?, ?, ?, ?)
        ''', (data['nombre'], data['apellido'], data['email'], data.get('telefono', '')))
        
        profesor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'profesor_id': profesor_id, 'message': 'Profesor creado correctamente'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/asignar_materia', methods=['POST'])
def asignar_materia():
    """API para asignar una materia y curso a un profesor"""
    data = request.json
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verificar si ya existe la asignación
        cursor.execute('''
            SELECT id FROM asignaciones 
            WHERE profesor_id = ? AND materia_id = ? AND curso_id = ?
        ''', (data['profesor_id'], data['materia_id'], data['curso_id']))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Esta asignación ya existe'})
        
        cursor.execute('''
            INSERT INTO asignaciones (profesor_id, materia_id, curso_id)
            VALUES (?, ?, ?)
        ''', (data['profesor_id'], data['materia_id'], data['curso_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Asignación creada correctamente'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/reportes')
def reportes():
    """Página de reportes"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Obtener estadísticas generales
    cursor.execute('SELECT COUNT(*) FROM profesores')
    total_profesores = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM asistencias WHERE fecha = date("now")')
    asistencias_hoy = cursor.fetchone()[0]
    
    # Asistencias recientes
    cursor.execute('''
        SELECT p.nombre, p.apellido, m.nombre as materia, 
               c.año || "° " || c.division as curso,
               h.hora_inicio || " - " || h.hora_fin as horario,
               a.fecha, a.presente, a.observaciones
        FROM asistencias a
        JOIN profesores p ON a.profesor_id = p.id
        JOIN materias m ON a.materia_id = m.id
        JOIN cursos c ON a.curso_id = c.id
        JOIN horarios h ON a.horario_id = h.id
        ORDER BY a.fecha DESC, h.hora_inicio DESC
        LIMIT 20
    ''')
    asistencias_recientes = cursor.fetchall()
    
    conn.close()
    
    return render_template('reportes.html', 
                         total_profesores=total_profesores,
                         asistencias_hoy=asistencias_hoy,
                         asistencias_recientes=asistencias_recientes)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)