import cv2
import glob
import random
from Undistort import CameraParameters

# Input preassigned coordinates
coordinates = []

# Function to draw a crosshair at the center of the image
def crosshair(frame, fheight, fwidth):
    # drawing a crosshair
    cv2.line(frame, (fwidth//2-350, fheight//2), (fwidth//2+350, fheight//2), (0, 255, 0), 1)
    cv2.line(frame, (fwidth//2, fheight//2-350), (fwidth//2, fheight//2+350), (0, 255, 0), 1)
# Function to draw a dot at coordinates in the image set before camera feed starts
# parameters of .circle: frame, coordinates, radius, color, line thickness (-1 will fill in circle)
def point(frame, coordinates, color):
    if len(coordinates) != 0 and len(coordinates[0]):
        for coord in coordinates:
            cv2.circle(frame, coord, 4, color, 3)
        
# function to display the coordinates of
# of the points clicked on the image
def click_event(event, x, y, flags, params):
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
 
        # displaying the coordinates
        # on the Shell
        print(x, ' ', y)
 
        # displaying coordinates in incrementing colors
        # on the image window
        # color = random.choice([(255,0,0), (0,255,0), (0,0,255)])
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, str(x) + ',' +
                    str(y), (x,y), font,
                    0.7, (0,0,255), 2)
        point(frame, [(x,y)], (0,0,255))
        point(frame, [(fwidth//2,y)], (0,0,255))

        cv2.imshow('Camera Feed', frame)

# Initiating Camera
camera = cv2.VideoCapture(1)
if not camera.isOpened():
    print("Cannot open camera")
    exit()
# Camera Info for undistortion
cameraparameters = CameraParameters()

ret,frame = camera.read()
print("Camera on...")
result = True

# Press ESC to cancel. Press space to take photo.
# Click on points in image to find and return coordinates of a pixel.
# Press space to keep photo or press any other key to retake.
while(result):
    ret,frame = camera.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    # camera dimensions
    fheight = frame.shape[0]
    fwidth = frame.shape[1]
    
    # undistorts frame
    frame = cameraparameters.undistortPicture(frame)
    
    # adding a crosshair
    crosshair(frame, fheight, fwidth)
    # adding points
    point(frame, coordinates, (255, 0, 0))
    
    # display image
    cv2.imshow('Camera Feed',frame)
    
    # take photo
    take_photo = cv2.waitKey(1)
    if take_photo == 32:
        # select pixels and auto adds corresponding pixel directly horizonal
        # on the vertical axis in the center of the image
        cv2.setMouseCallback("Camera Feed", click_event)
        keep_photo = cv2.waitKey(0)
        if keep_photo == 32:
            cv2.imwrite(f"pixeltocoordinate_imagetesting/Distance_Testing" + "-constantobjsize0" + ".png", frame)
            result = False
    elif take_photo == 27:
        break
camera.release()
cv2.destroyAllWindows()