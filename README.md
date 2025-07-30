# 📚 Sistema de Gestión de Asistencia de Profesores

Una aplicación web completa desarrollada con Flask para gestionar la asistencia de profesores con seguimiento de puntualidad, múltiples materias por profesor y reportes detallados.

## ✨ Características Principales

### 🔐 Sistema de Autenticación
- **Registro de profesores** con email y contraseña
- **Login seguro** con sesiones cifradas
- **Dashboard personalizado** para cada profesor
- **Gestión de usuarios** por administradores

### 📝 Registro de Asistencia
- **Registro automático de puntualidad**:
  - ⏰ **Temprano**: 5+ minutos antes del horario
  - ✅ **Puntual**: ±5 minutos del horario establecido
  - ⚠️ **Tarde**: Más de 5 minutos después
- **Múltiples materias por profesor** (ej: Química y Física)
- **Horarios predefinidos** desde 8:30 AM hasta 4:00 PM
- **Observaciones** adicionales por registro

### 🏫 Gestión Académica
- **Cursos**: 1° a 6° año con divisiones (A, B, etc.)
- **Materias predefinidas**: Matemática, Lengua, Historia, Ciencias, etc.
- **Asignaciones flexibles**: Un profesor puede tener múltiples materias y cursos

### 📊 Reportes y Análisis
- **Estadísticas en tiempo real**
- **Gráficos de puntualidad** con Chart.js
- **Filtros avanzados** por fecha y estado
- **Exportación** a CSV y PDF
- **Impresión** de reportes

## 🗄️ Estructura de la Base de Datos

### Tablas Principales

1. **`profesores`**: Información de usuarios profesores
   - ID, nombre, apellido, email, contraseña hasheada, teléfono, estado activo

2. **`materias`**: Catálogo de materias
   - ID, nombre, descripción

3. **`cursos`**: Años académicos y divisiones
   - ID, año (1-6), división (A, B, etc.)

4. **`asignaciones`**: Relación profesor-materia-curso
   - Permite que un profesor tenga múltiples asignaciones

5. **`horarios`**: Bloques de tiempo predefinidos
   - Horarios desde 8:30 AM hasta 4:00 PM

6. **`asistencias`**: Registros de asistencia con puntualidad
   - Incluye hora de llegada, estado de puntualidad, diferencia en minutos

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.7+
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd sistema-asistencia-profesores
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

4. **Acceder a la aplicación**
   - Abrir navegador en: `http://localhost:5000`

## 🎯 Uso del Sistema

### Para Profesores

1. **Registro Inicial**
   - Ir a `/register`
   - Completar formulario con datos personales
   - Contactar administrador para asignación de materias

2. **Uso Diario**
   - Login en `/login`
   - Ir a "Mi Asistencia" o usar el dashboard
   - Seleccionar materia, curso y horario
   - El sistema calcula automáticamente la puntualidad

3. **Dashboard Personal**
   - Ver asignaciones activas
   - Historial de asistencias recientes
   - Estadísticas de puntualidad
   - Acceso rápido a funciones

### Para Administradores

1. **Gestión de Profesores**
   - Crear nuevos profesores
   - Asignar materias y cursos
   - Ver estadísticas generales

2. **Reportes**
   - Filtrar por fechas y estados
   - Exportar datos
   - Visualizar gráficos de puntualidad

## 🕐 Sistema de Horarios

### Horarios Predefinidos
```
08:30 - 09:30  |  1ra hora
09:30 - 10:30  |  2da hora
10:30 - 11:00  |  Recreo
11:00 - 12:00  |  3ra hora
12:00 - 13:00  |  4ta hora
13:00 - 14:00  |  Almuerzo
14:00 - 15:00  |  5ta hora
15:00 - 16:00  |  6ta hora
```

### Criterios de Puntualidad
- **Temprano** 🔵: Llegada 5+ minutos antes
- **Puntual** 🟢: Llegada entre -5 y +5 minutos
- **Tarde** 🟡: Llegada más de 5 minutos después

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask 2.3.3**: Framework web de Python
- **SQLite**: Base de datos embebida
- **Werkzeug**: Seguridad y hashing de contraseñas
- **Flask-CORS**: Manejo de CORS

### Frontend
- **Bootstrap 5.1.3**: Framework CSS responsive
- **Font Awesome 6.0**: Iconografía
- **jQuery 3.6.0**: Manipulación del DOM
- **Chart.js**: Gráficos interactivos

### Características Técnicas
- **Responsive Design**: Compatible con móviles y tablets
- **Progressive Web App**: Funcionalidades de aplicación nativa
- **Cifrado de contraseñas**: Hash seguro con Werkzeug
- **Sesiones seguras**: Manejo de estado del usuario

## 📱 Diseño Responsive

La aplicación está optimizada para:
- 🖥️ **Desktop**: Experiencia completa con sidebar
- 📱 **Mobile**: Navegación adaptativa y touch-friendly
- 📄 **Tablet**: Layout intermedio optimizado

## 🔒 Seguridad

- **Contraseñas hasheadas** con algoritmos seguros
- **Sesiones cifradas** del lado del servidor
- **Validación de datos** en frontend y backend
- **Prevención XSS** con escape de caracteres
- **CSRF protection** en formularios críticos

## 📈 Funcionalidades Avanzadas

### Reportes y Estadísticas
- Porcentaje de puntualidad mensual
- Distribución de estados (temprano/puntual/tarde)
- Filtros por profesor, fecha y estado
- Exportación en múltiples formatos

### Interfaz de Usuario
- Dashboard personalizado por usuario
- Previsualización de asistencia antes de guardar
- Reloj en tiempo real
- Notificaciones de estado

### Administración
- Panel de gestión de profesores
- Asignación masiva de materias
- Estadísticas generales del sistema
- Gestión de usuarios activos/inactivos

## 🚀 Posibles Mejoras Futuras

- [ ] **Notificaciones push** para recordatorios
- [ ] **API REST** para integración con otros sistemas
- [ ] **Reportes automáticos** por email
- [ ] **Geolocalización** para verificar ubicación
- [ ] **Aplicación móvil nativa**
- [ ] **Integración con calendarios** (Google Calendar, Outlook)
- [ ] **Sistema de permisos** más granular
- [ ] **Backup automático** de base de datos

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

Desarrollado con ❤️ para facilitar la gestión de asistencia en instituciones educativas.

---

### 📞 Soporte

Si tienes preguntas o necesitas ayuda:
- Crear un issue en GitHub
- Revisar la documentación técnica
- Consultar los logs de la aplicación

**¡Gracias por usar el Sistema de Gestión de Asistencia de Profesores!** 🎓

