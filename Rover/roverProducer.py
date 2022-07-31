from kafka import KafkaProducer
import time
import pickle
import json
import datetime
import glob
import os

from roverCommands import RoverCommands

TOPIC_NAME = 'commands'
KAFKA_SERVER = "192.168.172.114:9092"
#KAFKA_SERVER = "172.20.10.9:9092"
#KAFKA_SERVER = "192.168.1.180:9092"

class Rover_Producer:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    
    def createMessage(self, message):
        command = {
            "forWhom":"GS",
            "message":message,
            "coordinates":"",
            "date":"",
            "pictureData":"",
            "altitude":"",
            "cameraHeading":"",
            "startEnd":"",
            "gpsData":"",
            "command":""
        }
        
        print("Successfully Created Command")
        self.producer.send(TOPIC_NAME, json.dumps(command).encode('utf-8'))
        print("Successfully sent to topic")
        self.producer.flush()

    def launch(self, GPSPATHS):
        roverCommands = RoverCommands(self)
        roverCommands.armAndGo(GPSPATHS, 'Picture 1')
        #time.sleep(3)
        #roverCommands.returnToHome(GPSPATHS, 'Picture 1')
        roverCommands.closeVehicle()
        
    def launchAndReturn(self, GPSPATHS):
        roverCommands = RoverCommands(self)
        roverCommands.armAndGo(GPSPATHS, 'Picture 1')
        time.sleep(3)
        roverCommands.returnToHome(GPSPATHS, 'Picture 1')
        roverCommands.closeVehicle() 