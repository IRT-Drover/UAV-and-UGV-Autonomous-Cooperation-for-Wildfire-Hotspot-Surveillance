from ensurepip import bootstrap
from kafka import KafkaProducer
import pickle
import json
import datetime
import glob
import os

TOPIC_NAME = 'commands'
KAFKA_SERVER = "192.168.172.114:9092"
#KAFKA_SERVER = "172.20.10.9:9092"
#KAFKA_SERVER = "192.168.1.180:9092"

class GS_Producer:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

    def startMission(self):
        None

    def retrievePhoto(self, coordinates, altitude):
        command = {
            "forWhom":"Drone",
            "message":"",
            "coordinates":coordinates,
            "date":"",
            "pictureData":"",
            "altitude":altitude,
            "cameraHeading":"",
            "startEnd":"",
            "gpsData":"",
            "command":"Send Picture"
        }

        print("Successfully Created Command")
        self.producer.send(TOPIC_NAME, json.dumps(command).encode('utf-8'))
        print("Successfully sent to topic")
        self.producer.flush()

    def sendPathCoordinatesToRoverandLaunch(self, GPSDataFile="GPSDATAPACKAGE.pickle"):
        directory = 'DronePictures/'
        flights = glob.glob(directory+"*")
        # flight = max(flights, key=os.path.getmtime) + '\\'
        flight = (directory + "2022-07-26_Sat/")
        with open(flight+GPSDataFile, 'rb') as file:
            GPSPATHS = pickle.load(file)
        #pathSer= pickle.dumps(GPSPATHS)
        command = {
            "forWhom":"Rover",
            "message":"",
            "coordinates":"",
            "date":str(flight), ### problem with slashes
            "pictureData":"",
            "altitude":"",
            "cameraHeading":"",
            "startEnd":"",
            "gpsData":GPSPATHS,
            "command":"launch"
        }

        print("Successfully Created Command")
        self.producer.send(TOPIC_NAME, json.dumps(command).encode('utf-8'))
        print("Successfully sent to topic")
        self.producer.flush()

    def launchRoverTest(self, GPSPATHS):
        # Left corner of pingry baseball infield behind football field bleachers
        command = {
            "forWhom":"Rover",
            "message":"",
            "coordinates":"",
            "date":"",
            "pictureData":"",
            "altitude":"",
            "cameraHeading":"",
            "startEnd":"",
            "gpsData":GPSPATHS,
            "command":"launch"
        }
        print("Successfully Created Command")
        self.producer.send(TOPIC_NAME, json.dumps(command).encode('utf-8'))
        print("Successfully sent to topic")
        self.producer.flush()
