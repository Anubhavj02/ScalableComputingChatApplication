# Scalable Computing Chat Server
Centralised Chat Server with chat room functionality

>Name: Anubhav Jain
<br>TCD Student ID: 17310876

This chat server can support multiple clients where clients can join chat rooms, post messages and retrieve messages, and leave chat rooms.

### Dependencies Required
* Python 2.7

### Starting the server
First clone the repository and then in command line/ terminal type....
'''python
sh start.sh {port_number}
'''

where port number is port where you want to start the server

### Demo Testing of the Server from a test client
ChatClient.py is a demo client file that tests the common commands of the server
  > python ChatClient.py {port_number}

### Commands and Response from the server
* #### Hello message to the server
Request
  > "HELO text\n"

Response
  > "HELO text\nIP:[ip address]\nPort:[port number]\nStudentID:[your student ID]\n"

