from mpu6050 import mpu6050
import RPi.GPIO as GPIO
import time
import math
import pigpio

while True:
    try:
        sensor = mpu6050(0x68)

        pi = pigpio.pi()
        pi.set_mode(17, pigpio.OUTPUT)
        pi.set_mode(18, pigpio.OUTPUT)
        #pi.set_servo_pulsewidth(17, 600)
        #pi.set_servo_pulsewidth(18, 2140)
        #print(pi.get_servo_pulsewidth(18))
        #time.sleep(5)
        #time.sleep(10)
        #for i in range(1000):
        #    print("z: ", sensor.get_accel_data().get("z"))
        #    time.sleep(0.25)
        #pi.set_servo_pulsewidth(17, 1500)
        #pi.set_servo_pulsewidth(18, 1500)

        angle1 = 1500
        angle2 = 1500

        def rotateBy(currentWidth, pulseWidth, servo):
            w = currentWidth + pulseWidth
            
            print("Frequency: ", w)
            if w >= 500 and w <= 2500:
                print("Frequency Accepted")

                pi.set_servo_pulsewidth(servo, w)
                
        def updateAngle(angle1, angle2):
            if(angle1 + angle2 >= 2500):
                return 2500
            elif(angle1 + angle2 <= 500):
                return 500
            else:
                return angle1+angle2

        def stabilize(angle, angle2, previousAngle2, counter, factor, accelData, servo1, servo2):
            x = accelData.get("x")
            y = accelData.get("y")
            z = accelData.get("z")
            print("z: ",z)
            print("y value ", y)
            if(angle2 == 500 or angle2 == 2500):
                factor *= -1
                
            if(y > 0.5):
                rotateBy(angle2,  6*factor, servo2)
                angle2 = updateAngle(angle2, 6*factor)
                
            elif(y < 0.5):
                rotateBy(angle2, -6*factor, servo2)
                angle2 = updateAngle(angle2, -6*factor)
            
            if(x > 0.5):
                rotateBy(angle,  3, servo1)
                angle += 3
                
            elif(x < -0.5):
                rotateBy(angle, -3, servo1)
                angle -= 3
            
            
            return angle, angle2, counter, factor, previousAngle2

        counter = 0
        previousAngle2 = angle2
        factor = -1
        while True:
            #print("Data: ", sensor.get_accel_data())
            angle1, angle2, counter, factor, previousAngle2 = stabilize(angle1, angle2, previousAngle2, counter, factor, sensor.get_accel_data(), 17, 18) 
    except KeyboardInterrupt:
        #pi.set_servo_pulsewidth(17, 2400)
        #pi.set_servo_pulsewidth(18, 1500)
        time.sleep(1)
        pi.stop()
    
