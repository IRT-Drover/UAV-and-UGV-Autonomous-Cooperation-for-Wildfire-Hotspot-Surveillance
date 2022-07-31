from ensurepip import bootstrap
from kafka import KafkaProducer
import json
import codecs
from datetime import datetime
import os
from groundStationProducer import GS_Producer
from PathfindingAndMapping import createPathAndCoords



producer = GS_Producer()
# producer.retrievePhoto()
#producer.launchRoverTest({'Picture 1':[[40.618199, -74.569113]]})
#producer.launchRoverTest({'Picture 1':[[40.66931276442911, -74.47597388341107]]}), 
# producer.sendPathCoordinatesToRoverandLaunch()

# createPathAndCoords([[50,50],[200,200]])

# producer.sendPathCoordinatesToRoverandLaunch("1_GPSDATAPACKAGE.pickle")
producer.sendPathCoordinatesToRoverandLaunch("2_GPSDATAPACKAGE.pickle")
# producer.sendPathCoordinatesToRoverandLaunch("3_GPSDATAPACKAGE.pickle")