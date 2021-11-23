# Import socket module
import socket
import cv2
import numpy as np
from keras.models import load_model

global sendBack_angle, sendBack_Speed, current_speed, current_angle, count
sendBack_angle = 0
sendBack_Speed = 0
current_speed = 0
current_angle = 0
count = 0
IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_CHANNELS = 132, 200, 3
model = None

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the port on which you want to connect
PORT = 54321
# connect to the server on local computer
s.connect(('host.docker.internal', PORT))
# s.connect(('127.0.0.1', PORT))

def Control(angle, speed):
    global sendBack_angle, sendBack_Speed
    sendBack_angle = angle
    sendBack_Speed = speed

if __name__ == "__main__":
    model = load_model('./models/model22-12.h5')
    modelsp = load_model('./models/modelsp-19.h5')
    try:
        while True:

            message_getState = bytes("0", "utf-8")
            s.sendall(message_getState)
            state_date = s.recv(100)

            try:
                current_speed, current_angle = state_date.decode(
                    "utf-8"
                ).split(' ')
            except Exception as er:
                print(er)
                pass

            message = bytes(f"1 {sendBack_angle} {sendBack_Speed}", "utf-8")
            s.sendall(message)
            data = s.recv(100000)

            try:
                image = cv2.imdecode(
                    np.frombuffer(
                        data,
                        np.uint8
                        ), -1
                )

                # preprocess
                image = image[130:, :, :]
                image = cv2.resize(image, (IMAGE_WIDTH, IMAGE_HEIGHT), cv2.INTER_AREA)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                ret, image = cv2.threshold(image, 215, 255, cv2.THRESH_BINARY)
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

                # predict model
                afterProcess = np.array([image])
                angle = float(model.predict(afterProcess, batch_size=1))
                speed = float(modelsp.predict(afterProcess, batch_size=1)) + 40

                Control(angle, speed)

            except Exception as er:
                print(er)
                pass

    finally:
        print('closing socket')
        s.close()