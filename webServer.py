import glob
import socket
from _thread import *
import threading
from threading import Thread 
from datetime import datetime
from port import portCanUse
import os
import time

print_lock = threading.Lock()

OK = 'HTTP/1.1 200 OK\r\n'
NOT_MODIFIED = 'HTTP/1.1 304 Not Modified\r\n'
BAD_REQUEST = 'HTTP/1.1 400 Bad Request\r\n'
NOT_FOUND = 'HTTP/1.1 404 Not Found\r\n'
TIMEOUT = 'HTTP/1.1 408 Request Timeout\r\n'

def countdown(t):  
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1
        break
    return 0
  
connectMaxTime = 30

class ClientThread(threading.Thread):
    def __init__(self, address, connection):
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = address
    def run(self):
        print('Connected to ->', self.address[0], ':', self.address[1])
        while True:
            requestData = self.connection.recv(1024).decode('utf-8')
            # if len(requestData) != 'bye':
            #     break

            string_list = requestData.split(' ')
            method = string_list[0]
            requesting_file = string_list[1]
        
            print('Client REQUEST: ',requesting_file)
        
            webFile = requesting_file.split('?')[0]
            webFile = webFile.lstrip('/')
            if(webFile == ''):
                if (glob.glob("./web/index.html")):
                    webFile = './web/index.html'
            else:
                webFile = './web/' + webFile

            try:
                file = open(webFile,'rb')
                response = file.read()
                file.close()
        
                header = 'HTTP/1.1 200 OK\n'

                if(webFile.endswith(".jpg")):
                    contentType = 'image/jpg'
                elif(webFile.endswith(".png")):
                    contentType = 'image/png'
                else:
                    contentType = 'text/html'

                header += 'Date: ' + datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000") + '\n'
                header += 'Connection: ' + 'keep-alive\n'
        
                header += 'Content-Type: ' + str(contentType) + '\n\n'
                # header += "keep-alive", "timeout=5, max=30"
                
                print("REQUEST Status: 200 OK\n")
                
                headerArg = header.split('\n')
                logHeaderStr = ''
                for i in range(len(headerArg) - 2):
                    logHeaderStr += '[' + headerArg[i] + ']'
                logFile = open((os.getcwd() + "/log.txt"), "a")
                logFile.write(logHeaderStr + '\n')
                logFile.close()
                
            except Exception as e:
                print(e)
                # if (FileNotFoundError):
                header = NOT_FOUND
                response = '<html><body><center><h3>Error 404: File not found</h3><p>HTTP Server</p></center></body></html>'.encode('utf-8')

                # header = NOT_MODIFIED
                # response = '<html><body><center><h3>Error 304: Not Modified</h3><p>HTTP Server</p></center></body></html>'.encode('utf-8')

                if (TimeoutError):
                    header = TIMEOUT
                    header += 'Date: ' + datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000") + '\n'
                    logHeaderStr = ''
                    for i in range(len(headerArg) - 2):
                        logHeaderStr += '[' + headerArg[i] + ']'
                    logFile = open((os.getcwd() + "/log.txt"), "a")
                    logFile.write(logHeaderStr + '\n')
                    logFile.close()
                    
                    response = '<html><body><center><h3>Error 408: Request Timeout</h3><p>HTTP Server</p></center></body></html>'.encode('utf-8')

                # header = BAD_REQUEST
                # response = '<html><body><center><h3>Error 400: Bad Request</h3><p>HTTP Server</p></center></body></html>'.encode('utf-8')

            finalResponse = header.encode('utf-8')
            finalResponse += response
            self.connection.send(finalResponse)
            self.connection.close()

            
                

def timeout():
    pass


def server():
    '''
        Create the muti-thread web server which can put the html to web, and can send header and status.
    '''
    
    HOST = '127.0.0.1'
    PORT = 12345
    PORT = portCanUse(HOST, PORT)

    webSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    webSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    webSocket.bind((HOST,PORT))
    webSocket.listen(5)
    webSocket.settimeout(10)

    print('Serving on port', PORT)
    print('Website run on http://'+ HOST + ':'+str(PORT) + '\n')
    
    while True:
        connection, address = webSocket.accept()
        print_lock.acquire()

        newthread = ClientThread(address, connection)
        newthread.start()

if __name__ == '__main__':
    server()