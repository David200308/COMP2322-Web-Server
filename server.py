import socket
import time
import threading
import os
import sys

## To check the port is used or not, if used +1 and recheck, if not return and use it.
def portCanUse(hostName, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if (sock.connect_ex((hostName, port)) == 0):
        return portCanUse(hostName, port + 1)
    else:
        sock.close()
        return port

HOST = '127.0.0.1'
PORT = 8080 
PORT = portCanUse(HOST, PORT)

## set the http header and log the head to file
def getHeader(statusCode, fileType):
   header = ''
   time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

   if statusCode == 200:
      header += 'HTTP/1.1 200 OK\n'
   elif statusCode == 404:
      header += 'HTTP/1.1 404 Not Found\n'
      
   header += 'Date: ' + time_now + '\n'
   header += 'Connection: keep-alive\n'

   if fileType == 'html':
      header += 'Content-Type: text/html\n\n'
   elif fileType == 'jpg' or fileType == 'jpeg':
      header += 'Content-Type: image/jpeg\n\n'
   elif fileType == 'png':
      header += 'Content-Type: image/png\n\n'
   else:
      header += 'Content-Type: ' + fileType + '\n\n'

   ## Store the header into the log file
   headerArg = header.split('\n')
   logHeaderStr = ''
   for i in range(len(headerArg) - 2):
      logHeaderStr += '[' + headerArg[i] + ']'
   logFile = open((os.getcwd() + "/log.txt"), "a")
   logFile.write(logHeaderStr + '\n')
   logFile.close()

   return header


def webServer(Socket, address):
   perConnection = False
   while True:
      try:
         msg = Socket.recv(1024).decode()  

         ## If no msg recieved, will be close connection
         if not msg:  
            print("No msg recieved, closing connection...")
            Socket.close()
            break

         ## Get request method from client request
         requestMethod = msg.split(' ')[0]
         print("Method: " + requestMethod)

         ## set timeout for 10s 
         if perConnection == False:
            perConnection = True
            Socket.settimeout(10)

         if requestMethod == "GET" or requestMethod == "HEAD":
            try:
               ## Get the requested file from the website address
               fileRequested = msg.split(' ')[1]
               if fileRequested == "/":
                  fileRequested = "/index.html"

               fileType = fileRequested.split('.')[1]
               print("Request: " + fileRequested + "\n")
            except Exception as e:
               print("Error getting filetype/requested file")
               print("Closing client socket...")
               Socket.close()
               break
            
            ## point to the website source folder
            filePath = "./web/" + fileRequested

            ## load and serve file content
            ## if try to get a html/text file request from client
            ## Success --> 200 OK, send header and file source (endcoded) to client
            ## Fail --> 404 Not Found, send header to client
            if fileType == 'html':
               try:
                  if requestMethod == "GET":
                     file = open(filePath, 'r')
                     responseData = file.read()
                     file.close()
                  responseHeader = getHeader(200, fileType)
                  statusCode = 200
               except Exception as e:
                  print("HTML/Text not found, 404 file not found")
                  responseHeader = getHeader(404, fileType)
                  statusCode = 404

               # If request was GET and requested file was read successfully, append the file to the response header
               if requestMethod == "GET" and statusCode == 200:
                  print("Header: \n" + responseHeader)
                  # Encode the response in bytes format so can be sent to client
                  Socket.send(responseHeader.encode() + responseData.encode())
               # Else simply return the response header (HEAD request - 200/404)
               else:
                  print("Header: \n" + responseHeader)
                  Socket.send(responseHeader.encode())
            ## if try to get a image file request from client
            elif fileType == "jpg" or fileType == "jpeg" or fileType == "png":
               try:
                  if requestMethod == "GET":
                     file = open(filePath, 'rb')
                     responseData = file.read()
                     file.close()
                  responseHeader = getHeader(200, fileType)
                  statusCode = 200
               except Exception as e:
                  print("Image not found, 404 file not found")
                  responseHeader = getHeader(404, fileType)
                  statusCode = 404

               ## If request was GET and status is 200 OK, stock will send header and image to client
               if requestMethod == "GET" and statusCode == 200:
                  print("Sending image with: \n" + responseHeader)
                  Socket.send(responseHeader.encode())
                  Socket.send(responseData)
               else:
                  print("Header: \n" + responseHeader)
                  Socket.send(responseHeader.encode())
            # Else trying to request/open an invalid file type
            else:
               print("Invalid Requested Filetype: " + fileType)
               responseHeader = getHeader(404, fileType)
               print("Header: \n" + responseHeader)
               Socket.send(responseHeader.encode())

            ## Want to keep persistent connection after completing request
            if perConnection == True:
               print("Continuing to recieve requests...")
         else:
            print("Error: Unknown HTTP request method: " + requestMethod)
            print("Closing client socket...")
            Socket.close()
            break
      except socket.timeout:
         print("Timeout, closing socket...")
         Socket.close()
         break

## Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

## Point the IP to the port, and release the website address
try:
   s.bind(('127.0.0.1', PORT))
   print("socket binded to", PORT)
   print("Running on -> http://127.0.0.1:" + str(PORT))
except Exception as e:
   print("Error: could not bind to port: " + PORT)
   s.close()
   sys.exit(1)

s.listen(5)

while True:
   Socket, address = s.accept()
   print('Got connection from ',address,'\n')
   threading.Thread(target=webServer, args=(Socket, address)).start()