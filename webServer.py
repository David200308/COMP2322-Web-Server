import glob
import socket
from _thread import *
import threading
from port import portCanUse

print_lock = threading.Lock()

def threaded(c, data):
    '''
        Create the thread for each client, and set connect timer is 30 sec per connection (with no data transfer).
    '''
    timer = 30
    while True:
        # data = c.recv(1024).decode('utf-8')
        timer = timer - 1
        if (not data and timer == 0):
            print('Disconnect')
            print_lock.release()
            break
        data = data[::-1]
        # c.send(data)
    c.close()

def server():
    '''
        Create the muti-thread web server which can put the html to web, and can send header and status.
    '''
    
    HOST = '127.0.0.1'
    PORT = 12345
    PORT = portCanUse(HOST, PORT)

    my_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    my_socket.bind((HOST,PORT))
    my_socket.listen(1)

    print('Serving on port',PORT)
    print('Website run on http://'+ HOST + ':'+str(PORT))
    
    while True:
        connection, address = my_socket.accept()
        print_lock.acquire()
        print('Connected to ->', address[0], ':', address[1])
        requestData = connection.recv(1024).decode('utf-8')
        start_new_thread(threaded, (connection, requestData))
        string_list = requestData.split(' ')
    
        method = string_list[0]
        requesting_file = string_list[1]
    
        print('Client request ',requesting_file)
    
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
                mimetype = 'image/jpg'
            elif(webFile.endswith(".css")):
                mimetype = 'text/css'
            else:
                mimetype = 'text/html'
    
            header += 'Content-Type: '+str(mimetype)+'\n\n'
    
        except Exception as e:
            header = 'HTTP/1.1 404 Not Found\n\n'
            response = '<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode('utf-8')
    
        final_response = header.encode('utf-8')
        final_response += response
        connection.send(final_response)
        connection.close()

if __name__ == '__main__':
    server()