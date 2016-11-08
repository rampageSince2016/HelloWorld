import socket
import msgpack

srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srvsock.bind(('', 8888))
srvsock.listen(5)

while 1:
    clisock, (remhost, remport) = srvsock.accept()
    Str = clisock.recv(100)
    msg = Str.decode()
    if msg == 'fuck':
        ret_msg = msgpack.dumps({'fuck': 'shit'})
        clisock.send(ret_msg)
    clisock.close()
