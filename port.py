import socket

def portCanUse(hostName, port):
    '''
        Checking the port is used or not, if used +1 and recheck, if not return and use it.
    '''

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if (sock.connect_ex((hostName, port)) == 0):
        return portCanUse(hostName, port + 1)
    else:
        sock.close()
        print("port can use", port)
        return port
