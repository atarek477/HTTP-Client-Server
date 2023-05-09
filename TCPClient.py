import socket
import re

receive_file = "client_data/Test_.html"

with open("input.txt", 'r') as inputfile:
    for requestMessage in inputfile:
        server = requestMessage.split(' ')[4]
        servername = server.partition(r'\r\n')[0]
        serverip = socket.gethostbyname(servername)
        #print("i am:" + serverip)
        serverport = 9333
        splittedData = requestMessage.split()
        requestType = splittedData[0]
        requestedFile = splittedData[1]
        requestedFile = requestedFile[1:]
        receive_file="client_data/"+requestedFile.rsplit("/",1)[1]
        with open("cached_request.txt", 'r+') as cache:

            if requestMessage in cache and "GET" in str(requestType):
                print("HTTP 304 Not Modified")
                continue
            else:

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
                    address = (serverip, serverport)
                    #print("here")
                    clientSocket.connect(address)

                    # print(requestType)
                    clientSocket.sendall(requestMessage.encode())
                    responseMessage = clientSocket.recv(65536).decode()
                    print('From Server:', responseMessage)

                    if "GET" in str(requestType):


                        if "HTTP/1.1 200 OK" in responseMessage:
                            header = responseMessage.split("\r\n")
                            for hdr in header:
                                if re.search("^Content-Length", hdr):
                                    length = re.findall("[0-9]+", hdr)
                                    break
                            file_length = int(length[0])

                            try:
                                file = open(receive_file, 'wb')
                                buffer = b''
                                while len(buffer) < file_length:
                                    res = clientSocket.recv(10)
                                    buffer = buffer + res
                                file.write(buffer)
                                file.close()
                                cache.write(requestMessage)

                                file_name=requestedFile.rsplit("/",1)[1]
                                with open("cache/"+file_name, 'wb') as cache_file:
                                    cache_file.write(buffer)
                                    cache_file.close()
                            except FileNotFoundError:
                                print("File save error")

                    elif "POST" in str(requestType):
                        requestedFile = splittedData[1]
                        requestedFile = requestedFile[1:]

                        if "OK" in responseMessage:
                            try:
                                file = open(requestedFile, 'rb')
                                buffer = file.read(65536)
                                while buffer:
                                    clientSocket.sendall(buffer)
                                    buffer = file.read(65536)
                                file.close()
                            except:
                                print("Nothing")
                    print("finish")
