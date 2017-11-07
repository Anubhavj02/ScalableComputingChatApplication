# Scalable Computing Chat Server
Centralised Chat Server with chat room functionality

>Name: Anubhav Jain
<br>TCD Student ID: 17310876

This chat server can support multiple clients where clients can join chat rooms, post messages and retrieve messages, and leave chat rooms.

### Dependencies Required
* Python 2.7

### Starting the server
First clone the repository and then in command line/ terminal type....
```
sh start.sh {port_number}
```
where port number is port where you want to start the server

### Demo Testing of the Server from a test client
ChatClient.py is a demo client file that tests the common commands of the server
```
python ChatClient.py {port_number}
```

### Commands and Response from the server
* #### HELLO message to the server
  Request
  ```
  "HELO text\n"
  ```
  Response
  ```
  "HELO text\nIP:[ip address]\nPort:[port number]\nStudentID:[your student ID]\n"
  ```
  
* #### JOIN message to the server
  Request
  ```
  JOIN_CHATROOM: [chatroom name]
	CLIENT_IP: [IP Address of client if UDP | 0 if TCP]
	PORT: [port number of client if UDP | 0 if TCP]
	CLIENT_NAME: [string Handle to identifier client user]
  ```
  Response
  ```
  JOINED_CHATROOM: [chatroom name]
	SERVER_IP: [IP address of chat room]
	PORT: [port number of chat room]
	ROOM_REF: [integer that uniquely identifies chat room on server]
  JOIN_ID: [integer that uniquely identifies client joining]
  ```
  
* #### LEAVE message to the server
  Request
  ```
  LEAVE_CHATROOM: [ROOM_REF]
	JOIN_ID: [integer previously provided by server on join]
	CLIENT_NAME: [string Handle to identifier client user]
  ```
  Response
  ```
  LEFT_CHATROOM: [ROOM_REF]
	JOIN_ID: [integer previously provided by server on join]
  ```
  

