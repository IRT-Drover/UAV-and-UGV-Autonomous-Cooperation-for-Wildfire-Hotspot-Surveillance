from droneCommands import DroneCommands

from kafka import KafkaProducer
import cv2 as cv
import json
import codecs
from datetime import datetime
import os

TOPIC_NAME = 'commands'
KAFKA_SERVER = '192.168.33.114:9092'

class Drone_Producer:

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER, max_request_size=20626282)

    def sendTestPicture(self): ### may need parameter to choose which photo
        img = cv.imread("pasinihouse.png") ### edit
        imgSer = img.tolist()
        self.createMessage("Creating Image")
        # img = open("pasinihouse.png", 'rb')
        # imgSer = img.read()
        # imgSer = bytearray(imgSer)
        # img.close()
        coords = [40.647649, -74.476466]
        altitude = 20
        bearing = 0
        startendlist = [[475,562],[926,440]]
        now = datetime.now()
        command = {
            "forWhom":"GS",
            "message":"",
            "coordinates":coords,
            "date":str(now.date()), ### may change to date photo taken
            "pictureData":imgSer,
            "altitude":altitude,
            "cameraHeading":bearing,
            "startEnd":startendlist,
            "gpsData":"",
            "command":""
        }

        print("Succesfully Created Command")
        self.producer.send(TOPIC_NAME, json.dumps(command).encode('utf-8'))
        #producer.send(TOPIC_NAME, b"bruh")
        print("Succesfully sent to topic")
        self.producer.flush()

    def createMessage(self, message):
        command = {
            "forWhom":"GS",
            "message": message,
            "coordinates":"",
            "date":"",
            "pictureData":"",
            "altitude":"",
            "cameraHeading":"",
            "startEnd":"",
            "gpsData":"",
            "command":""
        }

        print("Succesfully Created Command")
        self.producer.send(TOPIC_NAME, json.dumps(command).encode('utf-8'))
       #producer.send(TOPIC_NAME, b"bruh")
        print("Succesfully sent to topic")
        self.producer.flush()


    def sendPicture(self, img, location, alt, bearing):
        now = datetime.now()
        location = str(location)
        comma = location.find(',')
        lat = location[27:comma]
        location = location[comma+1:]
        lon = location[4:location.find(',')]
        command = {
            "forWhom":"GS",
            "message":"",
            "coordinates":[lat, lon],
            "date":str(now.date()), ### may change to date photo taken
            "pictureData":img.tolist(),
            "altitude":alt,
            "cameraHeading":bearing,
            "startEnd":[[50, 50], [80, 80]],
            "gpsData":"",
            "command":""
        }

        print("Succesfully Created Command")
        self.producer.send(TOPIC_NAME, json.dumps(command).encode('utf-8'))
        #producer.send(TOPIC_NAME, b"bruh")
        print("Succesfully sent to topic")
        self.producer.flush()

    def launch(self, coordinate, altitude):
        droneCommands = DroneCommands(self)
        droneCommands.takeOffAndGo(coordinate, altitude)
        img, location, alt, bearing = droneCommands.takePicture()
        self.createMessage("DRONE: Sent Picture")
        droneCommands.returnToHome()
        droneCommands.closeVehicle()
        self.sendPicture(img, location, alt, bearing)

    def launch(self, altitude):
        droneCommands = DroneCommands(self)
        droneCommands.takeOff(altitude)
        img, location, alt, bearing = droneCommands.takePicture()
        self.createMessage("DRONE: Sent Picture")
        droneCommands.land()
        droneCommands.closeVehicle()
        self.sendPicture(img, location, alt, bearing)
