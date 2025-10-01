from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from datetime import datetime, date
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Admin123'
app.config['MYSQL_DB'] = 'asistencia_profesores'
app.config['SECRET_KEY'] = 'admin123'

mysql = MySQL(app)

# Opcional: exponer fecha si deseas usarla en templates directamente
# from datetime import date, datetime  # ya importados arriba
# app.jinja_env.globals['date'] = date
# app.jinja_env.globals['datetime'] = datetime


# Rutas principales
@app.route('/')
def index():
    if 'profesor_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        cur = mysql.connection.cursor(DictCursor)
        cur.execute(
            "SELECT id_profesor, nombre, apellido, password FROM profesores WHERE LOWER(email) = %s LIMIT 1",
            (email,)
        )
        profesor = cur.fetchone()
        cur.close()

        if profesor:
            stored_password = profesor['password']
            password_ok = False
            try:
                password_ok = check_password_hash(stored_password, password)
            except Exception:
                # Si lo guardaron en texto plano durante pruebas
                password_ok = stored_password == password

            if password_ok:
                session['profesor_id'] = profesor['id_profesor']
                session['profesor_nombre'] = f"{profesor['nombre']} {profesor['apellido']}"
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('dashboard'))

        flash('Email o contraseña incorrectos', 'error')

    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']  # <-- Asegúrate de recoger el dni
        materia = request.form['materia']  # Si lo usas
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        
        # Verificar si el email ya existe
        cur.execute("SELECT id_profesor FROM profesores WHERE email = %s", (email,))
        if cur.fetchone(): 
            flash('El email ya está registrado', 'error')
            cur.close()
            return render_template('registro.html')
        
        # Crear nuevo profesor
        hashed_password = generate_password_hash(password)
        cur.execute(
            "INSERT INTO profesores (nombre, apellido, dni, materia, email, password) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre, apellido, dni, materia, email, hashed_password)
        )
        mysql.connection.commit()
        cur.close()
        
        flash('Registro exitoso. Puedes iniciar sesión ahora.', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/dashboard')
def dashboard():
    if 'profesor_id' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor(DictCursor)

    # Todas las materias disponibles (para que el profesor pueda elegir)
    cur.execute("SELECT id_materia, materia FROM materias ORDER BY materia")
    todas_materias = cur.fetchall()

    # Todos los cursos (opcional en horario)
    cur.execute("SELECT id, `año`, division FROM cursos ORDER BY `año`, division")
    cursos = cur.fetchall()

    # Horarios del profesor
    cur.execute(
        """
        SELECT h.id_horario, h.materia_id, h.curso_id, h.dia_semana, h.hora_clase,
               m.materia AS nombre_materia,
               CASE WHEN c.id IS NULL THEN NULL ELSE CONCAT(c.`año`, '°', c.division) END AS nombre_curso
        FROM profesor_horarios h
        JOIN materias m ON m.id_materia = h.materia_id
        LEFT JOIN cursos c ON c.id = h.curso_id
        WHERE h.profesor_id = %s
        ORDER BY h.dia_semana, h.hora_clase
        """,
        (session['profesor_id'],),
    )
    horarios = cur.fetchall()
    
    # Obtener asistencia del día
    hoy = date.today()
    cur.execute("""
        SELECT a.id_asistencia, a.id_profesor, a.fecha, a.hora_clase, a.hora_entrada, a.estado, a.observaciones,
               m.materia AS materia, CONCAT(c.`año`, '°', c.division) AS curso
        FROM asistencia a
        LEFT JOIN materias m ON a.materia_id = m.id_materia
        LEFT JOIN cursos c ON a.curso_id = c.id
        WHERE a.id_profesor = %s AND a.fecha = %s
        ORDER BY a.hora_entrada
    """, (session['profesor_id'], hoy))
    asistencia_hoy = cur.fetchall()
    
    cur.close()
    
    return render_template('dashboard.html', 
                         materias=todas_materias,
                         cursos=cursos,
                         horarios=horarios,
                         asistencia_hoy=asistencia_hoy,
                         profesor_nombre=session['profesor_nombre'],
                         hoy=hoy)

@app.route('/registrar_asistencia', methods=['GET', 'POST'])
def registrar_asistencia():
    if 'profesor_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        materia_id = request.form['materia']
        curso_id = request.form['curso']
        hora_clase = request.form['hora_clase']
        hora_llegada = request.form['hora_llegada']
        observaciones = request.form.get('observaciones', '')
        
        # Determinar si llegó temprano o tarde
        hora_clase_obj = datetime.strptime(hora_clase, '%H:%M').time()
        hora_llegada_obj = datetime.strptime(hora_llegada, '%H:%M').time()
        
        if hora_llegada_obj <= hora_clase_obj:
            estado = 'temprano'
        else:
            estado = 'tarde'
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO asistencia (id_profesor, materia_id, curso_id, fecha, 
                                   hora_entrada, estado, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (session['profesor_id'], materia_id, curso_id, date.today(),
              hora_llegada, estado, observaciones))
        mysql.connection.commit()
        cur.close()
        
        flash('Asistencia registrada exitosamente', 'success')
        return redirect(url_for('dashboard'))
    
    # Obtener materias y cursos para el formulario
    cur = mysql.connection.cursor()
    
    # Materias del profesor
    cur.execute("""
        SELECT m.id_materia, m.materia FROM materias m
        JOIN profesor_materia pm ON m.id_materia = pm.materia_id
        WHERE pm.profesor_id = %s
    """, (session['profesor_id'],))
    materias = cur.fetchall()
    
    # Todos los cursos
    cur.execute("SELECT id, año, division FROM cursos ORDER BY año")
    cursos = cur.fetchall()
    
    cur.close()
    
    return render_template('registrar_asistencia.html', 
                         materias=materias, 
                         cursos=cursos)

@app.route('/reportes')
def reportes():
    if 'profesor_id' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    
    # Estadísticas generales
    cur.execute("""
        SELECT 
            COUNT(*) as total_clases,
            SUM(CASE WHEN estado = 'temprano' THEN 1 ELSE 0 END) as llegadas_temprano,
            SUM(CASE WHEN estado = 'tarde' THEN 1 ELSE 0 END) as llegadas_tarde,
            SUM(CASE WHEN estado = 'ausente' THEN 1 ELSE 0 END) as ausencias
        FROM asistencia 
        WHERE id_profesor = %s
    """, (session['profesor_id'],))
    stats = cur.fetchone()
    
    # Asistencia por materia
    cur.execute("""
        SELECT m.materia, COUNT(*) as total_clases,
               SUM(CASE WHEN a.estado = 'temprano' THEN 1 ELSE 0 END) as temprano,
               SUM(CASE WHEN a.estado = 'tarde' THEN 1 ELSE 0 END) as tarde
        FROM asistencia a
        JOIN materias m ON a.materia_id = m.id_materia
        WHERE a.id_profesor = %s
        GROUP BY m.id_materia, m.materia
        ORDER BY m.materia
    """, (session['profesor_id'],))
    asistencia_materias = cur.fetchall()
    
    cur.close()
    
    return render_template('reportes.html', 
                         stats=stats, 
                         asistencia_materias=asistencia_materias)


# Endpoint: agregar horario de materia por profesor
@app.route('/horarios/agregar', methods=['POST'])
def agregar_horario():
    if 'profesor_id' not in session:
        return redirect(url_for('login'))

    materia_id = request.form.get('materia_id')
    curso_id = request.form.get('curso_id')  # opcional
    dia_semana = request.form.get('dia_semana')  # 0=Lunes ... 6=Domingo
    hora_clase = request.form.get('hora_clase')

    if not materia_id or not dia_semana or not hora_clase:
        flash('Completa materia, día y hora', 'error')
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor(DictCursor)

    if not str(materia_id).isdigit() or not str(dia_semana).isdigit():
        cur.close()
        flash('Datos inválidos', 'error')
        return redirect(url_for('dashboard'))

    materia_id = int(materia_id)
    dia_semana = int(dia_semana)
    curso_id_val = None
    if curso_id and str(curso_id).isdigit():
        curso_id_val = int(curso_id)

    # Validar FKs
    cur.execute("SELECT id_materia FROM materias WHERE id_materia = %s", (materia_id,))
    if cur.fetchone() is None:
        cur.close()
        flash('Materia no existe', 'error')
        return redirect(url_for('dashboard'))

    if curso_id_val is not None:
        cur.execute("SELECT id FROM cursos WHERE id = %s", (curso_id_val,))
        if cur.fetchone() is None:
            cur.close()
            flash('Curso no existe', 'error')
            return redirect(url_for('dashboard'))

    # Insertar horario
    cur2 = mysql.connection.cursor()
    cur2.execute(
        """
        INSERT INTO profesor_horarios (profesor_id, materia_id, curso_id, dia_semana, hora_clase)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (session['profesor_id'], materia_id, curso_id_val, dia_semana, hora_clase),
    )
    mysql.connection.commit()
    cur2.close()
    cur.close()

    flash('Horario agregado', 'success')
    return redirect(url_for('dashboard'))

@app.route('/guardar_asistencia', methods=['POST'])
def guardar_asistencia():
    if 'profesor_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Puede llegar horario_id para inferir materia/curso/hora_clase
        horario_id = request.form.get('horario_id')
        materia = request.form.get('materia')
        curso = request.form.get('curso')
        estado = request.form.get('estado')
        motivo = request.form.get('motivo', '')
        hora_entrada = request.form.get('hora_entrada', '08:30')
        
        if not materia or not estado:
            flash('Por favor completa todos los campos requeridos', 'error')
            return redirect(url_for('dashboard'))
        
        cur = mysql.connection.cursor(DictCursor)

        materia_id = None
        curso_id = None
        hora_clase = None

        if horario_id and str(horario_id).isdigit():
            # Usar horario guardado
            cur.execute(
                "SELECT materia_id, curso_id, hora_clase FROM profesor_horarios WHERE id_horario = %s AND profesor_id = %s",
                (int(horario_id), session['profesor_id']),
            )
            row = cur.fetchone()
            if not row:
                cur.close()
                flash('Horario no válido', 'error')
                return redirect(url_for('dashboard'))
            materia_id = row['materia_id']
            curso_id = row['curso_id']
            hora_clase = row['hora_clase']
        else:
            # Validar materia/curso desde selects directos
            if not materia or not str(materia).isdigit():
                cur.close()
                flash('Materia inválida', 'error')
                return redirect(url_for('dashboard'))
            materia_id = int(materia)
            cur.execute("SELECT id_materia FROM materias WHERE id_materia = %s", (materia_id,))
            if cur.fetchone() is None:
                cur.close()
                flash('La materia seleccionada no existe', 'error')
                return redirect(url_for('dashboard'))
            if curso and str(curso).isdigit():
                curso_id = int(curso)
                cur.execute("SELECT id FROM cursos WHERE id = %s", (curso_id,))
                if cur.fetchone() is None:
                    cur.close()
                    flash('El curso seleccionado no existe', 'error')
                    return redirect(url_for('dashboard'))
            hora_clase = request.form.get('hora_clase', hora_entrada)

        # Insertar nueva asistencia
        cur2 = mysql.connection.cursor()
        cur2.execute(
            """
            INSERT INTO asistencia (id_profesor, materia_id, curso_id, fecha,
                                   hora_entrada, hora_clase, estado, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (session['profesor_id'], materia_id, curso_id, date.today(),
             hora_entrada, hora_clase, estado, motivo),
        )
        
        mysql.connection.commit()
        cur2.close()
        cur.close()
        
        flash('Asistencia guardada exitosamente', 'success')
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

# Ruta para administradores (asignar materias a profesores)
@app.route('/admin/asignar_materias', methods=['GET', 'POST'])
def asignar_materias():
    if 'profesor_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        profesor_id = request.form['profesor']
        materias = request.form.getlist('materias')
        
        cur = mysql.connection.cursor()
        
        # Eliminar asignaciones anteriores
        cur.execute("DELETE FROM profesor_materia WHERE profesor_id = %s", (profesor_id,))
        
        # Asignar nuevas materias
        for materia_id in materias:
            cur.execute("INSERT INTO profesor_materia (profesor_id, materia_id) VALUES (%s, %s)",
                       (profesor_id, materia_id))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Materias asignadas exitosamente', 'success')
        return redirect(url_for('asignar_materias'))
    
    cur = mysql.connection.cursor()
    
    # Obtener todos los profesores
    cur.execute("SELECT id_profesor, nombre, apellido FROM profesores ORDER BY apellido, nombre")
    profesores = cur.fetchall()
    
    # Obtener todas las materias
    cur.execute("SELECT id_materia, materia FROM materias ORDER BY materia")
    materias = cur.fetchall()
    
    cur.close()
    
    return render_template('admin_asignar_materias.html', 
                         profesores=profesores, 
                         materias=materias)

if __name__ == '__main__':
    app.run(debug=True)