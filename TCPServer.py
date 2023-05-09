import os
import socket
import threading
import  time

def pipelinethread(connectionSocket):
    global timeout
    timeout = time.time()
    try :
        connectionSocket.setblocking(False)
        data = connectionSocket.recv(65536).decode()

        timeout= time.time() + 10

        if data :

            threading.Thread(target=pipelinethread, args=(connectionSocket,)).start()

            print("what we got from client " + str(data))
            splittedData = data.split()
            requestType = splittedData[0]

            requestedFile = splittedData[1]
            requestedFile = requestedFile[1:]
            if requestedFile == "":
                requestedFile = "data.html"

            if "GET" in str(requestType):
                try:
                    file = open(requestedFile, 'rb')
                    file_length = os.path.getsize(requestedFile)
                    # print(file_length)
                    header = f'HTTP/1.1 200 OK\r\nContent-Length: {file_length}\r\n\r\n'
                    connectionSocket.sendall(header.encode())
                    buffer = file.read(65536)
                    while buffer:
                        # print(buffer)
                        connectionSocket.sendall(buffer)
                        buffer = file.read(65536)
                    file.close()
                except FileNotFoundError:
                    header = 'HTTP/1.0 404 Not Found\r\n\r\n'
                    connectionSocket.sendall(header.encode())


            elif "POST" in str(requestType):
                header = "OK"
                connectionSocket.sendall(header.encode())
                buffer = connectionSocket.recv(65536)
                try:
                    file_name = requestedFile.rsplit("/", 1)[1]
                    file = open("server_data/" + file_name, 'wb')
                    file.write(buffer)
                    file.close()

                except FileNotFoundError:
                    print("File save error")

            if "HTTP/1.1" in str(splittedData):
                # print('hh')
                #connectionSocket.settimeout(8)
                #clientThreadHandler(connectionSocket)
                pass
    except :

        while True:
            if time.time() > timeout:
                print("close pipelined thread")
                break


def clientThreadHandler(connectionSocket):
    global timeout
    timeout = time.time()
    try:
       data = connectionSocket.recv(65536).decode()
       threading.Thread(target=pipelinethread, args=(connectionSocket,)).start()

       if data:
           #print(len(data))
           connectionSocket.settimeout(None)
       else:
           return
    except :
        print("here except")

    print("what we got from client " + str(data))
    splittedData = data.split()
    requestType = splittedData[0]

    requestedFile = splittedData[1]
    requestedFile = requestedFile[1:]


    if "GET" in str(requestType):
        try:
            file = open(requestedFile, 'rb')
            file_length = os.path.getsize(requestedFile)
            #print(file_length)
            header = f'HTTP/1.1 200 OK\r\nContent-Length: {file_length}\r\n\r\n'
            connectionSocket.sendall(header.encode())
            buffer = file.read(65536)
            while buffer:
               # print(buffer)
                connectionSocket.sendall(buffer)
                buffer = file.read(65536)
            file.close()
        except FileNotFoundError:
            header = 'HTTP/1.0 404 Not Found\r\n\r\n'
            connectionSocket.sendall(header.encode())


    elif "POST" in str(requestType):
        header = "OK"
        connectionSocket.sendall(header.encode())
        buffer = connectionSocket.recv(65536)
        try:
            file_name = requestedFile.rsplit("/", 1)[1]
            file = open("server_data/" + file_name, 'wb')
            file.write(buffer)
            file.close()

        except FileNotFoundError:
            print("File save error")

    if "HTTP/1.1" in str(splittedData):
        #print('hh')

        timeout=time.time()+10
        while True:
           if time.time()>timeout :
               print("main thread timeout")
               break
        #clientThreadHandler(connectionSocket)
    #print("hi")
    # connectionSocket.close()


if __name__ == "__main__":


    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket Created")

    ip = socket.gethostbyname(socket.gethostname())
    port = 9333
    address = (ip, port)
    serverSocket.bind(address)
    print("Socket has been bounded")


    while True:
        serverSocket.listen(1)
        connectionSocket, address = serverSocket.accept()
        print("Got a connection from " + str(address[0]) + " | " + str(address[1]))
        print("Server started listening on ip: " + str(ip) + " | port:" + str(port))
        threading.Thread(target=clientThreadHandler, args=(connectionSocket,)).start()

