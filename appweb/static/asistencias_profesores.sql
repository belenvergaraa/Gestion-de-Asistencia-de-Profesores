-- Crear base y configurar juego de caracteres (recomendado por el campo `año`)
CREATE DATABASE IF NOT EXISTS asistencia_profesores
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE asistencia_profesores;

-- Tabla: profesores
CREATE TABLE IF NOT EXISTS profesores (
  id_profesor INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  dni VARCHAR(20) NOT NULL,
  materia VARCHAR(100) NULL,
  email VARCHAR(150) NOT NULL,
  password VARCHAR(255) NOT NULL,
  UNIQUE KEY uq_profesores_email (email),
  UNIQUE KEY uq_profesores_dni (dni)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: materias
CREATE TABLE IF NOT EXISTS materias (
  id_materia INT AUTO_INCREMENT PRIMARY KEY,
  materia VARCHAR(150) NOT NULL,
  UNIQUE KEY uq_materias_materia (materia)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: cursos

CREATE TABLE IF NOT EXISTS cursos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  `año` INT NOT NULL,
  division VARCHAR(10) NOT NULL,
  UNIQUE KEY uq_cursos_anio_division (`año`, division)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla intermedia: profesor_materia (asignación de materias a profesores)
CREATE TABLE IF NOT EXISTS profesor_materia (
  profesor_id INT NOT NULL,
  materia_id INT NOT NULL,
  PRIMARY KEY (profesor_id, materia_id),
  KEY idx_pm_profesor (profesor_id),
  KEY idx_pm_materia (materia_id),
  CONSTRAINT fk_pm_profesor
    FOREIGN KEY (profesor_id) REFERENCES profesores(id_profesor)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_pm_materia
    FOREIGN KEY (materia_id) REFERENCES materias(id_materia)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: asistencia
-- Coherente con los INSERT/SELECT del código:
-- - id_profesor (FK)
-- - materia_id (FK)
-- - curso_id (FK)
-- - fecha, hora_entrada, hora_clase, estado, observaciones
CREATE TABLE IF NOT EXISTS asistencia (
  id_asistencia INT AUTO_INCREMENT PRIMARY KEY,
  id_profesor INT NOT NULL,
  materia_id INT NULL,
  curso_id INT NULL,
  fecha DATE NOT NULL,
  hora_entrada TIME NOT NULL,
  hora_clase TIME NULL,
  estado ENUM('temprano','tarde','ausente') NOT NULL,
  observaciones TEXT NULL,
  KEY idx_asistencia_profesor (id_profesor),
  KEY idx_asistencia_materia (materia_id),
  KEY idx_asistencia_curso (curso_id),
  KEY idx_asistencia_fecha (fecha),
  CONSTRAINT fk_asistencia_profesor
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_asistencia_materia
    FOREIGN KEY (materia_id) REFERENCES materias(id_materia)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_asistencia_curso
    FOREIGN KEY (curso_id) REFERENCES cursos(id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;