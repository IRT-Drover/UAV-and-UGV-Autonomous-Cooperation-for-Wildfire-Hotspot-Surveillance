from kafka import KafkaProducer
from datetime import datetime
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
from OpenCV import OpenCV
import cv2 as cv
from mpu6050 import mpu6050
import time
import pigpio
import subprocess

#from droneProducer import Drone_Producer

import argparse


#pi.set_servo_pulsewidth(17, 1500)
#pi.set_servo_pulsewidth(18, 1500)

#time.sleep(2)



camera = OpenCV()

class DroneCommands():
    def __init__(self, producer):
        
        
        self.pi = pigpio.pi()
        self.pi.set_mode(17, pigpio.OUTPUT)
        self.pi.set_mode(18, pigpio.OUTPUT)
        self.pi.set_servo_pulsewidth(17, 2400)
        self.pi.set_servo_pulsewidth(18, 1500)
        self.sensor = mpu6050(0x68)
        #self.parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
        #self.parser.add_argument('--connect',
        #            help="Vehicle connection target string. If not specified, SITL automatically started and used.")
        #self.args = self.parser.parse_args()

        self.connection_string = 'udp:127.0.0.1:14551'
        self.sitl = None
        self.producer = producer
        self.producer.createMessage("Test")
        self.newCamera = OpenCV()
        print('Connecting to vehicle on: %s' % self.connection_string)
        self.vehicle = connect(self.connection_string, wait_ready=True)
        self.vehicle.airspeed = 0.3

    # Function to arm and then takeoff to a user specified altitude
    def arm_and_takeoff(self, aTargetAltitude):
        print("Basic pre-arm checks")
        # Don't let the user try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            self.producer.createMessage("DRONE: Waiting for vehicle to initialise")
            time.sleep(1)

        print("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode    = VehicleMode("GUIDED")
        self.vehicle.armed   = True

        while not self.vehicle.armed:
            print(" Waiting for arming...")
            self.producer.createMessage("DRONE: Waiting for vehicle to arm")
            time.sleep(1)

        print("Taking off!")
        #self.producer.createMessage("DRONE: Taking Off to " + str(aTargetAltitude) + " meters")
        self.vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

        # Check that vehicle has reached takeoff altitude
        while True:
            print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
            #self.producer.createMessage("DRONE: Altitude: " + str(self.vehicle.location.global_relative_frame.alt))
            #Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.9:
                print("Reached target altitude")
                break
            
            time.sleep(1)

    def takeOffAndGo(self, coordinate, altitude):
        self.arm_and_takeoff(altitude)
        time.sleep(3)
        wp = LocationGlobalRelative(coordinate[0],coordinate[1], altitude)
        self.producer.createMessage("DRONE: Moving to Waypoint: " + coordinate)
        self.vehicle.simple_goto(wp)
        print("Arrived at Waypoint")
        self.producer.createMessage("DRONE: Arrived at Waypoint")

    def takeOff(self, altitude):
        self.arm_and_takeoff(altitude)
        self.proc1 = subprocess.Popen(args=["python", "/home/pi/Drone/finalGyro.py"], stdout=subprocess.PIPE)
        print("IT works")
        self.producer.createMessage("DRONE: Gyro Turned On")
        time.sleep(3)
    
    def land(self):
        self.producer.createMessage("DRONE: Landing")
        self.pi.set_servo_pulsewidth(17, 2400)
        self.pi.set_servo_pulsewidth(18, 1500)
        self.proc1.terminate()
        self.vehicle.mode = VehicleMode("LAND")
        
        self.producer.createMessage("DRONE: Gyro Turned Off")
        
        print("Drone Landed")
        time.sleep(2)

    def returnToHome(self):
        self.producer.createMessage("DRONE: Returning to Landing Zone")
        self.vehicle.mode = VehicleMode("RTL")
        print("Returned to Launch")
        time.sleep(2)

    def takePicture(self):
        time.sleep(5)
        #for i in range(10):
        location = self.vehicle.location.global_relative_frame
        altitude = self.vehicle.location.global_relative_frame.alt
        img = self.newCamera.takePicture(location, altitude)
        #    time.sleep(1)
        heading = self.vehicle.heading        
        angle = self.pi.get_servo_pulsewidth(18)
        angleFromZero = (angle - 2140.0) / 2000 * 180
        bearing = heading + angleFromZero        
        
        self.producer.createMessage("DRONE: Took Photo")
        return img, location, altitude, bearing

    def closeVehicle(self):
        self.producer.createMessage("DRONE: DONE")
        self.vehicle.close()

