import socket
from Queue import Queue
from threading import Thread
from threading import Lock  # For implementing Thread lock
import re as regex  # For pattern matching of input strings from the client
import hashlib  # For unique numbers associated to a string
import os  # for using the exit function
import sys

# Global variables for port and host
port = 0
host = ""

# All client stored in the queue
clients = Queue()

# This array will contain all the details of chat rooms in the memory
chat_rooms_array = {}

# This thread lock will hold other threads until a thread has finished processing,
# it would create synchronizing Chat room creation and chats
rooms_lock = Lock()

# All the valid input messages to the server from the client
valid_join_msg = r"JOIN_CHATROOM: ?(.*)(?:\s|\\n)CLIENT_IP: ?(.*)(?:\s|\\n)PORT: ?(.*)(?:\s|\\n)CLIENT_NAME: ?(.*)"
valid_hello_msg = r"HELO ?(.*)\s"
valid_leave_msg = r"LEAVE_CHATROOM: ?(.*)(?:\s|\\n)JOIN_ID: ?(.*)(?:\s|\\n)CLIENT_NAME: ?(.*)"
valid_chat_msg = r"CHAT: ?(.*)(?:\s|\\n)JOIN_ID: ?(.*)(?:\s|\\n)CLIENT_NAME: ?(.*)(?:\s|\\n)MESSAGE: ?(.*)"
valid_disconnect_msg = r"DISCONNECT: ?(.*)(?:\s|\\n)PORT: ?(.*)(?:\s|\\n)CLIENT_NAME: ?(.*)"

# Various error codes and their description
error_code_1 = "Invalid Message Format... Please write the correct format"
error_code_2 = "No Chat room exists with the Chat Room Ref-"


class Chatroom:
    """
    This class has all the attributes and functions related to chat room
    """

    def __init__(self, chat_room_name, chat_room_id):
        """Constructor to initialize the chat room object

            Args:
                chat_room_name: the name of the chat room
                chat_room_id: the id uniquely associated to particular chat room

        """

        self.chat_room_name = chat_room_name
        self.chat_room_id = chat_room_id
        self.chat_room_users = {}
        self.chat_room_lock = Lock()

    def add_user_to_chat_room(self, conn, port, host, chat_user_id, chat_user_name):
        """this function adds user to a chat room

            Args:
                conn: the connection parameter acting as a link b/w client and server
                port: the port of the connection
                host: host ip of the connection
                chat_user_id: id associated to a particular user
                chat_user_name: name associated with each user

        """

        # Lock the flow to enable sync between threads
        self.chat_room_lock.acquire()
        try:
            # Adding details of the user w.r.t user id
            self.chat_room_users[chat_user_id] = (chat_user_name, conn)
            print len(self.chat_room_users), self.chat_room_users
        finally:
            # Releasing the lock
            self.chat_room_lock.release()

        #  Returning the response after addition is complete
        return "JOINED_CHATROOM: " + self.chat_room_name + "\nSERVER_IP: " + str(host) + "\nPORT: " + str(
            port) + "\nROOM_REF: " + str(self.chat_room_id) + "\nJOIN_ID: " + str(chat_user_id)

    def send_chat_msg(self, source_user, msg):
        """this function send message to all the users in the chat room

            Args:
                source_user: the source user of the message
                msg: message to be sent in the chat room

        """

        #  Array that contains the connection details of all the users in chat room
        user_conns = []
        # Lock the flow to enable sync between threads
        self.chat_room_lock.acquire()
        try:
            user_conns = self.chat_room_users.values()
        finally:
            self.chat_room_lock.release()
        print user_conns
        # Loop through all the user connections and send them the message
        for dest_user, dest_conn in user_conns:
            send_msg_to_client("CHAT:" + str(self.chat_room_id) + "\nCLIENT_NAME:" + str(source_user) + "\nMESSAGE:" + msg + "\n",
                dest_conn)

    def remove_user_from_chat_room(self, chat_user_id, chat_user_name, conn):
        """this function removes the user from the chat room

            Args:
                chat_user_id: id associated to a particular user
                chat_user_name: name associated with each user
                conn: the connection parameter acting as a link b/w client and server

        """

        # Lock the flow to enable sync between threads
        self.chat_room_lock.acquire()
        try:
            # remove the userid from the list of users in the chat room if exits
            if chat_user_id in self.chat_room_users:
                if self.chat_room_users[chat_user_id][0] == chat_user_name:
                    del self.chat_room_users[chat_user_id]
                else:
                    #  If user does not exist send error message
                    send_error_msg_to_client("the username " + chat_user_name + " does not exists", 3, conn)
                    return
        finally:
            self.chat_room_lock.release()

    def disconnect_user_from_chat_room(self, chat_user_id, chat_user_name, conn):
        """this function disconnects the user from the chat room

            Args:
                chat_user_id: id associated to a particular user
                chat_user_name: name associated with each user
                conn: the connection parameter acting as a link b/w client and server

        """

        # Lock the flow to enable sync between threads
        self.chat_room_lock.acquire()
        try:
            # checking if user belongs to chat room if not give error and return
            if chat_user_id not in self.chat_room_users:
                return
        finally:
            self.chat_room_lock.release()
        # broadcast message to all chat room users
        self.send_chat_msg(chat_user_name, chat_user_name + " has left this chatroom.")
        self.chat_room_lock.acquire()
        try:
            del self.chat_room_users[chat_user_id] # delete the user from the array
        finally:
            self.chat_room_lock.release()


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

                #  Check the type of message and process them accordingly
                if message == "KILL_SERVICE\n":
                    os._exit(0)

                if message.startswith("HELO"):
                    process_hello_msg(conn, message, addr)

                if message.startswith("JOIN_CHATROOM"):
                    process_join_msg(conn, message)

                if message.startswith("LEAVE_CHATROOM"):
                    process_leave_msg(conn, message)

                if message.startswith("CHAT"):
                    process_chat_msg(conn, message)

                if message.startswith("DISCONNECT"):
                    process_disconnect_msg(conn, message)
                    conn.shutdown(1)
                    conn.close()
                    break


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
        send_error_msg_to_client(error_code_1, 1, conn)


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
        send_msg_to_client("HELO " + msg_components.groups()[0] + "\nIP:" + str(host) + "\nPort:" + str(port) + "\nStudentID:" + "17310876", conn)
    else:
        send_error_msg_to_client(error_code_1, 1, conn)


def process_leave_msg(conn, message):
    """function to process leave chat room request from client

        Args:
            conn: the connection parameter acting as a link b/w client and server
            message: message string from the client

    """

    # Matching the LEAVE message with the valid leave message template otherwise if false return error
    msg_components = regex.match(valid_leave_msg, message, regex.M)
    if msg_components is not None:
        delete_from_chat_room(conn, msg_components.groups()[0], msg_components.groups()[1], msg_components.groups()[2])
    else:
        send_error_msg_to_client(error_code_1, 1, conn)


def process_chat_msg(conn, message):
    """function to initiate chat request from the user

        Args:
            conn: the connection parameter acting as a link b/w client and server
            message: message string from the client

    """

    # Matching the CHAT message with the valid chat message template otherwise if false return error
    msg_components = regex.match(valid_chat_msg, message, regex.M)
    if msg_components is not None:
        broadcast_msg_chatroom_users(conn, msg_components.groups()[0], msg_components.groups()[1], msg_components.groups()[2], msg_components.groups()[3])
    else:
        send_error_msg_to_client(error_code_1, 1, conn)


def process_disconnect_msg(conn, message):
    """function to process disconnect request from all the chat rooms and the server

        Args:
            conn: the connection parameter acting as a link b/w client and server
            message: message string from the client

    """

    # Matching the DISCONNECT message with the valid disconnect message template otherwise if false return error
    msg_components = regex.match(valid_disconnect_msg, message, regex.M)
    if msg_components is not None:
        disconnect_user_from_chatroom(conn, msg_components.groups()[2])
    else:
        send_error_msg_to_client(error_code_1, 1, conn)


def disconnect_user_from_chatroom(conn, chat_user_name):
    """function to disconnect user from all the chat rooms that the user was part of

        Args:
            conn: the connection parameter acting as a link b/w client and server
            chat_user_name: name associated to a user

    """

    chat_user_id = str(int(hashlib.md5(chat_user_name).hexdigest(), 16))
    rooms = []
    print "RECEIVED FROM CLIENT->", chat_user_name, "has requested to disconnect from all the chat rooms"
    # Lock this portion such that no other thread can interfere
    rooms_lock.acquire()
    try:
        rooms = chat_rooms_array.values()
    finally:
        # Release the lock so that other thread can interact
        rooms_lock.release()
    #  Sort the rooms array as aplhabetical order of room name
    rooms = sorted(rooms, key=lambda x: x.chat_room_name)
    #  Iterate through all the rooms and disconnect the user from its associated chat room
    for r in rooms:
        r.disconnect_user_from_chat_room(chat_user_id, chat_user_name, conn)


def broadcast_msg_chatroom_users(conn, chat_room_id, chat_user_id, chat_user_name, msg):
    """function to broadcast user chat message to all the users of the specified chat room

        Args:
            conn: the connection parameter acting as a link b/w client and server
            chat_room_id: the unique id associated to a room to whose users the message is to be broadcasted
            chat_user_id: unique id associated to a user
            chat_user_name: name associated to a user
            msg: the message to be transmitted

    """
    room = None
    # Lock this portion such that no other thread can interfere
    rooms_lock.acquire()
    try:
        # Checking if chat room with hash id string exists if not throw an error
        if chat_room_id not in chat_rooms_array:
            send_error_msg_to_client(error_code_1 + chat_room_id, 1, conn)
            return
        #  If exist fetch the details in the object
        room = chat_rooms_array[chat_room_id]
    finally:
        # Release the lock so that other thread can interact
        rooms_lock.release()
    print "RECEIVED FROM CLIENT-> User with uername", chat_user_name, "has initiated chat in the room(", room.chat_room_name, ")"
    room.send_chat_msg(chat_user_name, msg)


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
            chat_rooms_array[chat_room_id] = Chatroom(chat_room_name, chat_room_id)
        room = chat_rooms_array[chat_room_id]
    finally:
        # Release the lock so that other thread can interact
        rooms_lock.release()

    print "RECEIVED FROM CLIENT-> Join request to join chat room named", chat_room_name, "from the user with username", chat_user_name
    #  Send chat room details and response to the client
    send_msg_to_client(room.add_user_to_chat_room(conn, port, host, chat_user_id, chat_user_name), conn)
    #  Send message to all the users of the chat room- a new user has joined
    room.send_chat_msg(chat_user_name, chat_user_name + "has joined the chat room")


def delete_from_chat_room(conn, chat_room_id, chat_user_id, chat_user_name):
    """function to delete a user assocaited from a specific chat room

    Args:
        conn: the connection parameter acting as a link b/w client and server
        chat_room_id: the id uniquely associated to particular chat room
        chat_user_id: id of the user who has to be delete from chat room
        chat_user_name: unique name associated with each user

    """

    room = None

    # Lock this portion such that no other thread can interfere
    rooms_lock.acquire()
    try:
        # Checking if chat room with hash id string exists if not throw an error
        if chat_room_id not in chat_rooms_array:
            send_error_msg_to_client(error_code_1 + chat_room_id, 1, conn)
            return
        #  If exist fetch the details in the object
        room = chat_rooms_array[chat_room_id]
    finally:
        # Release the lock so that other thread can interact
        rooms_lock.release()

    # Send response back to the client that leave process was successful
    send_msg_to_client("LEFT_CHATROOM: " + str(chat_room_id) + "\nJOIN_ID: " + str(chat_user_id), conn)
    #  Inform other users in the chat room that a particular user has left
    room.send_chat_msg(chat_user_name, chat_user_name + " has left this chatroom.")
    #  Remove user details from chat room
    room.remove_user_from_chat_room(chat_user_id, chat_user_name, conn)


def send_error_msg_to_client(err_desc, err_code, conn):
    """function to create Error string in proper format with error code and description and then send to the client

    Args:
        err_desc: stating the underlying meaning of the error
        err_code: the numeric code associated with each error
        conn: the connection parameter acting as a link b/w client and server

    """

    print "SENDING ERROR-> Error Code:", str(err_code), "with description", err_desc
    message = "ERROR_CODE: " + str(err_code) + "\nERROR_DESCRIPTION: " + err_desc
    send_msg_to_client(message, conn)


def send_msg_to_client(message, conn):
    """function to send processed message to the client

    Args:
        message: message string to be sent to the client
        conn: the connection parameter acting as a link b/w client and server

    """

    print "SENDING MESSAGE TO CLIENT->\n", message
    if conn:
        conn.sendall((message + "\n").encode())


# Main Method: First method to be called
def server_main():
    global port, host

    print "Starting Server"

    if len(sys.argv) != 2:
        sys.exit("Please give the port number")

    port = int(sys.argv[1])  # Port for connection
    # Ipv4 Socket Family and TCP Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostbyname(socket.gethostname())
    s.bind((host, port))  # Bind with port and host
    s.listen(5)

    # continuous loop to keep accepting client requests
    while True:

        print "Server started waiting for connections...."

        # accept a connection request
        conn, address = s.accept()

        # Initializing the client thread
        ClientThread(clients)

        # receive data and put request in queue
        clients.put((conn, address))


if __name__ == '__main__':
    server_main()