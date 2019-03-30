# fakebox
- this program is a simple dropbox prototype written in Python 3.6.2
- client.py and server.py can be run on the same machine or different ones
- if ran on the same machine, client.py and server.py should be executed from separate directories
- multiple instances of client.py can connect to one instance of server.py simultaneously
- both client.py and server.py need a directory named 'file' located in the same directories as them to store shared files
- both also need a file.log file located in the same directory to keep track of shared files
- to upload files to the server from the client they must be in the same directory as client.py
