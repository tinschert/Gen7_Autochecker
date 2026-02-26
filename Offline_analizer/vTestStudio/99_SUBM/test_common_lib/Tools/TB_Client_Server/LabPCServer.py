import socket
import time
import subprocess
import traceback

# For test on local laptop
#TCP_IP_ADDRESS = '127.0.0.1'

TCP_IP_ADDRESS = '192.168.0.5'
TCP_PORT_NO = 5555

# For test on local laptop
#CLIENT_ADDRESS = '127.0.0.1'

CLIENT_ADDRESS = '192.168.0.2'

conn = None
addr = None
serverSock = None

##
# Accept the connection from the client on the RT rack.
# But only if the connection was established from the RT rack client with address CLIENT_ADDRESS.
#
def acceptConnection():
    global conn, addr, serverSock
    
    # wait to accept a connection - blocking call
    conn, addr = serverSock.accept()

    if addr[0] != CLIENT_ADDRESS:
        closeConnection()
        print('Rejected connection from ' + addr[0] + ':' + str(addr[1]))
    else:
        # display client information
        print('Connected with ' + addr[0] + ':' + str(addr[1]))

##
# Close the TCP connection.
#
def closeConnection():
    global conn

    if conn != None:
        print('Close connection to ' + addr[0] + ':' + str(addr[1]))
        conn.close()
        conn = None

##
# Execute the command sent by the client.
#
def executeCmd(cmd):
    try:
        returnval = subprocess.call(cmd)
        print('returnval: %d' % returnval)

    except:
        traceback.print_exc()
    
    return returnval

##
# 
#
def main():
    global serverSock

    execCmdReturnCode = 0

    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.bind((TCP_IP_ADDRESS, TCP_PORT_NO))

    # listen for only one connection
    serverSock.listen(1)

    acceptConnection()

    while True:

        try:
            if conn != None:
                # now keep talking with the client
                data = conn.recv(4096)
                if not data:
                    time.sleep(1)
                    continue

                # remove NULL bytes
                data = data.replace('\x00', '')
                print('data: %s\n' % data)

                try:
                    execCmdReturnCode = executeCmd(data)
                except:
                    traceback.print_exc()

                conn.sendall(str(execCmdReturnCode))
            else:
                print('conn == None')
            
            closeConnection()
            
            # wait to accept a connection - blocking call
            acceptConnection()

        except (KeyboardInterrupt, SystemExit):
            closeConnection()
            raise
        
        except Exception:

            traceback.print_exc()

            closeConnection()
            
            # wait to accept a connection - blocking call
            acceptConnection()


##
# Call the main function.
#            
main()