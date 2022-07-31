#CalibrateCamera.py
#Last Updated: 02/21/2021
#Last Updated with Python 3.7.0, OpenCV 4.5.4 and NumPy 1.21.5

#This program calculates the distortion parameters of a camera.
#A video must first be taken of a chessboard pattern moved to a variety of positions
#in the field of view with a camera.

from logging import raiseExceptions
import cv2, sys
import numpy as np
import glob

#Import Video Information
filename = 'CameraCalibrationVideo1.mp4'
#Directory Information
checkerboard_directory = '1__CheckerboardPhotos_ELP-OV2710-2.1mm/'
#Define dimensions of board (width and height) - number of corners of internal squares
board_w = 9
board_h = 6
#Length of each square (in mm)
square_size = 24
#Image resolution
#image_size = (1920, 1080) # <-- Don't need this

#The ImageCollect function requires two input parameters.  Filename is the name of the file
#in which checkerboard images will be collected from.  n_boards is the number of images of
#the checkerboard which are needed.  In the current writing of this function an additional 5
#images will be taken.  This ensures that the processing step has the correct number of images
#and can skip an image if the program has problems.

#This function loads the video file into a data space called video.  It then collects various
#meta-data about the file for later inputs.  The function then enters a loop in which it loops
#through each image, displays the image and waits for a fixed amount of time before displaying
#the next image.  The playback speed can be adjusted in the waitKey command.  During the loop
#checkerboard images can be collected by pressing the spacebar.  Each image will be saved as a
#*.png into the directory which stores this file.  The ESC key will terminate the function.
#The function will end once the correct number of images are collected or the video ends.
#For the processing step, try to collect all the images before the video ends.

def ImageCollect(filename, checkerboard_directory):
    #Collect Calibration Images
    print('-----------------------------------------------------------------')
    print('Loading video...')

    #Load the file given to the function
    video = cv2.VideoCapture(filename)
    #Checks to see if a the video was properly imported
    status = video.isOpened()

    if status == True:

        #Collect metadata about the file.
        FPS = video.get(cv2.CAP_PROP_FPS)
        FrameDuration = 1/(FPS/1000)
        width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        size = (int(width), int(height))
        total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)

        #Initializes the frame counter and collected_image counter
        current_frame = 0
        collected_images = 0

        #Video loop.  Press spacebar to collect images.  ESC terminates the function.
        while current_frame < total_frames:
            success, image = video.read()
            current_frame = video.get(cv2.CAP_PROP_POS_FRAMES)
            cv2.imshow('Video', image)
            k = cv2.waitKey(int(FrameDuration)) #You can change the playback speed here
            if k == 32:
                collected_images += 1
                ret = cv2.imwrite(f'{checkerboard_directory}Calibration_Image' + str(collected_images) + '.png', image)
                if ret == False:
                    raise Exception('Unable to write image')
                print(str(collected_images) + ' images collected.')
            if k == 27:
                break

        #Clean up
        video.release()
        cv2.destroyAllWindows()
        return collected_images
    else:
        print('Error: Could not load video')
        sys.exit()


#The ImageProcessing function performs the calibration of the camera based on the images
#collected during ImageCollect function.  This function will look for the images in the folder
#which contains this file.  The function inputs are the number of boards which will be used for
#calibration (n_boards), the number of squares on the checkerboard (board_w, board_h) as
#determined by the inside points (i.e. where the black squares touch).  square_size is the actual
#size of the square, this should be an integer.  It is assumed that the checkerboard squares are
#square.

#This function first initializes a series of variables. selected_opts will store the true object points
#(i.e. checkerboard points) of selected images with good corners.
#Ipts will store the points as determined by the calibration images.
#The function then loops through each image.  Each image is converted to grayscale, and the
#checkerboard corners are located.  If it is successful at finding the correct number of corners, the
#corners are displayed with the image.
#Click x to not include image, click any other key to not include image in cameracalibration.
#If the points are not found that image or image isn't selected, is skipped.
#If the points are found and the image is selected, all true points and the measured points are stored into selected_opts and seected_ipts.
#Once all images have been analyzed for checkerboard points, the calibration
#parameters (intrinsic matrix and distortion coefficients) are calculated.

#The distortion parameter are saved into a numpy file (calibration_data.npz).  The total
#total reprojection error is calculated by comparing the "true" checkerboard points to the
#image measured points once the image is undistorted.  The total reprojection error should be
#close to zero.

#Finally the function will go through the calbration images and display the undistorted image.

def ImageProcessing(n_boards, board_w, board_h, square_size, checkerboard_directory):
    #Initializing variables
    board_n = board_w * board_h
    opts = []
    ipts = []
    npts = np.zeros((n_boards, 1), np.int32)
    intrinsic_matrix = np.zeros((3, 3), np.float32)
    distCoeffs = np.zeros((5, 1), np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

    # prepare object points based on the actual dimensions of the calibration board
    # like (0,0,0), (25,0,0), (50,0,0) ....,(200,125,0)
    objp = np.zeros((board_h*board_w,3), np.float32)
    objp[:,:2] = np.mgrid[0:(board_w*square_size):square_size,0:(board_h*square_size):square_size].T.reshape(-1,2)

    # EDITED
    IMAGES = glob.glob(f'{checkerboard_directory}Calibration*.png')
    print(f'Total of {len(IMAGES)} calibration images found in {checkerboard_directory}\n')
    for i in range(1, n_boards+1):

        #Loading images
        print ('Loading... Calibration Image... ' + IMAGES[i-1][len(checkerboard_directory):])
        image = cv2.imread(IMAGES[i-1]) # EDITED

        #Converting to grayscale
        grey_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        #Find chessboard corners
        found, corners = cv2.findChessboardCorners(grey_image, (board_w,board_h),cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE) # EDITED
        print (found)

        if found == True:
            #Improve the accuracy of the checkerboard corners found in the image and save them to the ipts variable.
            corners = cv2.cornerSubPix(grey_image, corners, (20, 20), (-1, -1), criteria)

            #Draw chessboard corners
            cv2.drawChessboardCorners(image, (board_w, board_h), corners, found)

            #Show the image with the chessboard corners overlaid.
            cv2.imshow("Corners", image)

            char = cv2.waitKey(10000)
            if char != 120: # lowercase x
                #Add the "true" checkerboard corners
                opts.append(objp)
                
                #Add the measured checkerboard corners
                ipts.append(corners)
            #char = cv2.waitKey(0)

    cv2.destroyWindow("Corners")

    print ('')
    print ('Finished processing images.')
    print (f'Out of {len(IMAGES)} images, {len(ipts)} images were selected by you.')
    print ('')

    #Calibrate the camera
    print ('Running Calibrations...')
    print (' ')
    ret, intrinsic_matrix, distCoeff, rvecs, tvecs = cv2.calibrateCamera(opts, ipts, grey_image.shape[::-1],None,None)

    #Save matrices
    print('Intrinsic Matrix: ')
    print(str(intrinsic_matrix))
    print('\n Distortion Coefficients: ')
    print(str(distCoeff))
    print('\n Rotation Vectors: ')
    print(str(rvecs))
    print('\n Translation Vectors: ')
    print(str(tvecs))

    #Calculate the total reprojection error.  The closer to zero the better.
    tot_error = 0
    for i in range(len(opts)):
        imgpoints2, _ = cv2.projectPoints(opts[i], rvecs[i], tvecs[i], intrinsic_matrix, distCoeff)
        error = cv2.norm(ipts[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        tot_error += error
    reproj_error = tot_error/len(opts)

    print ('total reprojection error: ', reproj_error)

    #Save data
    print ('Saving data file...')
    camera_dimensions = grey_image.shape[::-1] # width by length
    np.savez('calibration_data_TEMP', distCoeff=distCoeff, intrinsic_matrix=intrinsic_matrix, camera_dimensions=camera_dimensions, reproj_error=reproj_error)
    print ('Calibration complete')

    #Undistort Images
    for i in range(1, n_boards+1):

        #Loading images
        print ('Loading... Calibration Image... ' + IMAGES[i-1][len(checkerboard_directory):])
        image = cv2.imread(IMAGES[i-1])

        # undistort
        dst = cv2.undistort(image, intrinsic_matrix, distCoeff, None)

        cv2.imshow('Undistorted Image',dst)
        cv2.imwrite(f'{checkerboard_directory}undistorted_{IMAGES[i-1][len(checkerboard_directory)+12:-4]}.png', dst)

        char = cv2.waitKey(0)

    cv2.destroyAllWindows()


print('Starting camera calibration....')
print('Step 1: Image Collection')
print('We will playback the calibration video.  Press the spacebar to save')
print('calibration images.')
print(' ')
print('Collect as many images as you need. ~20 calibration images are recommended')
print(' ')
print('Once satisfied, wait for video to end or press ESC')

ImageCollect(filename, checkerboard_directory)
#Number of collected board images in the directory (recommended: ~20)
n_boards = len(glob.glob(f'{checkerboard_directory}Calibration*.png'))
print(' ')
print(f'Total of {n_boards} calibration images found in {checkerboard_directory}')
print('------------------------------------------------------------------------')
print('Step 2: Calibration')
print('We will analyze the images taken and calibrate the camera.')
print(' ')
print('Press \'x\' to exclude an image with inaccurate corner mapping from')
print('the calibration calculations as the image windows appear.')
print(' ')

ImageProcessing(n_boards, board_w, board_h, square_size, checkerboard_directory)