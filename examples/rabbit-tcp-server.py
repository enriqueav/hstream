

import socket
import sys
import tweepy
import pika
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("HOST")
parser.add_argument("QUEUE")
parser.add_argument("TCP_SRV")
parser.add_argument("TCP_PORT")

args = parser.parse_args()

HOST = args.HOST
QUEUE= args.QUEUE
SRV  = args.TCP_SRV
PORT = int(args.TCP_PORT)

connection = None

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    if connection is not None:
        connection.sendall(body)


if __name__ == '__main__':
    
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the port
    server_address = (SRV, PORT)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    
    # Listen for incoming connections
    sock.listen(1)
    
    while True:
        try:
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = sock.accept()
            print('connection from', client_address)
            
            conn = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
            channel = conn.channel()
            channel.queue_declare(queue=QUEUE)  
            channel.basic_consume(callback, queue=QUEUE, no_ack=True)
            channel.start_consuming()
        
        except KeyboardInterrupt:
            sys.exit()
        
        except: 
            continue

