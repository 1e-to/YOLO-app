import socket
import numpy as np
import cv2


image_result = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\result.png"

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
sock.connect(server_address)

global_size = 0
limit = 0

video_filename = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\out1.avi"
out = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\out.avi"
img_process = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\img_process.png"

codec = cv2.VideoWriter_fourcc(*'XVID')
writer = cv2.VideoWriter(out, codec, 25.0, (1920,1080))
# writer = cv2.VideoWriter(out,codec, 25.0, (640,480))
# writer = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*"MJPG"), 25,(640,480))
vid = cv2.VideoCapture(video_filename)
# vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while(vid.isOpened()):
	ret, frame = vid.read()
	if cv2.waitKey(1) & 0xFF == ord('q') or ret == False or limit >=100:
		break
	cv2.imwrite(img_process, frame)

	try:
		myfile = open(img_process, 'rb')
		bytes = myfile.read()
		size = len(bytes)

	    # send image size to server
		sock.sendall(("SIZE %s" % size).encode())
		answer = sock.recv(4096)
		answer = answer.decode()

	    # send image to server
		if answer == 'GOT SIZE':
			sock.sendall(bytes)

	        # check what server send
			answer = sock.recv(4096)

			if answer.decode() == 'GOT IMAGE' :
				data = sock.recv(4096)
				data = data.decode()
				if 'SIZE' in data:
					tmp = data.split()
					size = int(tmp[1])
					global_size = size

					sock.sendall(b'GOT SIZE')

					data = sock.recv(4096)
					myfile = open(image_result, 'wb')
					myfile.write(data)

					data = sock.recv(global_size)
					myfile.write(data)
					myfile.close()

					sock.sendall(b'GOT IMAGE')

				print('Image successfully send to server')

		myfile.close()

	finally:
		im = cv2.imread(image_result)
		writer.write(im)
		limit +=1


writer.release()
vid.release()
cv2.destroyAllWindows()

sock.sendall(b'BYE BYE')
sock.close()
