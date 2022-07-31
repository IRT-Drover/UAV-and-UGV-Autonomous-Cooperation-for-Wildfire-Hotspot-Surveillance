# Bug 3
# V3. Coords are represented as LatLon objects. Wall following
# To be implemented into roverCommands

from rplidar import RPLidar
import pickle
from math import sqrt, cos, sin, tan, atan2, asin, pi
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
from pygeodesy.ellipsoidalVincenty import LatLon
from pygeodesy import Datums
import time
import pygame


# 2 PURPOSES OF SHORTTERMCORRECTION: 1. dodge obstacles 2. mitigate effect of GPS drift when entering places with obstacles


# Known: Path will be LatLon objects. Progress on path, starting with next unreached coord. First coordinate in remaining path is rover's present location
# Second coordinate is coordinate closest to rover's present location (i.e. next coordinate on path if rover is not in STC or closest coordinate if rover is in STC)

# Two scenarios that can trigger edge following:
# 1. Within 2 meters of traveling distance along path (measured using gps), obstacle within 1 meter of a path point (measured using gps and lidar)


class RoverCommands_temp():
    def __init__(self):
        connection_string = 'udp:127.0.0.1:14551'
        vehicle = connect(connection_string, wait_ready=False)
        vehicle.wait_ready(True, timeout=150)
        
        self.rover_loc = LatLon(vehicle.location.global_relative.lat, vehicle.location.global_relative_frame.lon, datum=Datum.NAD83)
        self.rover_heading = vehicle.heading # not sure if from 0 to 360
        self.rover_loc = LatLon(40.1, -70.1, datum=Datums.NAD83)
        self.rover_heading = 0

        self.lidar = RPLidar('/dev/ttyUSB0')
        info = self.lidar.get_info()
        print('Lidar Info: ' , info)
        health = self.lidar.get_health()
        print('Lidar Health: ' , health)

        # Setting wall following constants
        self.prev_error = 0.0
        self.kp = 14.0
        self.kd = 0.09
        self.vel_input = 1 # will be set according the velocity defined in navigation
        
        
        pygame.init()
        self.lcd = pygame.display.set_mode((640,480))
        pygame.mouse.set_visible(True)
        self.lcd.fill((0,0,0))
        pygame.display.update()
        # used to scale data to fit on the screen
        self.max_distance = 0

    def closeLidar(self):
        self.lidar.stop()
        self.lidar.disconnect()

    def display(self, data):
        
        ## black screen. center is blue. detected lidar points white
        self.lcd.fill((0,0,0))
        self.lcd.set_at((320, 240), pygame.Color(0,0,255))
        pygame.draw.circle(self.lcd, pygame.Color(0,0,255), (320,240), 3, 0)

        for angle in range(360):
            dist = data[angle]
            if dist > 0:
                self.max_distance = max([min([5000, dist]), self.max_distance])
                radians = (angle+180) % 360 * pi / 180.0
                x = dist * cos(radians)
                y = dist * sin(radians)
                point = (320 + int(x / self.max_distance * 480), 240 + int(y / self.max_distance * 480))
                self.lcd.set_at(point, pygame.Color(255, 255, 255))
            
        # print("Obstacle distance: " + str(data[270]))
        # findEdges(data, 270, 0.5)

    # Checks if any lidar point is within danger distance of given coord in the path, starting from nearest to furthest coord
    # Sets avoidance mode to True if STC is required, False if not.
    def avoidanceModeOn(self, path, data):
        
        future_dist_traveled = 0
        for coordex in range(len(path)-1):
            # # Finds where Rover is on the path. ## IS GIVEN BY INPUT PATH
            # progress = LatLon(path[0][0],path[0][1],datum=Datums.NAD83)
            # remaining_path = [coord for coord in path]
            # for coordex in range(len(path)): # Searches for nearest.
            #      coord = LatLon(path[coordex][0],path[coordex][1],datum=Datums.NAD83)
            #      if self.rover_loc.distanceTo(coord) < self.rover_loc.distanceTo(progress):
            #         progress = coord
            #         remaining_path = remaining_path[coordex:]
            
            if future_dist_traveled <= 2: # Only checks coords within 10 meters of travel distance (not including dist between rover and next coord on path) to avoid premature reaction to path doubling back on itself and to save run time
                coord_1 = path[coordex]
                coord_2 = path[coordex+1]
                dist_1, bearing_1, _ = self.rover_loc.distanceTo3(coord_1)
                # print(str(dist_1) + ', bearing:' + str(bearing_1))
                angle_1 = ((360 - (bearing_1 - self.rover_heading) + 90) % 360)*pi/180
                # print(str(dist_1) + ', angle:' + str(angle_1))
                dist_2, bearing_2, _ = self.rover_loc.distanceTo3(coord_2)
                angle_2 = ((360 - (bearing_2 - self.rover_heading) + 90) % 360)*pi/180
                
                # Path points as cartesian coordinates with rover at origin
                coord_1_x = dist_1*cos(angle_1)
                coord_1_y = dist_1*sin(angle_1)
                coord_2_x = dist_2*cos(angle_2)
                coord_2_y = dist_2*sin(angle_2)
                # print("path coordinate: " + str(coord_1_x) + "," + str(coord_1_y))
                
                
                h = coord_1_x + (coord_2_x - coord_1_x)/2 # center of path points: x coord
                k = coord_1_y + (coord_2_y - coord_1_y)/2 # center of path points: y coord
                a = sqrt((coord_2_x - coord_1_x)**2 + (coord_2_y - coord_1_y)**2) # distance between 2 path points
                theta = atan2((coord_2_y-coord_1_y),(coord_2_x-coord_1_x)) # angle between 2 path points
                # Once edge following mode is on, rover will, at most, go 1 meter close to obstacle. Mitigates effect of gps drift
                r = 1.5 # radius of trigger area ## CHANGE BASED ON ACCURACY OF ROVER GPS (error). 1.5 meters and not 1 bc doesn't trust gps drift
                
                ##
                if coordex != 0:
                    future_dist_traveled += a
                ##
            
                # Checks if any lidar point is within distance of path coord
                # If a lidar point is within given area perimeter (Stadium/capsule shape created around two consecutive path points basically forming chain links), trigger obstacle avoidance protocol.
                # Or trigger protocol if point is closer than 1 meter at front or 0.75 meter at side
                for degree in range(360):
                    # LATER CHANGE SO DOESN'T EVEN ITERATE THROUGH 90-270 TO SAVE TIME
                    # print("---")
                    # print(degree , data[degree])
                    # print("---")
                    
                    # No go zone # necessary to be in this function bc of possible gps drift (gps thinks rover is on course when it's actually about to hit  wall)
                    # if (data[degree] < 1 and (degree <= 35 or degree >= -35)) or (data[degree] < 0.75):
                    #     print('TRIGGER OBSTACLE AVOIDANCE MODE: obstacle too close')
                    #     return [True, degree] # True and obstacle coordinate in lidar graph
                    
                    angle = ((360 - degree + 90) % 360)*pi/180
                    x = data[degree]*cos(angle) # lidar x coord
                    y = data[degree]*sin(angle) # lidar y coord
                    
                    # print('Lidar point coordinate: ' + str(x) + ' , ' + str(y))
                    # print(r**2-((x-h)*sin(theta)-(y-k)*cos(theta))**2)
                    # If lidar point is within area around remaining path and is within 2.5 meters of vehicle, edge following mode is turned on
                    try:
                        if (((x-h)*cos(theta)+(y-k)*sin(theta))-a/2-sqrt(r**2-((x-h)*sin(theta)-(y-k)*cos(theta))**2))*(((x-h)*cos(theta)+(y-k)*sin(theta))+a/2+sqrt(r**2-((x-h)*sin(theta)-(y-k)*cos(theta))**2))*(((x-h)*sin(theta)-(y-k)*cos(theta))**2-r**2) >= 10**(-5): ## capsule shape cartesian equation ##
                            print('TRIGGER OBSTACLE AVOIDANCE MODE: obstacle blocking path: Degree ' + str(degree))
                            
                            if coordex == 0:
                                return [True, degree]
                            else:
                                # MIGHT HAVE TO CHECK WHICH COORDINATE IS IN OBSTACLE
                                path = path[coordex:] # removes path points between rover and object, but ensures first path point is still rover location
                                path.insert(self.rover_loc)
                                return [True, degree] # True and obstacle coordinate in lidar graph
                    except ValueError:
                        continue

                    # if obstacle is behind rover (past 90 degrees) and there is no lidar point blocking nearest path point and no lidar point blocking next 10 meters along path,
                    # previous conditionals are all false, so STC mode is False and returns to A* generated path
                    
            else: # stops analyzing scan if no obstacle within 10 meters along path. edge following is False
                break
        return [False, None]


    # p --> [distance, theta] theta is in degrees
    def distance(self, p1, p2):
        dist = sqrt((p1[0])**2 + (p2[0])**2 - 2*p1[0]*p2[0]*cos((p1[1]-p2[1])*pi/180))
        # print("DISTANCE BETWEEN POINTS: " + str(dist))
        return dist

    def findEdges(self, scan_data, originDegree, tolerance):
        
        endPoint_right = [scan_data[originDegree], originDegree]
        # maxdegree = asin(tolerance/scan_data[originDegree]) # FIGURE OUT MATH DOMAIN ERROR # rover can't be within tolerance distance
        # print("maxdegree: " + str(maxdegree))
        degree = originDegree
        for degree in range(originDegree, originDegree+360):
            theta = degree%360
            if scan_data[theta] != 0: # skips infinite distance
                # print("CLOCKWISE")
                if self.distance([scan_data[theta], theta], endPoint_right) <= tolerance: # if distance between endPoint and lidar point is less than meter, make new endPoint
                    endPoint_right = [scan_data[theta], theta]
                    bound_endPoint_right = scan_data[theta] - scan_data[theta-1]
                    # maxdegree = asin(tolerance/scan_data[theta])
                    
                    ## display as red dots
                    self.max_distance = max([min([5000, scan_data[theta]]), self.max_distance])
                    radians = (theta+180) % 360 * pi / 180.0
                    x = scan_data[theta] * cos(radians)
                    y = scan_data[theta] * sin(radians)
                    point = (320 + int(x / self.max_distance * 480), 240 + int(y / self.max_distance * 480))
                    self.lcd.set_at(point, pygame.Color(255, 0, 0))
                    ##
                    
                # else: # if distance to endPoint is greater than tolerance, break
                #     break
            # if ((theta - endPoint_right[1])%360)*pi/180 > maxdegree: # breaks if theta is bigger than maxdegree
            #     break
        # else:
        #     return None
        
        # Same thing to find edge for opposite direction
        endPoint_left = [scan_data[originDegree], originDegree]
        for degree in range(originDegree+360,originDegree, -1):
            theta = degree%360
            if scan_data[theta] != 0:
                # print("COUNTERCLOCKWISE")
                if self.distance([scan_data[theta], theta], endPoint_left) <= tolerance:
                    endPoint_left = [scan_data[theta], theta]
                    # maxdegree = asin(tolerance/scan_data[theta])
                    
                    ##
                    self.max_distance = max([min([5000, scan_data[theta]]), self.max_distance])
                    radians = (theta+180) % 360 * pi / 180.0
                    x = scan_data[theta] * cos(radians)
                    y = scan_data[theta] * sin(radians)
                    point = (320 + int(x / self.max_distance * 480), 240 + int(y / self.max_distance * 480))
                    self.lcd.set_at(point, pygame.Color(255, 0, 0))
                    ##
                # else:
                #     break
            # if ((theta - endPoint_left[1])%360)*pi/180 > maxdegree:
            #     break
        # else:
        #     return None
        
        return [endPoint_left, endPoint_right]

    def chooseSide(self, path, edges):
            
        # if obstacle hadn't been previously detected, choose edge that's closer to the final destination
        # Converts GPS coord to polar coordinate with rover at origin
        target_coord = path[-1]
        dist, bearing, _ = self.rover_loc.distanceTo3(target_coord)
        theta = ((bearing+360-self.rover_heading) % 360)
        pTarget = [dist, theta]
        
        # Chooses edge closer to final destination
        distToEdgeL = self.distance(edges[0], pTarget)
        distToEdgeR = self.distance(edges[1], pTarget)

        print("Distance to left edge " + str(distToEdgeL))
        print("Distance to right edge " + str(distToEdgeR))
        if distToEdgeL >= distToEdgeR: # (turns right) keeps obstacle on port side if right edge is closer or equal in distance to final destination
            return "port"
        else: # (turns left) keeps obstacle on starboard side if left edge is closer in distance to final destination
            return "starboard"


    def wallFollowing(self, path, scan_data, wallSide, buffer_dist): # wall following algorithm that constantly maintains buffer distance with wall (theory-->https://www.youtube.com/watch?v=GMadsuBmGxU)
        
        # take two lidar rays and calc error from desired trajectory
        def error_finder(scan_data, wallSide, buffer_dist):
            if wallSide == "port":
                # first go to wall after first sensing obstacle
                theta = 10
                a = scan_data[270+theta]
                b = scan_data[270]
                if a == 0: # check if reached corner protocol: continue cluster_tolerance distance, continually checking. If still nothing, then turn until a!=0 rediscovered?
                    pass
                
                alpha = atan2((a*cos(theta) - b)/a*sin(theta)) # angle from desired heading
                pres_dist = b*cos(alpha)
                proj_dist = self.vel_input * 1 # change time if each cycle takes longer than 1 second
                fut_dist = pres_dist + proj_dist * sin(alpha)
                
                error = buffer_dist - fut_dist # error from desired distance
                
            elif wallSide == "starboard":
                # first go to wall after first sensing obstacle
                
                theta = 10
                a = scan_data[90-theta]
                b = scan_data[90]
                if a == 0: # check if reached corner protocol: continue cluster_tolerance distance, continually checking. If still nothing, then turn until a!=0 rediscovered?
                    pass
                
                alpha = atan2((a*cos(theta) - b)/a*sin(theta)) # angle from desired heading
                pres_dist = b*cos(alpha)
                proj_dist = self.vel_input * 1 # change time if each cycle takes longer than 1 second
                fut_dist = pres_dist + proj_dist * sin(alpha)
                
                error = buffer_dist - fut_dist # error from desired distance
        
            return error
        
        def control(error, dt):
            # calculate correct steering
            # x,y velocity vectors
            
            # self.rover_heading = vehicle.heading
            
            alpha_corr = self.kp * error + self.kd * (error-self.prev_error)/dt # angle for correcting steering
            self.prev_error = error
            
            vel_y = sqrt(self.vel_input / ((tan(self.rover_heading - alpha_corr))**2 + 1)) ## will have to check and fix angle direction and stuff
            vel_x = sqrt(self.vel_input - self.vel_input / ((tan(self.rover_heading - alpha_corr))**2 + 1)) ## will have to check and fix angle direction and stuff
            
            return [vel_x, vel_y]
        
        def send_ned_velocity(velocity_x, velocity_y, velocity_z): # vel x parallel to north, vel y parallel to east
            print("Driving w/ velocity: x: " + str(velocity_x) + " y: " + str(velocity_y) + " z: " + str(velocity_z))
            
            """
            Move vehicle in direction based on specified velocity vectors.
            """
            msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
                0,       # time_boot_ms (not used)
                0, 0,    # target system, target component
                mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
                0b0000111111000111, # type_mask (only speeds enabled)
                0, 0, 0, # x, y, z positions (not used)
                velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
                0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
                0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

            # send command to vehicle
            self.vehicle.send_mavlink(msg)
            return True


        t = time.time()
        while True:
        
            scan_data = [0]*360
            for (_, angle, dist) in self.lidar.iter_measurments():
                scan_data[min([359, int(angle)])] = dist/1000
            
            # take two lidar rays and calc error from desired trajectory
            error =  error_finder(scan_data, wallSide)
            # correct steering
            vel_x, vel_y = control(error, time.time()-t)
            t = time.time()
            # send command
            send_ned_velocity("rover", vel_x, vel_y, 0)
        
        
            # Check if rover crosses path. Exit wall following and obstacle avoidance mode if path is crossed.
        
            for coordex in range(2, len(path)-1): # checks each coordinate in path
                
                # Convert segment of path to xy cartesian plane
                start = time.time()
                coord_1 = LatLon(path[coordex][0],path[coordex][1],datum=Datums.NAD83)
                coord_2 = LatLon(path[coordex+1][0],path[coordex+1][1],datum=Datums.NAD83)
                mid1 = time.time()
                print("\n---\nCOORD TIME: " + str(mid1-start))
                
                dist_1, bearing_1, _ = self.rover_loc.distanceTo3(coord_1)
                angle_1 = ((360 - (bearing_1 - self.rover_heading) + 90) % 360)*pi/180
                dist_2, bearing_2, _ = self.rover_loc.distanceTo3(coord_2)
                angle_2 = ((360 - (bearing_2 - self.rover_heading) + 90) % 360)*pi/180
                end = time.time()
                print("CALC DISTANCE TO COORD TIME: " +  str(end-mid1))
                
                print("TOTAL XY CONVERSION TIME: " + str(end-start))
                print("---")
                # time.sleep(2)
                
                # Path points with rover at origin
                p1 = [dist_1*cos(angle_1), dist_1*sin(angle_1)]
                p2 = [dist_2*cos(angle_2), dist_2*sin(angle_2)]
                # slope of path segment
                m_path = (p2[1]-p1[1])/(p2[0]-p1[0])
                
                ### Checks if rover crosses path points
                # code
                ###
                   
                endloop = time.time()
                print("REST: " + str(endloop-end))
                # time.sleep(2)


    def bug3(self, path, cluster_tolerance, buffer_dist):
        
        scan_data = [0]*360
        for (_, angle, dist) in self.lidar.iter_measurments():
            scan_data[min([359, int(angle)])] = dist/1000
        
        # Rover location
        # self.rover_loc = LatLon(vehicle.location.global_relative.lat, vehicle.location.global_relative_frame.lon, datum=Datum.NAD83)
        # self.rover_heading = vehicle.heading # not sure if from 0 to 360
        self.rover_loc = LatLon(40.1, -70.1, datum=Datums.NAD83)
        self.rover_heading = 0

        path.insert(0,self.rover_loc) # sets first coordinate to rover location) 
        print(path[0])
        print("Path length: " + str(len(path)))
        
        self.display(scan_data)
        
        # print("Obstacle distance: " + str(scan_data[270]))
        # findEdges(scan_data, 270, 0.5)
        
        # Wall Following Version
        avoidance_on, obstacle_angle = self.avoidanceModeOn(scan_data)
        # if turned on, find endpoints, choose which the side that will face the wall
        if avoidance_on == True:
            print("Obstacle distance: " + str(scan_data[obstacle_angle]))
            # Searches for and returns endpoints of obstacle
            # start = time.time()
            obstacle_edges = self.findEdges(scan_data, obstacle_angle, cluster_tolerance)
            # end = time.time()
            # print("FIND EDGE TIME: " + str(end-start))
            
            # If there are any path points between rover and the point that intersects obstacle, delete those points. (already did tht in avoidance mode)
            
            # Chooses endpoint that's closest to the final destination
            # start = time.time()
            wallSide = self.chooseSide(obstacle_edges) # port or starboard
            # end = time.time()
            # print("CHOOSE EDGE TIME: " + str(end-start))
            
            
            # once avoidance mode is turned on, start wall following
            avoidance_on = self.wallFollowing(path, scan_data, wallSide, buffer_dist)
        
    

if __name__ == "__main__":
    # TEMP GPSPATH
    with open('GPSDATAPACKAGE.pickle', 'rb') as file:
        GPSPATHS = pickle.load(file)
    path = GPSPATHS['Picture 1']

    # WILL BE DONE RIGHT WHEN PATH IS RECEIVED FROM GOUNDSTATION
    for i in range(len(path)):
        path[i] = LatLon(path[i][0],path[i][1],datum=Datums.NAD83)


    roverCommand = RoverCommands_temp()

    total_time = 0
    scan_count = 0

    cluster_tolerance = 1 # meter
    buffer_dist = 1 # meter

    try:
        
        while True:
            scan_count += 1
            print("\n===========Scan " + str(scan_count) + "===============")
            
            start_time = time.time()
            
            roverCommand.bug3(path, cluster_tolerance, buffer_dist)
            
            pygame.display.flip()
            
            end_time = time.time()
            print("Scan time + Processing time: " + str(round(end_time-start_time,6)))
            print("==========================")
            total_time += (end_time-start_time)
        
    except KeyboardInterrupt:
        print('Stopping.')
        print("Total scans: " + str(total_time))
        print("AVG TIME PER SCAN: " + str(total_time/scan_count))
    roverCommand.closeLidar()