import socket
import hashlib
import sys


def client_main():

    if len(sys.argv) < 2:
        sys.exit("Please give the port number")

    port = int(sys.argv[1])

    client_name = ""
    room_name = ""
    message = ""

    # take the values from command line arguments otherwise use defaults
    if len(sys.argv) >= 3:
        client_name = sys.argv[2]
    else:
        client_name = "client1"

    if len(sys.argv) >= 4:
        room_name = sys.argv[3]
    else:
        room_name = "room"

    if len(sys.argv) >= 5:
        message = sys.argv[3]
    else:
        message = "room"

    host = socket.gethostbyname(socket.gethostname())
    s = socket.socket()
    s.connect((host, port))

    # Messages to be sent to the chat server
    hello_msg = "HELO " + client_name + "\n"
    join_msg = "JOIN_CHATROOM: " + room_name + "\nCLIENT_IP: 0\nPORT: 0\nCLIENT_NAME: " + client_name
    chat_msg = "CHAT: " + str(int(hashlib.md5(room_name).hexdigest(), 16)) + "\nJOIN_ID: " + str(
        int(hashlib.md5(client_name).hexdigest(), 16)) + "\nCLIENT_NAME: " + client_name + "\nMESSAGE: " + message
    leave_msg = "LEAVE_CHATROOM: " + str(int(hashlib.md5(room_name).hexdigest(), 16)) + "\nJOIN_ID: " + str(
        int(hashlib.md5(client_name).hexdigest(), 16)) + "\nCLIENT_NAME: " + client_name
    disconn_msg = "DISCONNECT: 0\nPORT: 0\nCLIENT_NAME: " + client_name

    # send message to the chat server
    send_receive_msg(s, hello_msg)
    send_receive_msg(s, join_msg)
    send_receive_msg(s, leave_msg)
    send_receive_msg(s, chat_msg)
    send_receive_msg(s, disconn_msg)
    s.close()


def send_receive_msg(s, msg):
    s.send(msg.encode())
    msg = s.recv(1024).decode()
    print('Message Received from server:\n' + msg)

if __name__ == '__main__':
    client_main()
