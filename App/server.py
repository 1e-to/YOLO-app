import random
import socket, select
from time import gmtime, strftime
from random import randint

imgcounter = 1
basename = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\image%s.png"

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
# 	s.bind((HOST, PORT))
# 	s.listen()
# 	conn, addr = s.accept()
# 	with conn:
# 		print('Connected by', addr)
# 		while True:
# 			data = conn.recv(1024)
# 			if not data:
# 				break
# 			conn.sendall(data)

connected_clients_sockets = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(10)

connected_clients_sockets.append(server_socket)

global_size = 0

while True:

	read_sockets, write_sockets, error_sockets = select.select(connected_clients_sockets, [], [])

	for sock in read_sockets:

		if sock == server_socket:

			sockfd, client_address = server_socket.accept()
			connected_clients_sockets.append(sockfd)

		else:
			try:
				# print("1")
				data = sock.recv(4096)
				# txt = data.decode()
				# txt = str(data)
				# print("txt", txt)

				if data:
					try:
						data = data.decode()
						print(type(data))
						print("2")
						# if data.startswith(' SIZE'):
						if 'SIZE' in data:
							print("3")
							tmp = data.split()
							print("tmp", tmp)
							size = int(tmp[1])
							global_size = size

							print('got size', size)

							sock.sendall(b'GOT SIZE')

						elif 'BYE' in data:
							print("4")
							sock.shutdown()

					except:
						print("5")
						myfile = open(basename % imgcounter, 'wb')
						myfile.write(data)

						data = sock.recv(global_size)
						if not data:
							myfile.close()
							break
						myfile.write(data)
						myfile.close()

						sock.sendall(b'GOT IMAGE')

						sendfile = open(basename % imgcounter, 'rb')
						bytes = sendfile.read()
						size = len(bytes)

						sock.sendall(("SIZE %s" % size).encode())

						answer = sock.recv(4096)
						answer = answer.decode()
						print("answer", answer)

						if answer == 'GOT SIZE':
							sock.sendall(bytes)
							answer = sock.recv(4096)
							print('answer = %s' % answer)

							if answer.decode() == 'GOT IMAGE' :
								print('Image successfully send to client')

						# sock.shutdown()
			except Exception as e:
				print("6")
				print(e)
				# sock.close()
				# connected_clients_sockets.remove(sock)
				continue
		# print("7")
		# imgcounter += 1
server_socket.close()
print("8")
