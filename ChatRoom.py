from threading import Lock


class Chatroom:

    """
    This class has all the attributes and functions related to chat room
    """

    def __init__(self, chat_room_name, chat_room_id, chat_user_name, chat_user_id):
        self.chat_room_name = chat_room_name
        self.chat_room_id = chat_room_id
        self.chat_user_name = chat_user_name
        self.chat_user_id = chat_user_id
        self.chat_room_users = {}
        self.chat_room_lock = Lock()

    def add_user(self, conn, port, host):
        # Lock the flow to enable sync between threads
        self.chat_room_lock.acquire()
        try:
            # Adding details of the user w.r.t user id
            self.chat_room_users[self.chat_user_id] = (self.chat_user_name, conn)
        finally:
            # Releasing the lock
            self.chat_room_lock.release()

        return "JOINED_CHATROOM: " + self.chat_room_name + "\nSERVER_IP: " + str(host) + "\nPORT: " + str(port) + "\nROOM_REF: " + str(self.chat_room_id) + "\nJOIN_ID: " + str(self.chat_user_id)