import socket
import numpy as np
import cv2
from tkinter import *
from tkinter import filedialog as fd
from queue import Queue, Empty
from threading import Thread

from pathlib import Path


class TimeOut(Exception):
    def __init__(self, message):
        self.msg = message


class DataEmpty(Exception):
    def __init__(self, message):
        self.msg = message


class Client:
    root = Tk()
    root.geometry('366x200')
    root.title("Client")
    Connect = Button(text="Connect")
    Settings = Button(text="Set settings", state="disabled")
    Start = Button(text="Start recording", state="disabled")
    Stop = Button(text="Stop recording", state="disabled")
    Save = Button(text='Save', state="disabled")
    Quit = Button(text='Quit')
    Camera = Entry()
    Label(text="Index camera: ").grid(row=1, column=0)
    Info = Text(width=43, height=10, wrap=WORD)
    Connect.grid(row=0, column=0, sticky=W + E)
    Settings.grid(row=1, column=2, sticky=W + E)
    Start.grid(row=0, column=1, sticky=W + E)
    Stop.grid(row=0, column=2, sticky=W + E)
    Save.grid(row=0, column=3, sticky=W + E)
    Quit.grid(row=0, column=4, columnspan=2, sticky=W + E)
    Camera.grid(row=1, column=1, sticky=W + E)
    Info.grid(row=2, column=0, columnspan=5, sticky=W + E)
    scroll = Scrollbar(command=Info.yview)
    scroll.grid(row=2, column=5, sticky=S + N)
    Info.config(yscrollcommand=scroll.set)

    qu = Queue()

    stop_signal = False
    sock = None

    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 65432  # The port used by the server

    img_process = "./img_process.png"
    codec = None
    writer = None
    vid = None
    index_camera = None

    def state_connect(self):
        self.Start["state"] = "disable"
        self.Stop["state"] = "disable"
        self.Settings["state"] = "active"
        self.Save["state"] = "disable"

    def error_state_connect(self):
        self.Start["state"] = "disable"
        self.Stop["state"] = "disable"
        self.Settings["state"] = "disable"
        self.Save["state"] = "disable"

    def state_set_settings(self):
        self.Start["state"] = "active"

    def state_stop_recording(self):
        self.Connect["state"] = "active"
        self.Stop["state"] = "disable"
        self.Start["state"] = "active"
        self.Settings["state"] = "active"
        self.Save["state"] = "active"

    def state_start_recording(self):
        self.Connect["state"] = "disable"
        self.Start["state"] = "disable"
        self.Stop["state"] = "active"
        self.Settings["state"] = "disable"
        self.Save["state"] = "disable"

    def error_state_start_recording(self):
        self.Connect["state"] = "active"
        self.Start["state"] = "active"
        self.Stop["state"] = "disable"
        self.Settings["state"] = "active"
        self.Save["state"] = "disable"

    def log(self, message):
        self.Info.insert(END, message)
        self.Info.insert(END, "\n")

    def set_settings(self):
        if self.Camera.get():
            self.index_camera = self.Camera.get()
            self.state_set_settings()
        else:
            self.log("Set index of camera")

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.HOST, self.PORT))
            self.state_connect()
            self.log("Connected to {}:{}".format(self.HOST, self.PORT))
        except ConnectionRefusedError as e:
            self.error_state_connect()
            self.log(e)

    def task(self):
        try:
            q = self.qu.get(block=False)  # получить значение из очереди
        except Empty:  # если в очереди ничего нет, то возвращаем False
            q = None
        if q:  # если вернулось True, то сообщаем об окончании
            self.log(q)
        self.root.after(1000, self.task)  # снова перезапускаем задачу после выполнения

    def recording(self):
        try:
            self.codec = cv2.VideoWriter_fourcc(*'XVID')
            self.writer = cv2.VideoWriter("./out.avi", self.codec, 25.0, (1920, 1080))
            # self.vid = cv2.VideoCapture(self.index_camera, cv2.CAP_DSHOW)
            self.vid = cv2.VideoCapture("./out1.avi")
            self.state_start_recording()
            # self.qu.put("Sending frame")
            self.log("Sending frame")
            while self.vid.isOpened():
                ret, frame = self.vid.read()
                if cv2.waitKey(1) & 0xFF == ord('q') or ret is False or self.stop_signal:
                    #self.qu.put("Stop")
                    self.log("Stopped")
                    self.state_stop_recording()
                    break
                cv2.imwrite(self.img_process, frame)
                self.send_frame_to_server()
                self.log(self.vid.isOpened())
                #self.qu.put(False)

        except Exception as e:
            self.log("rr")
            self.error_state_start_recording()
            self.log(e)

    def start(self):
        # self.root.after(1000, self.task)
        # result_queue = Queue()
        Thread(target=self.recording, args=[], daemon=True).start()

    def send_frame_to_server(self):
        image_result = "./result.png"
        try:
            file_with_frame = open(self.img_process, 'rb')
            bytes = file_with_frame.read()
            size = len(bytes)

            # send image size to server
            self.sock.sendall(("SIZE %s" % size).encode())
            answer = self.sock.recv(4096)
            answer = answer.decode()

            # send image to server
            if answer == 'GOT SIZE':
                self.sock.sendall(bytes)

                # check what server send
                answer = self.sock.recv(4096)

                if answer.decode() == 'GOT IMAGE':
                    data = self.sock.recv(4096)
                    data = data.decode()
                    if 'SIZE' in data:
                        global_size = int(data.split()[1])

                        self.sock.sendall(b'GOT SIZE')
                        data = self.sock.recv(4096)

                        file_with_frame = open(image_result, 'wb')
                        file_with_frame.write(data)

                        data = self.sock.recv(global_size)
                        if not data:
                            file_with_frame.close()
                            raise DataEmpty("data empty")
                        file_with_frame.write(data)
                        file_with_frame.close()
                        self.sock.sendall(b'GOT IMAGE')

            file_with_frame.close()
        finally:
            image = cv2.imread(image_result)
            self.writer.write(image)

    def stop_recording(self):
        self.stop_signal = True
        self.state_stop_recording()
        self.writer.release()
        self.vid.release()
        cv2.destroyAllWindows()

    def save_out_file(self):
        avi_file = Path("./out.avi")
        file_name = fd.asksaveasfilename(filetypes=(("Avi files", "*.avi"), ("all files", "*")))
        avi_file.rename(file_name)

    def quit(self):
        try:
            self.sock.sendall(b'BYE BYE')
            self.sock.close()
        except Exception:
            pass
        finally:
            self.root.quit()


reformat = Client()
reformat.Connect.configure(command=reformat.connect)
reformat.Settings.configure(command=reformat.set_settings)
reformat.Start.configure(command=reformat.start)
reformat.Stop.configure(command=reformat.stop_recording)
reformat.Save.configure(command=reformat.save_out_file)
reformat.Quit.configure(command=reformat.quit)


def main():
    mainloop()


if __name__ == '__main__':
    main()
