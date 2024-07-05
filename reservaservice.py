import socket
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the server is listening
server_address = ('localhost', 5000)
logging.info('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
try:
    # Send data
    message = b'00010sinitresho'
    logging.info('sending {!r}'.format(message))
    sock.sendall(message)
    while True:
        # Look for the response
        logging.info("Waiting for transaction Reserva")
        amount_received = 0
        amount_expected = int(sock.recv(5))
        while amount_received < amount_expected:
            data = sock.recv(amount_expected - amount_received)
            amount_received += len(data)
            logging.info('received {!r}'.format(data))
            logging.info("Processing reserva...")
            data = data.decode().split()
            try:
                opcion = data[1]
                #-----------------VER HORARIOS------------------
                if opcion == '4':
                    logging.info("recibido...")
                    id_At = data[2]
                    largo = len(opcion + id_At) + 9
                    message = '000{}datos {} {}'.format(largo, opcion, id_At).encode()
                    logging.info('sending to bbdd {!r}'.format(message))
                    sock.sendall(message)
                    
                    # Esperar respuesta de la base de datos
                    logging.info("Waiting for response from BBDD")
                    respuesta = sock.recv(4096)
                    logging.info('response from bbdd: {!r}'.format(respuesta))
                    
                    if 'exito' in respuesta.decode():
                        separar = respuesta.decode().split(" ")
                        if len(separar) > 1:  # Verificar si hay suficientes elementos
                            horarios = separar[1]  # Ajustado para reflejar el índice correcto
                            message = '000{}reshoexito {}'.format(11 + len(horarios), horarios).encode()
                            logging.info('sending {!r}'.format(message))
                            sock.send(message)
                        else:
                            logging.error("Invalid response format from BBDD")
                            message = '00010reshofallo'.encode()
                            logging.info('sending {!r}'.format(message))
                            sock.send(message)
                    else:
                        message = '00010reshofallo'.encode()
                        logging.info('sending {!r}'.format(message))
                        sock.send(message)
                #-------------------RESERVAR---------------------
                elif opcion == '5':
                    idHor = data[2]
                    idU = data[3]
                    cantidad = data[4]
                    largo = len(idHor + idU + cantidad) + 13
                    message = '000{}datos {} {} {} {}'.format(largo, opcion, idHor, idU, cantidad).encode()
                    logging.info('sending to bbdd {!r}'.format(message))
                    sock.sendall(message)
                    
                    # Esperar respuesta de la base de datos
                    logging.info("Waiting for response from BBDD")
                    respuesta = sock.recv(4096)
                    logging.info('response from bbdd: {!r}'.format(respuesta))
                    
                    if 'exito' in respuesta.decode():
                        message = '00010reshoexito'.encode()
                        logging.info('sending {!r}'.format(message))
                        sock.send(message)
                    else:
                        message = '00010reshofallo'.encode()
                        logging.info('sending {!r}'.format(message))
                        sock.send(message)
            except Exception as e:
                logging.error(f"Error processing data: {e}")
            logging.info('-------------------------------')

finally:
    logging.info('closing socket')
    sock.close()
