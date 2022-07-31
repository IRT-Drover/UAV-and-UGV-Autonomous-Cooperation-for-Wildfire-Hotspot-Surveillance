from kafka import KafkaConsumer
import os
import cv2 as cv
import numpy as np
import json
import time
from groundStationProducer import GS_Producer
from groundStationProducer import KAFKA_SERVER
from groundStationProducer import TOPIC_NAME

from PathfindingAndMapping import createPathAndCoords

keepGoing = True
while(keepGoing):
    try:
        consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=KAFKA_SERVER)
        keepGoing = False
        print("Connected to Server")
    except:
        print("Failed Connection: Trying Again in 10 Seconds")
        time.sleep(10)

#Ground Station Consumer
producer = GS_Producer()
for message in consumer:
    print("Recieved Message")
    message = json.loads(message.value.decode('utf-8'))
    #message = json.load(message)
    print("Decoding Message")
    if message["forWhom"] == "GS":
        print("Recieved Message for GS")
        if not message["message"] == "":
            print(message["message"])
            
        if not message["pictureData"] == "":
            flight =  "DronePictures\\"+message["date"]
            if(not os.path.exists(flight)):
                os.mkdir(flight)
            print("Message has picture data")
            respository = open(flight + "\\pictureData.txt", "a")
            respository.write("Picture " + "\n" + str(message["coordinates"][0]) + " " +  str(message["coordinates"][1]) + "\n" + str(message["altitude"]) + "\n" + str(message["cameraHeading"]))
            print("Write Coordinates")
            img =  np.array(message["pictureData"])
            cv.imwrite(flight + "\\ma.png", img)
            print("Going to create path and coordinates")
            createPathAndCoords(message["startEnd"])
            #print(message)
            
            cont = input("Image processed... Send GPS data to rover? (y/n): ")
            while cont != 'y' and cont != 'n':
                cont = input("(y/n): ")
            if cont == 'y':
                producer.sendPathCoordinatestoRover()
            else:
                print('Cancelled')