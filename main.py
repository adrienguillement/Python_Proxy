# coding: utf-8

import socket, sys
from _thread import start_new_thread

try:
    listening_port = int(input("[*] Enter listening port number : "))
except KeyboardInterrupt:
    print("\n[*] User Requested An Interrupt.")
    print("[*] Program Exiting...")

max_connection = 4
buffer_size = 4096


def start():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Initialize socket
        print("[*] Initializing Sockets... Done")
        s.bind(('', listening_port))  # Bind Socket
        print("[*] Sockets Binded Successfully...")
        s.listen(max_connection)  # Start Listening for connection
        print("[*] Server Started Successfully [ {} ]".format(listening_port))
    except Exception as e:
        print("[*] Unable To Initialize Socket")
        sys.exit(1)

    while True:
        try:
            connection, address = s.accept()  # Accept Connection From Client Browser
            data = connection.recv(buffer_size)  # Receive Client Data
            start_new_thread(connection_string, (connection, data, address))  # Start A Thread
        except KeyboardInterrupt:
            s.close()
            print("\n[*] Proxy Server Shutting Down... Done")
            sys.exit(1)
    s.close()


def connection_string(connection, data, address):
    """
    Client Browset Request Appears Here
    This function retreive the host address and port
    """
    try:
        data = data.decode('UTF-8')
        first_line = data.split('\n')[0]

        url = first_line.split(' ')[1]

        http_pos = url.find('://')
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos+3):]

        port_pos = temp.find(":")
        webserver_pos = temp.find('/')
        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos):
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]

        proxy_server(webserver, port, connection, address, data)
    except Exception as e:
        print(e)


def proxy_server(webserver, port, connection, data, addr):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        data_string = ''.join(str(x) for x in data)
        s.sendall(data_string.encode())

        while True:
            reply = s.recv(buffer_size)

            if len(reply) > 0:
                connection.send(reply)  # Send reply back to client

                dar = float(len(reply))
                dar = float(dar / 1024)
                dar = "{}.3s".format(str(dar))
                dar = "{} KB".format(dar)

                print("[*] Request Done : {} => {} <=".format(str(addr), str(dar)))
            else:
                break
        s.close()
        connection.close()
    except socket.error:
        s.close()
        connection.close()
        sys.exit(1)

start()