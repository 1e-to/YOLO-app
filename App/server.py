import random
import socket, select
from time import gmtime, strftime
from random import randint
import subprocess
import sys

### NN ###
import cv2
import numpy as np

net = cv2.dnn.readNet("C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\yolov3_coco\\yolov3.weights",
					  "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\yolov3.cfg")
classes = []
with open("C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\COCO.names", "r") as f:
	classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()

outputlayers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

img_path = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\image1.png"
res_path = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\res.jpg"
##########

imgcounter = 1
basename = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\image1.png"
res_path = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\res.jpg"

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
						myfile = open(basename, 'wb')
						myfile.write(data)

						data = sock.recv(global_size)
						if not data:
							myfile.close()
							break
						myfile.write(data)
						myfile.close()

						sock.sendall(b'GOT IMAGE')







						#########
						# nn_script = "C:\\Users\\etotmeni\\OneDrive - Intel Corporation\\Desktop\\App\\nn.py"
						# subprocess.check_call([sys.executable, nn_script])
						#########
						im = cv2.imread(img_path)
						img = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
						img_orig = img.shape

						img = cv2.resize(img, (400, 300))
						img_orig = img.shape
						height, width, channels = img.shape

						blob = cv2.dnn.blobFromImage(img,  # 	input image (with 1-, 3- or 4-channels).
													 0.00392,  # 	spatial size for output image
													 (416,416),  # 	
													 (0,0,0),
													 True,
													 crop=False )
						
						net.setInput(blob)
						outs = net.forward(outputlayers)

						# Showing info on the screen
						conf_min = 0.5 # порог уверенности
						class_ids = []
						confidences = []
						boxes = []  # [[43, 167, 381, 181]] - список координат найденных объектов
						for out in outs:
							for detection in out:
								scores = detection[5:]
								class_id = np.argmax(scores)
								confidence = scores[class_id]
								if confidence > conf_min:
								# Object detected
									center_x = int(detection[0] * width)
									center_y = int(detection[1] * height)
									w = int(detection[2] * width)
									h = int(detection[3] * height)

									# Rectangle coordinates
									x = int(center_x - w / 2 )
									y = int(center_y - h / 2 )

									boxes.append([x, y, w, h])
									confidences.append(float(confidence))
									class_ids.append(class_id)

						number_objects_detected = len(boxes)

						if number_objects_detected:
							classes = {0:'???', 13:'unknow', 56:'chair', 57:'sofa', 59:'bed', 60:'diningtable', 69:'&&&'}
							for i in range(100):
								if i not in classes.keys():
									classes[i] = "???"

							indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

							# периодически выскакивает keyError, но label присваивается верно
							font = cv2.FONT_HERSHEY_PLAIN
							color = 0
							label = ""
							x = 0
							y = 0
							w = 0
							h = 0
							# for i in range(len(boxes)):
							# Нужно предать:
							x, y, w, h = boxes[0]
							label = str(classes[class_ids[0]])
							color = colors[0]

							# # далее уже отрисовка
							cv2.rectangle(img, (x,y), (w,h), color, 1)
							cv2.circle(img, (center_x, center_y), 10, (0,255,0))
							cv2.putText(img, label, (x,y - 10), font, 1, (0,255,0), 2)
							# plt.imshow(img)
							img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
							res = cv2.imwrite(res_path ,img)
							cv2.waitKey(0)
							cv2.destroyAllWindows()

						else:
							print("Nothing in img")
							img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
							res = cv2.imwrite(res_path ,img)





						#########
						sendfile = open(res_path, 'rb')
						# sendfile = open(img_path, 'rb')
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
