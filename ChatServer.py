import socket
from Queue import Queue
from threading import Thread
from threading import Lock
import re as regex


# All client stored in the queue
clients = Queue()

roomsArray = {}

valid_join_msg = r"JOIN_CHATROOM: ?(.*)\\nC"


# Client thread to handle multiple client requests
class ClientThread(Thread):
    # Initialize the client thread
    def __init__(self, clients):
        print("Client Thread Initialized")
        Thread.__init__(self)
        self.clients = clients
        self.start()

    # function run when thread is started
    def run(self):
        while True:
            (conn, address) = self.clients.get()
            # If connection object exists process message otherwise exit
            if conn:
                self.process_message(conn, address)
            else:
                break

    # function to process a client request
    @staticmethod
    def process_message(conn, addr):
        while conn:
            message = ""
            # Looping through messages and storing in the string
            while "\n\n" not in message:
                message_content = conn.recv(1024)
                message += message_content.decode()
                if len(message_content) < 1024:
                    break
            # Check if message string have some data or not
            if len(message) > 0:

                if message.startswith("HELO"):
                    conn.sendall(("HELO " + message.split("HELO ", 1)[1] + "\nIP:" + str(addr[0]) + "\nPort:" + str(addr[
                        1]) + "\nStudentID:" + "17310876" + "\n").encode())

                if message.startswith("JOIN_CHATROOM"):
                    createChatRoom(conn, message)


def createChatRoom(conn, message):
    print message
    msg_components = regex.match(valid_join_msg, message, regex.M)
    print msg_components
    if msg_components is not None:
        conn.sendall(("Chat room Created").encode())
    else:
        conn.sendall(("ERROR_CODE: 5\nERROR_DESCRIPTION: Invalid Chatroom join message... Please write the format").encode())


# Main Method: First method to be called
def server_main():
    port = 8080  # Port for connection
    # Ipv4 Socket Family and TCP Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", port))  # Bind with port and host
    s.listen(2)

    # continuous loop to keep accepting client requests
    while True:
        # accept a connection request
        conn, address = s.accept()

        # Initializing the client thread
        ClientThread(clients)

        # receive data and put request in queue
        clients.put((conn, address))


if __name__ == '__main__':
    server_main()
