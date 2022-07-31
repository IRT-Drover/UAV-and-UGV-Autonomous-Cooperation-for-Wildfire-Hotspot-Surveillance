from kafka import KafkaConsumer
import dronekit
import os
import numpy as np
import json
import datetime
import pickle
import time

from roverProducer import Rover_Producer
from roverProducer import KAFKA_SERVER
from roverProducer import TOPIC_NAME


keepGoing = True
while(keepGoing):
    try:
        consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=KAFKA_SERVER)
        keepGoing = False
        print("Connected to Server")
        producer = Rover_Producer()
        producer.createMessage("ROVER: Connected to Server")
    except:
        print("Failed Connection: Trying Again in 10 Seconds")
        time.sleep(10)

for message in consumer:
    print("Recieved Message")
    message = json.loads(message.value.decode('utf-8'))
    #message = json.load(message)
    print("Decoding Message")

    if message["forWhom"] == "Rover":
        print("Received Message for Rover")
        producer.createMessage("ROVER: Received command")
        if not message["message"] == "":
            print(message["message"])
            
        if message["command"] == "launch": # just makeshift names for now
            print("Launching...")
            producer.createMessage("Rover Launching...")
            # flight = "DronePictures\\"+message["date"]
            # if(not os.path.exists(flight)):
            #     os.mkdir(flight)
            # GPSPATHS = pickle.loads(message["gpsData"])
            GPSPATHS = message["gpsData"]
            # with open(flight+'GPSDATAPACKAGE.pickle','wb') as file:
            #     pickle.dump(GPSPATHS, file, 0)
            try:
                producer.launch(GPSPATHS)
            except dronekit.TimeoutError:
                print(dronekit.TimeoutError)
                producer.createMessage("ROVER: dronekit.TimeoutError: wait_ready experienced a timeout after 150 seconds.")
            except dronekit.APIException:
                print(dronekit.APIException)
                producer.createMessage("ROVER: dronekit.APIException: Timeout in initializing connection to mavproxy")
                
        if message["command"] == "launchandreturn": # just makeshift names for now
            print("Launching...")
            producer.createMessage("Rover Launching...")
            # flight = "DronePictures\\"+message["date"]
            # if(not os.path.exists(flight)):
            #     os.mkdir(flight)
            # GPSPATHS = pickle.loads(message["gpsData"])
            GPSPATHS = message["gpsData"]
            # with open(flight+'GPSDATAPACKAGE.pickle','wb') as file:
            #     pickle.dump(GPSPATHS, file, 0)
            try:
                producer.launchAndReturn(GPSPATHS)
            except dronekit.TimeoutError:
                print(dronekit.TimeoutError)
                producer.createMessage("ROVER: dronekit.TimeoutError: wait_ready experienced a timeout after 150 seconds.")
            except dronekit.APIException:
                print(dronekit.APIException)
                producer.createMessage("ROVER: dronekit.APIException: Timeout in initializing connection to mavproxy")
