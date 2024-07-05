import sqlite3
import socket
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

init_sql_file = "/home/chonp/Escritorio/ArquiProyecto/init.sql"

def read_init_sql(file_path):
    with open(file_path, "r") as sql_file:
        sql_script = sql_file.read()
        cursor.executescript(sql_script)

def login(correo, contrasena):
    cursor.execute("SELECT nombre, ID_Usuario, rol FROM Usuario WHERE correo = ? AND contrasena = ?", (correo, contrasena))
    resultado = cursor.fetchone()
    if resultado is not None:
        nombre = resultado[0]
        idU = resultado[1]
        rol = resultado[2]
        logging.info("Login Exitoso.")
        return nombre, idU, rol
    else:
        logging.warning("No se encontraron usuarios con la información solicitada")
        return None

def registro(nombre, correo, contrasena):
    rol = "visita"
    cursor.execute("SELECT COUNT(*) FROM Usuario WHERE correo = ?", (correo,))
    resultado = cursor.fetchone()
    if resultado[0] > 0:
        logging.warning("El usuario ya está registrado.")
        return False
    else:
        cursor.execute("INSERT INTO Usuario (nombre, correo, contrasena, rol) VALUES (?, ?, ?, ?)", (nombre, correo, contrasena, rol))
        conn.commit()
        logging.info("Usuario registrado con éxito.")
        return True

def atracciones():
    cursor.execute("SELECT * FROM Atraccion")
    atracciones = cursor.fetchall()
    if atracciones:
        logging.info('Atracciones encontradas')
        return atracciones
    else:
        logging.warning('No se encontraron atracciones')
        return None

def verHorarios(id_At):
    cursor.execute("SELECT ID_Horario, Fecha, Cupo_Disponible FROM Horarios WHERE ID_Atraccion = ?", (id_At,))
    horarios = cursor.fetchall()
    if horarios:
        logging.info('Horarios encontrados')
        return horarios
    else:
        logging.warning('No se encontraron horarios disponibles')
        return None

def reservar(idHor, idU, cantidad):
    cursor.execute("SELECT Cupo_Disponible FROM Horarios WHERE ID_Horario = ?", (idHor,))
    resultado = cursor.fetchone()
    if resultado[0] < cantidad:
        logging.warning("La cantidad excede los cupos disponibles")
        return False
    else:
        cursor.execute("BEGIN TRANSACTION;")
        cursor.execute("INSERT INTO Reserva (ID_Horario, ID_Usuario, Cantidad) VALUES (?, ?, ?)", (idHor, idU, cantidad))
        cursor.execute("UPDATE Horarios SET Cupo_Disponible = Cupo_Disponible - ? WHERE ID_Horario = ?", (cantidad, idHor))
        conn.commit()
        logging.info("Reserva exitosa")
        return True
    
def calificar(idAt, idU, calificacion, reseña):
    try:
        cursor.execute("SELECT COUNT(*) FROM Calificaciones WHERE ID_Atraccion = ? AND ID_Usuario = ?", (idAt, idU))
        count = cursor.fetchone()[0]  # Obtiene el primer valor del resultado
        if count > 0:
            cursor.execute("UPDATE Calificaciones SET Calificacion = ?, Comentario = ? WHERE ID_Atraccion = ? AND ID_Usuario = ?", (calificacion, reseña, idAt, idU))
            conn.commit()
            logging.info('Calificación actualizada con éxito')
            return True
        else:
            cursor.execute("INSERT INTO Calificaciones (ID_Atraccion, ID_Usuario, Calificacion, Comentario) VALUES (?, ?, ?, ?)", (idAt, idU, calificacion, reseña))
            conn.commit()
            logging.info("Calificación registrada con éxito.")
            return True
    except sqlite3.Error as e:
        logging.error(f'Error al insertar o actualizar la calificación: {e}')
        return False


def asistencia(idAt, fecha, cantidad):
    try:
        # Intentar insertar
        cursor.execute("INSERT INTO Asistencia (ID_Atraccion, Fecha, Asistentes) VALUES (?, ?, ?)", (idAt, fecha, cantidad))
        conn.commit()
        logging.info('Asistencia registrada')
        return True
    except sqlite3.IntegrityError:
        # Si hay conflicto, actualizar la cantidad de asistentes
        cursor.execute("UPDATE Asistencia SET Asistentes = Asistentes + ? WHERE ID_Atraccion = ? AND Fecha = ?", (cantidad, idAt, fecha))
        conn.commit()
        logging.info('Asistencia actualizada')
        return True
    except sqlite3.Error as e:
        logging.error(f'Error al actualizar asistencia: {e}')
        return False

    
def popular():
    try:
        cursor.execute('''
            WITH CalificacionesPromedio AS (
                SELECT 
                    ID_Atraccion,
                    AVG(Calificacion) AS PromedioCalificacion
                FROM 
                    Calificaciones
                GROUP BY 
                    ID_Atraccion
            ),
            AsistentesTotales AS (
                SELECT 
                    ID_Atraccion,
                    SUM(Asistentes) AS TotalAsistentes
                FROM 
                    Asistencia
                GROUP BY 
                    ID_Atraccion
            ),
            Popularidad AS (
                SELECT 
                    C.ID_Atraccion,
                    AT.Nombre AS Nombre_Atraccion,
                    C.PromedioCalificacion,
                    A.TotalAsistentes,
                    (0.6 * C.PromedioCalificacion + 0.4 * A.TotalAsistentes) AS PuntuacionPopularidad
                FROM 
                    CalificacionesPromedio C
                JOIN 
                    AsistentesTotales A ON C.ID_Atraccion = A.ID_Atraccion
                JOIN 
                    Atraccion AT ON C.ID_Atraccion = AT.ID_Atraccion
            )
            SELECT 
                Nombre_Atraccion,
                PromedioCalificacion,
                TotalAsistentes,
                PuntuacionPopularidad
            FROM 
                Popularidad
            ORDER BY 
                PuntuacionPopularidad DESC
            LIMIT 5;
        ''')
        populares = cursor.fetchall()
        logging.info('Atracciones populares encontradas')
        return populares
    except sqlite3.Error as e:
        logging.error(f'Error al encontrar atracciones populares: {e}')
        return False


conn = sqlite3.connect("/home/chonp/Escritorio/ArquiProyecto/BDD/database.db")
cursor = conn.cursor()

read_init_sql(init_sql_file)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 5000)
logging.info('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

try:
    message = b'00010sinitdatos'
    logging.info('sending {!r}'.format(message))
    sock.sendall(message)
    while True:
        logging.info("Waiting for transaction BBDD")
        amount_received = 0
        amount_expected = int(sock.recv(5))
        while amount_received < amount_expected:
            data = sock.recv(amount_expected - amount_received)
            amount_received += len(data)
            logging.info('received {!r}'.format(data))
            logging.info("Processing sql...")
            try:
                data = data.decode().split()
                opcion = data[1]
                if opcion == '1':
                    Correo = data[2]
                    Contrasena = data[3]
                    logging.info('Ingresando...')
                    nombre, idusuario, rol = login(Correo, Contrasena)
                    if nombre is not None:
                        idU = str(idusuario)
                        message = '000{}datosloginexito {} {} {}'.format(18 + len(nombre + idU + rol), nombre, idU, rol).encode()
                    else:
                        message = '00015datosloginfallo'.encode()
                    logging.info('sending {!r}'.format(message))
                    sock.send(message)
                elif opcion == '2':
                    Nombre = data[2]
                    Correo = data[3]
                    Contrasena = data[4]
                    logging.info('Registrando...')
                    if registro(Nombre, Correo, Contrasena):
                        message = '00015datosregisexito'.encode()
                    else:
                        message = '00015datosregisfallo'.encode()
                    logging.info('sending {!r}'.format(message))
                    sock.send(message)
                elif opcion == '3':
                    lista = atracciones()
                    atracciones_str = ";".join("{},{},{},{},{}".format(id_At, nombre, desc, res, disp) for id_At, nombre, desc, res, disp in lista)
                    message = '00{}datosexito  {}'.format(16 + len(atracciones_str), atracciones_str).encode()
                    logging.info('sending {!r}'.format(message))
                    sock.send(message)
                elif opcion == '4':
                    idAt = int(data[2])
                    lista = verHorarios(idAt)
                    if lista is not None:
                        horarios = ";".join("{},{},{}".format(id_Hor, fecha, cupos) for id_Hor, fecha, cupos in lista)
                        message = '000{}datosexito {}'.format(16 + len(horarios), horarios).encode()
                    else:
                        message = '00015datosreshofallo'.encode()
                    logging.info('sending {!r}'.format(message))
                    sock.send(message)
                elif opcion == '5':
                    idHor = int(data[2])
                    idU = int(data[3])
                    cantidad = int(data[4])
                    logging.info('Reservando...')
                    if reservar(idHor, idU, cantidad):
                        message = '00015datosreshoexito'.encode()
                    else:
                        message = '00015datosreshofallo'.encode()
                    logging.info('sending {!r}'.format(message))
                    sock.send(message)
                elif opcion == '6':
                    opcion = data[1]
                    separar = data[2].split(";")
                    idAt = int(separar[0])
                    idU = int(separar[1])
                    calificacion = int(separar[2])
                    reseña1 = separar[3]
                    reseña = reseña1.replace("|", " ")
                    logging.info('Calificando...')
                    if calificar(idAt, idU, calificacion, reseña):
                        message = '00015datoscalifexito'.encode()
                    else:
                        message = '00015datoscaliffallo'.encode()
                    logging.info('sending {!r}'.format(message))
                    sock.send(message)
                elif opcion == '7':
                    opcion = data[1]
                    idAt = int(data[2])
                    fecha = data[3]
                    cant = int(data[4])
                    logging.info('Ingresando asistencia...')
                    if asistencia(idAt, fecha, cant):
                        message = '00015datosasistexito'.encode()
                    else:
                        message = '00015datosasistfallo'.encode()
                    logging.info('sending {!r}'.format(message))
                    sock.send(message)
                elif opcion == '8':
                    lista = popular()
                    populares = ";".join("{},{},{},{}".format(nombre, promedio, asist, pop) for nombre, promedio, asist, pop in lista)
                    message = '00{}datosatpopexito  {}'.format(17 + len(populares), populares).encode()
                    logging.info('sending {!r}'.format(message))
                    sock.send(message)
            except Exception as e:
                print(f"Ocurrió un error: {e}")
            logging.info('-------------------------------')

finally:
    logging.info('closing socket')
    sock.close()
    conn.commit()
    conn.close()
