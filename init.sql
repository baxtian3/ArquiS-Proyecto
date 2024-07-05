-- Crear la tabla Usuario si no existe
CREATE TABLE IF NOT EXISTS Usuario (
    ID_Usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT,
    Correo TEXT,
    Contrasena VARCHAR,
    Rol TEXT
);

-- Crear la tabla Atraccion si no existe
CREATE TABLE IF NOT EXISTS Atraccion (
    ID_Atraccion INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT,
    Descripcion TEXT,
    Restricciones TEXT,
    Disponible BOOLEAN
);

-- Crear la tabla Horarios si no existe
CREATE TABLE IF NOT EXISTS Horarios (
    ID_Horario INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Atraccion INTEGER,
    Fecha TEXT,
    Cupo_Disponible INTEGER,
    FOREIGN KEY (ID_Atraccion) REFERENCES Atraccion(ID_Atraccion)
);

-- Crear la tabla Reserva si no existe
CREATE TABLE IF NOT EXISTS Reserva (
    ID_Reserva INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Horario INTEGER,
    ID_Usuario INTEGER,
    Cantidad INTEGER,
    FOREIGN KEY (ID_Horario) REFERENCES Horarios(ID_Horario),
    FOREIGN KEY (ID_Usuario) REFERENCES Horarios(ID_Usuario)
);

-- Crear la tabla Calificaciones si no existe
CREATE TABLE IF NOT EXISTS Calificaciones (
    ID_Calificacion INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Atraccion INTEGER,
    ID_Usuario INTEGER,
    Calificacion INTEGER,
    Comentario TEXT,
    FOREIGN KEY (ID_Atraccion) REFERENCES Atraccion(ID_Atraccion),
    FOREIGN KEY (ID_Usuario) REFERENCES Horarios(ID_Usuario)
);

-- Crear la tabla Asistencia si no existe
CREATE TABLE IF NOT EXISTS Asistencia (
    ID_Asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Atraccion INTEGER,
    Fecha TEXT CHECK (Fecha IN ('jueves', 'viernes', 'sabado', 'domingo')),
    Asistentes INTEGER,
    UNIQUE(ID_Atraccion, Fecha),
    FOREIGN KEY (ID_Atraccion) REFERENCES Atraccion(ID_Atraccion)
);


