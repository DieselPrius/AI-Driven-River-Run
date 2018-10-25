import os
import socket
import subprocess

s = socket.socket()

sox = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sox.connect(("8.8.8.8", 80))
print(sox.getsockname()[0])

host = sox.getsockname()[0]
sox.close()
port = 4444

x = 1
while x:
    try:
        s.connect((host, port))
    except:
        continue
    x = 0

i = 0
while 1:
    data = s.recv(1024)
    print(data)
    if len(data) > 0:
        if i%2 == 0:
            output_str = "RIGHT"
        else:
            output_str = "PASS"
        i += 1
        s.send(str.encode(output_str))

s.close()