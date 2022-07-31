from kafka import KafkaProducer
from datetime import datetime
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time
import pickle
from pygeodesy.ellipsoidalVincenty import LatLon
from pygeodesy import Datums

#from roverProducer import Rover_Producer

import argparse

class RoverCommands():
    def __init__(self, producer):
        # self.parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
        # self.parser.add_argument('--connect udp:127.0.0.1:14551',
        #             help="Vehicle connection target string. If not specified, SITL automatically started and used.")
        # self.args = self.parser.parse_args()

        self.connection_string = 'udp:127.0.0.1:14551'
        self.sitl = None
        self.producer = producer
        print('Connecting to vehicle on: %s' % self.connection_string)
        self.producer.createMessage('ROVER: Connecting to vehicle on: %s' % self.connection_string)
        self.vehicle = connect(self.connection_string, wait_ready=False)
        self.vehicle.wait_ready(True, timeout=150)
        #self.vehicle.groundspeed = 1

  # Function to arm
    def arm(self):
        print("Basic pre-arm checks")
        # Don't let the user try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            self.producer.createMessage("ROVER: Waiting for vehicle to initialise")
            time.sleep(1)

        print("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode    = VehicleMode("GUIDED")
        self.vehicle.armed   = True

        while not self.vehicle.armed:
            print(" Waiting for arming...")
            self.producer.createMessage("ROVER: Waiting for vehicle to arm")
            time.sleep(1)


  # Moves the vehicle to a position latitude, longitude, altitude.
  # The method takes a function pointer argument with a single `dronekit.lib.LocationGlobal` parameter for
  # the target position. This allows it to be called with different position-setting commands.
  # By default it uses the standard method: dronekit.lib.Vehicle.simple_goto().
  # It uses pygeodesy methods to calculate distance between coordinates.
  # The method reports the distance to target every two seconds.
  #
  # note: simple_goto(), by itself, can be interrupted by a later command,
  # and does not provide any functionality to indicate when the vehicle has reached its destination.
    def goto(self, latitude, longitude, altitude):
        #self.producer.createMessage("ROVER: Moving to Waypoint: " + str(latitude) + ' , ' + str(longitude))
        self.vehicle.mode = VehicleMode("GUIDED")
        # currentLocation=vehicle.location.global_relative_frame
        currentCoord = LatLon(self.vehicle.location.global_relative_frame.lat, self.vehicle.location.global_relative_frame.lon, datum=Datums.NAD83)

        targetCoord = LatLon(latitude, longitude, datum=Datums.NAD83)
        targetDistance = currentCoord.distanceTo(targetCoord)

        targetLocation = LocationGlobalRelative(latitude, longitude, altitude)
        self.vehicle.simple_goto(targetLocation)

        #print "DEBUG: targetCoord: %s" % targetCoord
        #print "DEBUG: targetCoord: %s" % targetDistance

        while self.vehicle.mode.name == "GUIDED": # Stop action if we are no longer in guided mode.
            print("\nMODE: " + self.vehicle.mode.name)
            #self.producer.createMessage("ROVER: Vehicle speed: " + str(self.vehicle.groundspeed))
            # remainingDistance=get_distance_metres(vehicle.location.global_relative_frame, targetLocation)
            currentCoord = LatLon(self.vehicle.location.global_relative_frame.lat, self.vehicle.location.global_relative_frame.lon, datum=Datums.NAD83)
            remainingDistance = currentCoord.distanceTo(targetCoord)
            print ("Distance to waypoint: " + str(remainingDistance))
            if remainingDistance <= 5: # targetDistance*0.3: #Just below target, in case of undershoot. # MAYBE WILL CHANGE TO A CONSTANT
                print ("Reached waypoint")
                break
            time.sleep(0.5)
        #self.producer.createMessage("ROVER: Arrived at Waypoint")

    def navigate(self, GPSPATHS, picture_selec):
        # with open(GPSDATAFILE, 'rb') as file:
        #   GPSPATHS = pickle.load(file)
        PATH = GPSPATHS[picture_selec]
        for i in range(0, len(PATH)):
            print('Go to waypoint #' + str(i+1) + ': ' + str(PATH[i][0]) + " , " + str(PATH[i][1]))
            self.goto(PATH[i][0], PATH[i][1], 0)

    def armAndGo(self, GPSPATHS, picture_selec):
        self.arm()
        print("Arming complete")
        # Send update to GS
        self.producer.createMessage("ROVER: Arming Complete")

        print("Set ground speed to " + str(1.2))
        self.vehicle.groundspeed = 1.2
        self.producer.createMessage("ROVER: Ground speed set to " + str(1.2))

        # Start journey
        # navigate('2022-06-14 Satellite Image Testing/GPSDATAPACKAGE.pickle', 'Picture 1')
        self.producer.createMessage("ROVER: MISSION START")
        self.navigate(GPSPATHS, picture_selec)
        print("ROVER: Target reached")
        #self.producer.createMessage("ROVER: Final waypoint reached")
        
        # print("Go to waypoint:")

        # # wp3 = LocationGlobalRelative(40.61925811343867, -74.57010269091948, 0)   # <- the 3rd argument is the altitude in meters. (set to 0 for rover)
        # # vehicle.simple_goto(wp3)
        # goto(40.61925811343867, -74.57010269091948, 0)

        # Stop for 5 seconds
        # time.sleep(3)

        # Close vehicle object
        # self.closeVehicle()
      
    def stop(self):
        self.producer.createMessage("ROVER: Stopping")
        self.vehicle.mode = VehicleMode("HOLD")
        print("Rover stopped")
        time.sleep(2)
      
    def directReturnToHome(self):
        #self.producer.createMessage("ROVER: Returning to home location")
        self.vehicle.mode = VehicleMode("RTL")
        print("Returning to home")
        self.producer.createMessage("ROVER: Returning to home location")
      
    def returnToHome(self, GPSPATHS, picture_selec):
        # with open(GPSDATAFILE, 'rb') as file:
        #   GPSPATHS = pickle.load(file)
        print("Returning to home")
        self.producer.createMessage("ROVER: Returning to home location")
        PATH = GPSPATHS[picture_selec]
        for i in range(len(PATH)-1, -1, -1):
            print('Go to waypoint #' + str(i+1) + ': ' + str(PATH[i][0]) + " , " + str(PATH[i][1]))
            self.goto(PATH[i][0], PATH[i][1], 0)
      
    def closeVehicle(self):
        # Send update to GS
        print(("ROVER: FINAL DESTINATION REACHED. MISSION COMPLETE... CLOSING VEHICLE"))
        self.producer.createMessage("ROVER: FINAL DESTINATION REACHED. MISSION COMPLETE... CLOSING VEHICLE")
        self.vehicle.close()