import cv2
from datetime import datetime
import os
from Undistort import CameraParameters
global vid, path, cam, today, now, time, newpath
path = "/home/pi/Drone-Navigation/DronePictures"
cam = cv2.VideoCapture(0)
class OpenCV:

    #today = datetime.today()
    now = datetime.now()
    day = str(now.date())
    time = str(now.time())
    newPath = r"/home/pi/Drone/DronePictures/" + day + " " + time
    os.makedirs(newPath)
    path = newPath
    counter = 0
    repository = open(newPath + "/pictureData.txt", "a")
    cameraparameters = CameraParameters()

    def takePicture(self, location, alt):
        ret, img = cam.read()
        # Undistorts image
        img = self.cameraparameters.undistortPicture(img)
        # Saves image in flight folder
        self.counter += 1
        cv2.imwrite(self.newPath + "/Drone Picture: " + self.day + " " + self.time + str(self.counter) + ".png", img)
        # self.repository.write("Picture " + str(self.counter) + "\n" + "Location " + str(location) + "\n" + "Altitude " + str(alt))
        # Appends location to pictureData file in correct format
        location = str(location)
        comma = location.find(',')
        lat = location[27:comma]
        location = location[comma+1:]
        lon = location[4:location.find(',')]
        self.repository.write("Picture " + str(self.counter) + "\n" + lat + " " + lon + "\n" + str(alt) + "\n")
        return img