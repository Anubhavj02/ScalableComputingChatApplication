import socket


def server_main():
    port = 8080
    s = socket.socket()
    s.bind(("localhost", port))
    s.listen(2)
    conn, add = s.accept()
    print("Client connected from address" + str(add))
    while True:
        msg = conn.recv(1024).decode()
        if not msg:
            break
        print("Data from user: " + str(msg))
        msg = input('Enter data to be sent to the user->')
        conn.send(msg.encode())
    conn.close()
if __name__ == '__main__':
    server_main()
