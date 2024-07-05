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
    message = b'00010sinitatpop'
    logging.info ('sending {!r}'.format (message))
    sock.sendall (message)
    while True:
        # Look for the response
        logging.info ("Waiting for transaction AtraccionPopular")
        amount_received = 0
        amount_expected = int(sock.recv(5))
        while amount_received < amount_expected:
            data = sock.recv (amount_expected - amount_received)
            amount_received += len (data)
            logging.info('received {!r}'.format(data))
            logging.info ("Processing atraccionPopular...")
            data = data.decode().split()
            try:
                opcion = data[1]
                largo = 10
                message = '000{}datos {}'.format(largo, opcion).encode()
                logging.info ('sending to bbdd {!r}'.format (message))
                sock.sendall(message)
                respuesta = sock.recv(4096)
                print(respuesta.decode())
                if 'exito' in respuesta.decode():
                    atpop = respuesta.decode().split("  ")
                    populares = atpop[1]
                    message = '00{}atpopexito  {}'.format(12 + len(populares), populares).encode()
                    logging.info ('sending {!r}'.format (message))
                    sock.send(message)
                else:
                    message = '00010atpopfallo'.encode()
                    logging.info ('sending {!r}'.format (message))
                    sock.send(message)
            except:
                pass
            logging.info('-------------------------------')

finally:
    logging.info ('closing socket')
    sock.close ()