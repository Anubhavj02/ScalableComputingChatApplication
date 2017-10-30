import socket


def client_main():
    port = 8080
    s = socket.socket()
    s.connect(("localhost", port))
    message = raw_input("Enter Message to be sent to the server-> ")
    while message.lower().strip() != 'exit':
        s.send(message.encode())
        msg = s.recv(1024).decode()
        print('Message Received from server:\n' + msg)
        message = raw_input("Enter Message to be sent to the server-> ")
    s.close()
if __name__ == '__main__':
    client_main()
