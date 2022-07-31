# Converting pixels of the path into coordinates v2

import cv2 as cv
import numpy as np
import glob
import math
import sys
from astar import Node

# PyGeodesy Github: https://github.com/mrJean1/PyGeodesy
# Documentation: https://mrjean1.github.io/PyGeodesy/
from pygeodesy.ellipsoidalVincenty import LatLon
from pygeodesy import Datums

def distance(pixHome, pix1, resolution, magnification):
    distance_img_y = (pixHome[1] - pix1[1]) / resolution
    distance_map_y = distance_img_y / magnification
    print("Vert meters to center: " + str(distance_map_y))

    distance_img_x = (pix1[0] - pixHome[0]) / resolution
    distance_map_x = distance_img_x / magnification
    print("Horiz meters to center: " + str(distance_map_x))

    return [distance_map_x, distance_map_y]

def pixelstocoordinates(PATH, pictureData):
    if PATH is None or len(PATH)==0:
        return None
        # sys.exit("No pixel path found.")

    #Camera Specs
    # # focal length calculated from info given by manufacture
    # focal = 0.002 # focal length in meters #x=sensor_hdimens*pixelsize_in_micrometers/1,000,000 #f = x/(2tan(angleofview/2))
    # unitcell = 1.12 # size of single pixel in micrometers
    # resolution = 1/unitcell*1000000 # pixels per meter
    # sensor_H = 4656 # pixel dimensions of camera sensor/photo
    # sensor_V = 3496

    #Picture Data
    drone = LatLon(pictureData[0][0], pictureData[0][1], datum=Datums.NAD83) # default datum is WGS-84
    altitude = pictureData[1]
    img_direction = pictureData[2]

    #Camera Info
    npz_calib_file = np.load('calibration_data.npz')
    intrinsic_matrix = npz_calib_file['intrinsic_matrix']
    camera_shape = npz_calib_file['camera_dimensions']
    npz_calib_file.close()
    unitcell = 3 # size of single pixel in micrometers
    # AVG focal length from camera calibration
    focal = (intrinsic_matrix[0][0]*unitcell + intrinsic_matrix[1][1]*unitcell)/2/1000000 - 0.000117# focal length in meters #x=sensor_hdimens*pixelsize_in_micrometers/1,000,000 #f = x/(2tan(angleofview/2))
    resolution = 1/unitcell*1000000 # pixels per meter
    print("focal length: " + str(focal))

    sensor_H = camera_shape[0]
    sensor_V = camera_shape[1]

    print(sensor_H)
    print(sensor_V)
    print("Sensor dimensions in mm:")
    print("Width:" , (sensor_H/resolution*1000)) # in mm
    print("Height:" , (sensor_V/resolution*1000)) # in mm

    #TESTING PATH. ALL CORNERS AND MIDPOINTS, STARTING TOP LEFT
    # PATH = []
    # for i in [[0,0],[sensor_H/2-1,0],[sensor_H-1,0],[sensor_H-1,sensor_V/2-1],[sensor_H-1,sensor_V-1],[sensor_H/2-1,sensor_V-1],[0,sensor_V-1], [0,sensor_V/2-1]]:
    #     testpixel = Node()
    #     testpixel.x = i[0]
    #     testpixel.y = i[1]
    #     PATH.append(testpixel)

    ### FOR SATELLITE TESTING
    #resolution = 5024
    #imagepixels = 287 # scale width in number of pixels
    #objectsize = 32 # real world scale width in meters
    #magnification = (1/resolution)*imagepixels/objectsize #imagesize/objectsize #in meters
    #sensor_H = 1440
    #sensor_V = 900
    ###

    image_dist = (altitude * focal) / (altitude - focal)
    magnification = image_dist/altitude
    #print("image distance: " + str(image_dist))
    #print("altitude: " + str(altitude))
    #print("magnification: " + str(magnification))

    pixel_y_0 = int((sensor_V)//2) # pixel y-coordinate
    pixel_x_0 = int((sensor_H)//2) # pixel x-coordinate
    pixelCenter = [pixel_x_0, pixel_y_0]

    print("---")

    rover_path = []

    # Finds physical x- y-distance to a point and returns the GPS coordinates
    for i in range(0,len(PATH)):
        distance_map_x, distance_map_y = distance(pixelCenter, PATH[i], resolution, magnification)

        distance_map = math.sqrt(distance_map_x**2 + distance_map_y**2)

        bearing = 0 # compass 360 degrees; north = 0 degrees # accounts for angle of top of image from North
        if distance_map_x != 0:
            bearing = 90 - (math.atan(distance_map_y/distance_map_x)*180/math.pi) + img_direction
            if distance_map_x < 0:
                bearing += 180
        elif distance_map_y < 0:
            bearing = 180 + img_direction

        print("\nBearing: " + str(bearing))
        print("Distance: " + str(distance_map) + "\n")
        # http://www.movable-type.co.uk/scripts/latlong-vincenty.html
        # Millimeter accuracy. To get to nanometer accuracy, will have to switch from Vincenty to Karney's method
        waypoint = drone.destination(distance_map, bearing)

        rover_path.append([waypoint.lat, waypoint.lon])

    print("Drone Coordinate: ")
    print(drone)
    print("Path:")
    for wp in rover_path:
        print(wp)
    return rover_path

# directory = 'CameraCalibration/pixeltocoordinate_imagetesting/'
# PATH = []
# img = cv.imread(f'{directory}Distance_Testing-constantobjsize1.png')
# sensor_H = img.shape[1] # pixel dimensions of camera sensor/photo (should be the same thing)
# sensor_V = img.shape[0]
# for i in [[0,0],[825,460],[sensor_H, sensor_V//2]]:
#     testpixel = Node()
#     testpixel.x = i[0]
#     testpixel.y = i[1]
#     PATH.append(testpixel)
# ROVERPATH = pixelstocoordinates(PATH, directory)
