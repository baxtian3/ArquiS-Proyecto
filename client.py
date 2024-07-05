import socket
import time
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def respuestaLogin(sock):
    time.sleep(2)
    data = sock.recv(4096).decode()
    if 'exito' in data:
        usuario = data.split()
        nombre = usuario[1]
        idU = usuario[2]
        rol = usuario[3]
        return nombre, idU, rol
    else:
        print("Los datos ingresados no coinciden, vuelva a intentar o cree una nueva cuenta.")
        print("\n")
        return None, None, None

def respuestaRegis(sock):
    time.sleep(2)
    data = sock.recv(4096).decode()
    if 'exito' in data:
        return True
    else:
        print("Los datos ingresados ya están en uso, intente nuevamente.")
        print("\n")
        return False

def respuestaVer(sock):
    time.sleep(2)
    data = sock.recv(4096).decode()
    if 'exito' in data:
        separar = data.split("  ")
        atracciones = separar[1]
        return atracciones
    else:
        return ""

def datosAtraccion(id_At, nombre, desc, res, disp):
    print(f"Nombre: '{nombre}'\nID: {id_At}\nDisponible: {'Sí' if disp else 'No'}\nRestricción: {res}\nDescripción: {desc}")

def verHorarios(sock):
    time.sleep(2)
    data = sock.recv(4096).decode()
    if 'exito' in data:
        separar = data.split(" ")
        horarios = separar[1]
        return horarios
    else:
        print("No se encontraron horarios disponibles para esta atracción")
        print("\n")
        return False

def respuestaRes(sock):
    time.sleep(2)
    data = sock.recv(4096).decode()
    if 'exito' in data:
        return True
    else:
        print("El horario ya está reservado.")
        print("\n")
        return False
    
def respuestaCalif(sock):
    time.sleep(2)
    data = sock.recv(4096).decode()
    if 'exito' in data:
        return True
    else:
        print("Error al intentar calificar")
        print("\n")
        return False
    
def respuestaAsist(sock):
    time.sleep(2)
    data = sock.recv(4096).decode()
    if 'exito' in data:
        return True
    else:
        print("Error al ingresar asistencia")
        print("\n")
        return False

def respuestaAtpop(sock):
    time.sleep(2)
    data = sock.recv(4096).decode()
    if 'exito' in data:
        separar = data.split("  ")
        populares = separar[1]
        return populares
    else:
        return ""
    
def datosPopulares(nombre, promedio, asist, pop):
    print(f"Nombre: '{nombre}'\nCalificacion promedio: {promedio}\nAsistentes totales: {asist}\nPopularidad: {pop}\n")
    
def main():
    systemState = True

    while systemState:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            server_address = ('localhost', 5000)
            print(f'Conectando a {server_address[0]} puerto {server_address[1]}')
            sock.connect(server_address)

            print("Menú Principal")
            print("0 - Salir")
            print("1 - Login")
            print("2 - Registrarse")
            print("3 - Ver Atracciones")
            opcion = input("¿Qué desea hacer? ")

            try:
                if opcion == '0':
                    print("Saliendo...")
                    systemState = False

                elif opcion == '1':
                    Correo = input("Ingrese su correo: ")
                    Contrasena = input("Ingrese contraseña: ")
                    largo = len(Correo + Contrasena + opcion) + 13
                    message = f'000{largo}login {opcion} {Correo} {Contrasena}'.encode()
                    sock.sendall(message)
                    nombre, idU, rol = respuestaLogin(sock)
                    loginState = False
                    if nombre is not None:
                        loginState = True
                    if loginState and rol == "visita":
                        print(f"\nBienvenido, {nombre}\n")
                        while loginState:
                            print("0 - Salir")
                            print("1 - Ver todas las atracciones")
                            print("2 - Ver atracciones populares")
                            opcion = input("¿Qué desea hacer? ")
                            try:
                                if opcion == '0':
                                    print('Saliendo...\n')
                                    loginState = False

                                elif opcion == '1':
                                    largo = 10
                                    message = f'000{largo}datos 3'.encode()
                                    sock.sendall(message)
                                    lista = respuestaVer(sock)
                                    nombres = lista.split(";")
                                    
                                    print("Atracciones: ")
                                    for n in nombres:
                                        nombre = n.split(",")
                                        print(f"{nombre[0]}. {nombre[1]}")

                                    atracciones_por_id = {}
                                    for dato in nombres:
                                        id_At, nombre, desc, res, disp = map(str.strip, dato.split(","))
                                        id_At = int(id_At)
                                        disp = bool(int(disp))
                                        atracciones_por_id[id_At] = (nombre, desc, res, disp)
                                    
                                    while True:
                                        opcion = input("Seleccione una Atracción: (0 para Salir) ")
                                        op = int(opcion)
                                        if op == 0:
                                            print("Saliendo del programa.")
                                            break
                                        elif op in atracciones_por_id:
                                            datosAtraccion(op, *atracciones_por_id[op])

                                            while True:
                                                sub_opcion = input("¿Qué desea hacer? (1: Reservar, 2: Calificar, 3: Volver atrás) ")
                                                sub_op = int(sub_opcion)

                                                if sub_op == 1:
                                                    hor = '4'
                                                    idAt = op
                                                    largo = len(hor + str(idAt)) + 9
                                                    message = f'000{largo}resho {hor} {idAt}'.encode()
                                                    sock.sendall(message)
                                                    lista = verHorarios(sock)
                                                    if lista:
                                                        horarios = [tuple(horario.split(',')) for horario in lista.split(';')]
                                                        horarios = [(int(id_Hor), fecha, int(cupos)) for id_Hor, fecha, cupos in horarios]
                                                        for id_Hor, fecha, cupos in horarios:
                                                            print(f"{id_Hor}. {fecha}: {cupos} cupos")

                                                        try:
                                                            idHor = int(input("Seleccione el ID_Hor del horario que desea reservar: "))
                                                            
                                                            horario_valido = next((horario for horario in horarios if horario[0] == idHor), None)
                                                            
                                                            if horario_valido:
                                                                cantidad = int(input("Ingrese la cantidad de cupos que desea reservar: "))
                                                                
                                                                if cantidad > 0 and cantidad <= horario_valido[2]:
                                                                    res = '5'
                                                                    idHor = str(idHor)
                                                                    idU = str(idU)
                                                                    cantidad = str(cantidad)
                                                                    largo = len(idHor + idU + cantidad) + 9
                                                                    message = f'000{largo}resho {res} {idHor} {idU} {cantidad}'.encode()
                                                                    sock.sendall(message)
                                                                    if respuestaRes(sock):
                                                                        print("Reservado con éxito.\n")
                                                                else:
                                                                    print('Cantidad de cupos inválida. Debe ser un número positivo y no exceder el cupo disponible.')
                                                            else:
                                                                print('ID_Hor no válido. Por favor, ingrese un ID_Hor válido.')
                                                                
                                                        except ValueError:
                                                            print('Entrada inválida. Por favor, ingrese un número.')

                                                    else:
                                                        print("No se encontraron horarios disponibles")
                                                        break
                                                elif sub_op == 2:
                                                    cal = '6'
                                                    calificacion = str(input("Ingrese una calificación (1-5 estrellas): ").strip())
                                                    while True:
                                                        reseña1 = input("Ingrese una reseña (máximo 83 caracteres): ").strip()
                                                        reseña = reseña1.replace(" ", "|")
                                                        if len(reseña) <= 83:
                                                            break
                                                        else:
                                                            print("La reseña excede los 83 caracteres. Inténtelo de nuevo.")
                                                    idAt = str(op)
                                                    idU = str(idU)
                                                    largo = len(calificacion + reseña + cal + idAt + idU) + 10
                                                    message = f'000{largo}calif {cal} {idAt};{idU};{calificacion};{reseña}'.encode()
                                                    sock.sendall(message)
                                                    if respuestaCalif(sock):
                                                        print("Calificación registrada.\n")
                                                    break
                                                elif sub_op == 3:
                                                    break
                                                else:
                                                    print("Opción no válida. Inténtelo de nuevo.")
                                        else:
                                            print("Opción no válida. Inténtelo de nuevo.")

                                elif opcion == '2':
                                    largo = 10
                                    message = f'000{largo}atpop 8'.encode()
                                    sock.sendall(message)
                                    lista = respuestaAtpop(sock)
                                    populares = lista.split(";")
                                    
                                    print("Atracciones populares: ")
                                    for n in populares:
                                        datos = n.split(",")
                                        datosPopulares(datos[0], datos[1], datos[2], datos[3])


                            except Exception as e:
                                print(f"Ocurrió un error: {e}")

                    elif loginState and rol == "personal":
                        print(f"\nBienvenido personal {nombre}\n")
                        while loginState:
                            print("0 - Salir")
                            print("1 - Gestionar asistencia")
                            opcion = input("¿Qué desea hacer? ")
                            try:
                                if opcion == '0':
                                    print('Saliendo...\n')
                                    loginState = False

                                elif opcion == '1':
                                    largo = 10
                                    message = f'000{largo}datos 3'.encode()
                                    sock.sendall(message)
                                    lista = respuestaVer(sock)
                                    nombres = lista.split(";")
                                    
                                    print("Atracciones: ")
                                    for n in nombres:
                                        nombre = n.split(",")
                                        print(f"{nombre[0]}. {nombre[1]}")

                                    atracciones_por_id = {}
                                    for dato in nombres:
                                        id_At, nombre, desc, res, disp = map(str.strip, dato.split(","))
                                        id_At = int(id_At)
                                        disp = bool(int(disp))
                                        atracciones_por_id[id_At] = (nombre, desc, res, disp)
                                    
                                    while True:
                                        opcion = input("Seleccione una Atracción para modificar asistencia: (0 para Salir) ")
                                        op = int(opcion)
                                        if op == 0:
                                            print("Saliendo del programa.")
                                            break
                                        elif op in atracciones_por_id:
                                            while True:
                                                fecha = input("Ingrese el día: ").lower()
                                                if fecha in ['jueves', 'viernes', 'sabado', 'domingo']:
                                                    break  # Salir del bucle interno si la fecha es válida
                                                else:
                                                    print("Día no válido. Por favor ingrese jueves, viernes, sábado o domingo.")
                                            
                                            while True:
                                                asis = input("Ingrese la asistencia: ")
                                                if asis.isdigit():  # Verificar si es un número
                                                    cant = int(asis)
                                                    break  # Salir del bucle interno si la asistencia es válida
                                                else:
                                                    print("Asistencia no válida. Por favor ingrese un número válido.")
                                            a = '7'
                                            idAt = op
                                            largo = len(a + str(idAt) + fecha + str(cant)) + 9
                                            message = f'000{largo}asist {a} {idAt} {fecha} {cant}'.encode()
                                            sock.sendall(message)
                                            if respuestaAsist(sock):
                                                print("Asistencia registrada.\n")
                                            break


                            except Exception as e:
                                print(f"Ocurrió un error: {e}")    

                elif opcion == '2':
                    Nombre = input("Ingrese el Nombre: ")
                    Correo = input("Ingrese el Correo: ")
                    Contrasena = input("Ingrese la Contraseña: ")
                    largo = len(Nombre + Correo + Contrasena + opcion) + 9
                    message = f'000{largo}regis {opcion} {Nombre} {Correo} {Contrasena}'.encode()
                    sock.sendall(message)
                    if respuestaRegis(sock):
                        print("Usuario Registrado.\n")

                elif opcion == '3':
                    largo = len(opcion) + 9
                    message = f'000{largo}datos {opcion}'.encode()
                    sock.sendall(message)
                    lista = respuestaVer(sock)
                    nombres = lista.split(";")
                    
                    print("Atracciones: ")
                    for n in nombres:
                        nombre = n.split(",")
                        print(f"{nombre[0]}. {nombre[1]}")
                    
                    atracciones_por_id = {}
                    for dato in nombres:
                        id_At, nombre, desc, res, disp = map(str.strip, dato.split(","))
                        id_At = int(id_At)
                        disp = bool(int(disp))
                        atracciones_por_id[id_At] = (nombre, desc, res, disp)
                    
                    while True:
                        opcion = input("Seleccione una Atracción: (0 para Salir) ")
                        op = int(opcion)
                        if op == 0:
                            print("Saliendo del programa.")
                            break
                        elif op in atracciones_por_id:
                            datosAtraccion(op, *atracciones_por_id[op])
                        else:
                            print("Opción no válida. Inténtelo de nuevo.")

                else:
                    print("Opción no válida. Inténtelo de nuevo.")
            except Exception as e:
                print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
