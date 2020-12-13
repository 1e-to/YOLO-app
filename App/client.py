import random
import socket, select
from time import gmtime, strftime
from random import randint

import sys
import numpy as np
import cv2
import os

image = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\tux.png"
image_re = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\tux_re.png"

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
sock.connect(server_address)

global_size = 0
limit = 0

filename_ = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\out1.avi"
out = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\out.avi"
img_process = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\img_process.png"

codec = cv2.VideoWriter_fourcc(*'XVID')
writer = cv2.VideoWriter(out,codec, 25.0, (400,300))
# writer = cv2.VideoWriter(out,codec, 25.0, (640,480))
# writer = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*"MJPG"), 25,(640,480))


vid = cv2.VideoCapture(filename_)
# vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)


while(vid.isOpened()):
	ret, frame = vid.read()
	if cv2.waitKey(1) & 0xFF == ord('q') or ret == False or limit >=100:
		break
	cv2.imwrite(img_process, frame)
	# im = cv2.imread(img_process)
	

# for i in range(3):
	try:
		print("1")
		# myfile = open(image, 'rb')
		myfile = open(img_process, 'rb')
		bytes = myfile.read()
		size = len(bytes)
		print("2")
		print("size", size)

	    # send image size to server
		# sock.sendall(b"SIZE %s" % size)
		sock.sendall(("SIZE %s" % size).encode())
		answer = sock.recv(4096)
		answer = answer.decode()
		print("answer", answer)
		# print('answer = %s' % answer)

	    # send image to server
		if answer == 'GOT SIZE':
			print("3")
			sock.sendall(bytes)

	        # check what server send
			answer = sock.recv(4096)
			print('answer = %s' % answer)

			if answer.decode() == 'GOT IMAGE' :
				data = sock.recv(4096)
				data = data.decode()
				if 'SIZE' in data:
					print("3")
					tmp = data.split()
					print("tmp", tmp)
					size = int(tmp[1])
					global_size = size

					print('got size', size)
					sock.sendall(b'GOT SIZE')

					data = sock.recv(4096)
					myfile = open(image_re, 'wb')
					myfile.write(data)

					data = sock.recv(global_size)
					# if not data:
					# 	myfile.close()
					# 	break
					myfile.write(data)
					myfile.close()

					sock.sendall(b'GOT IMAGE')

				# sock.sendall(b'BYE BYE')
				print('Image successfully send to server')

		myfile.close()
		print("4")

	finally:
		# sock.close()
		im = cv2.imread(image_re)
		writer.write(im)
		limit +=1
		print("5")


writer.release()
vid.release()
cv2.destroyAllWindows()

sock.sendall(b'BYE BYE')
sock.close()
