import socket
from Queue import Queue
from threading import Thread
from threading import Lock  # For implementing Thread lock
import re as regex  # For pattern matching of input strings from the client
import ChatRoom  # Python class having all functionalities of a ChatRoom
import hashlib  # For unique numbers associated to a string

# Global variables for port and host
port = 0
host = "localhost"

# All client stored in the queue
clients = Queue()

# This array will contain all the details of chat rooms in the memory
chat_rooms_array = {}

# This thread lock will hold other threads until a thread has finished processing, it would create synchronizing Chat room creation and chats
rooms_lock = Lock()

# All the valid input messages to the server from the client
valid_join_msg = r"JOIN_CHATROOM: ?(.*)\\nCLIENT_IP: ?(.*)\\nPORT: ?(.*)\\nCLIENT_NAME: ?(.*)\\n"
valid_hello_msg = r"HELO ?(.*)\\n"

# Various error codes and their description
error_code_5 = "Invalid Message Format... Please write the correct format"


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

    @staticmethod
    def process_message(conn, addr):

        """function to process a client request

        Args:
            conn: the connection parameter acting as a link b/w client and server
            addr: port and ip of the client connected

        """

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
                print "MESSAGE FROM CLIENT->", message
                if message.startswith("HELO"):
                    process_hello_msg(conn, message, addr)

                if message.startswith("JOIN_CHATROOM"):
                    process_join_msg(conn, message)


def process_join_msg(conn, message):
    """function to process join chat request from client

    Args:
        conn: the connection parameter acting as a link b/w client and server
        message: message string from the client

    """

    # Matching the JOIN message with the valid join message template otherwise if false return error
    msg_components = regex.match(valid_join_msg, message, regex.M)
    if msg_components is not None:
        create_chat_room(conn, msg_components.groups()[0], msg_components.groups()[3])
    else:
        send_error_msg_to_client(5, error_code_5)


def process_hello_msg(conn, message, addr):
    """function to process hello request from client, check if server is live or not

    Args:
        conn: the connection parameter acting as a link b/w client and server
        message: message string from the client
        addr: message string from the client

    """

    # Matching the HELO message with the valid HELO message template otherwise if false return error
    msg_components = regex.match(valid_hello_msg, message, regex.M)
    if msg_components is not None:
        send_msg_to_client("HELO " + msg_components.groups()[0] + "\nIP:" + str(addr[0]) + "\nPort:" + str(
            addr[1]) + "\nStudentID:" + "17310876", conn)
    else:
        send_error_msg_to_client(5, error_code_5)


def create_chat_room(conn, chat_room_name, chat_user_name):
    """function to create a new chatroom or initialize user to a existing chat room

    Args:
        conn: the connection parameter acting as a link b/w client and server
        chat_room_name: the name associated to a particular chat room
        chat_user_name: unique name associated with each user

    """

    # Associating uniques hash string to the chat room name and chat user name
    chat_room_id = str(int(hashlib.md5(chat_room_name).hexdigest(), 16))
    chat_user_id = str(int(hashlib.md5(chat_user_name).hexdigest(), 16))

    # Lock this portion such that no other thread can interfere
    rooms_lock.acquire()
    try:
        # Checking if chat room with hash id string exists if not create new
        if chat_room_id not in chat_rooms_array:
            chat_rooms_array[chat_room_id] = ChatRoom.Chatroom(chat_room_name, chat_room_id, chat_user_name,
                                                               chat_user_id)
        room = chat_rooms_array[chat_room_id]
    finally:
        # Release the lock so that other thread can interact
        rooms_lock.release()

    print "RECEIVED FROM CLIENT-> Join request to join chat room named", chat_room_name, "from the user with username", chat_user_name
    send_msg_to_client(room.add_user(conn, port, host), conn)


def send_error_msg_to_client(err_desc, err_code, conn):
    """function to create Error string in proper format with error code and description and then send to the client

    Args:
        err_desc: stating the underlying meaning of the error
        err_code: the numeric code associated with each error
        conn: the connection parameter acting as a link b/w client and server

    """

    print "SENDING ERROR-> Error Code:", str(err_code), "with description", err_desc
    message = "ERROR_CODE: " + str(err_code) + "\nERROR_DESCRIPTION: " + err_desc
    send_error_msg_to_client(message, conn)


def send_msg_to_client(message, conn):
    """function to send processed message to the client

    Args:
        message: message string to be sent to the client
        conn: the connection parameter acting as a link b/w client and server

    """

    print "SENDING MESSAGE TO CLIENT->", message
    if conn:
        conn.sendall((message + "\n").encode())


# Main Method: First method to be called
def server_main():
    global port
    port = 8080  # Port for connection
    # Ipv4 Socket Family and TCP Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))  # Bind with port and host
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
