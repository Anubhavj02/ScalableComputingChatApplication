import socket


def client_program():
    port = 8080
    s = socket.socket()
    s.connect(("localhost", port))
    message = input("Enter Message to be sent to the server-> ")
    while message.lower().strip() != 'exit':
        s.send(message.encode())
        msg = s.recv(1024).decode()
        print('Message Received from server: ' + msg)
        message = input("Enter Message to be sent to the server-> ")
    s.close()
if __name__ == '__main__':
    client_program()
