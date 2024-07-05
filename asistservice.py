import socket
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Create a TCP/IP socket
sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the server is listening
server_address = ('localhost', 5000)
logging.info ('connecting to {} port {}'.format (*server_address))
sock.connect (server_address)
try:
    # Send data
    message = b'00010sinitasist'
    logging.info ('sending {!r}'.format (message))
    sock.sendall (message)
    while True:
        # Look for the response
        logging.info ("Waiting for transaction Asistencia")
        amount_received = 0
        amount_expected = int(sock.recv(5))
        while amount_received < amount_expected:
            data = sock.recv (amount_expected - amount_received)
            amount_received += len (data)
            logging.info('received {!r}'.format(data))
            logging.info ("Processing asistencia...")
            data = data.decode().split()
            try:
                opcion = data[1]
                idAt = data[2]
                fecha = data[3]
                cant = data[4]
                
                largo = len(opcion + idAt + fecha + cant) + 9
                message = '000{}datos {} {} {} {}'.format(largo, opcion, idAt, fecha, cant).encode()
                logging.info ('sending to bbdd {!r}'.format (message))
                sock.sendall(message)
                respuesta = sock.recv(4096)
                print(respuesta.decode())
                if 'exito' in respuesta.decode():
                    message = '00010asistexito'.encode()
                    logging.info ('sending {!r}'.format (message))
                    sock.send(message)
                else:
                    message = '00010asistfallo'.encode()
                    logging.info ('sending {!r}'.format (message))
                    sock.send(message)
            except:
                pass
            logging.info('-------------------------------')

finally:
    logging.info ('closing socket')
    sock.close ()