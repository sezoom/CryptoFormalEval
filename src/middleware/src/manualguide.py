#!../venv/bin/python
import sys
import socket

host = '127.0.0.1'
port = 12358

# Retrieve the goal's name and the list of possible choices from the input
goal = sys.argv[1]
choices = sys.stdin.readlines()

# If there are less than two possible goals, provide the default value
if len(choices) <= 1 :
    print(0)
else :
    # If there are multiple choices, connect (as a client) to the middleware's server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        # Communicate the name of the intermediate goal and the set of possible choices back to the middleware
        message = f"Goal: {goal}\n" + "".join(choices)
        s.sendall(message.encode())
        # Retrieve the choice from the middleware
        data = s.recv(1024)
        # Return the choice to Tamarin
        print(data.decode())