from kafka import KafkaConsumer
import time
import json


from droneProducer import Drone_Producer
import json

KAFKA_SERVER = '192.168.33.114:9092'
TOPIC_NAME = 'commands'


keepGoing = True
while(keepGoing):
	try:
		consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=KAFKA_SERVER)
		keepGoing = False
		print("Connected to Server")
	except:
		print("Failed Connection: Trying Again in 10 Seconds")
		time.sleep(10)

producer = Drone_Producer()
for message in consumer:
    print("Recieved Message")
    message = json.loads(message.value.decode('utf-8'))

    if message["forWhom"] == "Drone":
        print("Recieved Message for Drone")
        if not message["message"] == "":
            producer.createMessage("Please")
            print(message["message"])

        if message["command"] == "SendTestPicture": ### will change latter
            print("Sending picture")
            producer.sendTestPicture()

        elif message['command'] == "takeoff":
            producer.launch(message['altitude'])

        elif message['command'] == 'moveTo':
            producer.launch(message['coordinates'], message['altitude'])
