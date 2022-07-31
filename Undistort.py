#Undistort.py
#Last Updated: 02/21/2021
#Last Updated with Python 3.7.0, OpenCV 4.5.4 and NumPy 1.21.5

#This program takes an image/images and removes the camera distortion based on the
#camera calibration parameters. The filename and the calibration data filenames
#should be changed where appropriate.

import numpy as np
import cv2, time, sys
import glob

class CameraParameters:
    npz_calib_file = np.load('calibration_data.npz')
    distCoeff = npz_calib_file['distCoeff']
    intrinsic_matrix = npz_calib_file['intrinsic_matrix']
    npz_calib_file.close()
    
    # undistort an image that has already been read
    def undistortPicture(self, img):
        img = cv2.undistort(img, self.intrinsic_matrix, self.distCoeff, None)
        return img

    # read images from a folder and undistort each of them and write them as new photos
    def undistortFolder(self, directory):
        print('Starting to undistort the photos....')

        #Loading images
        IMAGES = glob.glob(f'{directory}*')
        for i in range(0, len(IMAGES)):
            print ('Loading... Image... ' + IMAGES[i][len(directory):])
            image = cv2.imread(IMAGES[i])

            # undistort
            undst = self.undistortPicture(image)

            cv2.imshow('Undistorted Image',undst)
            cv2.imwrite(f'{directory}undst-{IMAGES[i][len(directory):]}', undst)  
        
# directory = 'pixeltocoordinate_imagetesting/'
# camerainfo = CameraParameters()
# camerainfo.undistortFolder(directory)
    
    
#This program first loads the calibration data.  Secondly, the video is loaded and
#the metadata is derived from the file.  The export parameters and file structure
#are then set-up.  The file then loops through each frame from the input video,
#undistorts the frame and then saves the resulting frame into the output video.
#It should be noted that the audio from the input file is not transfered to the
#output file.

#   # filename = 'GOPR0028.MP4'


# print('Loading data files')

# npz_calib_file = np.load('calibration_data.npz')

# # print('total reprojection error: ' + npz_calib_file['reproj_error'])

# distCoeff = npz_calib_file['distCoeff']
# intrinsic_matrix = npz_calib_file['intrinsic_matrix']

# npz_calib_file.close()

# print('Finished loading files')
# print(' ')
# print('Starting to undistort the video....')

# #Loading images
# IMAGES = glob.glob(f'{directory}*')
# for i in range(0, len(IMAGES)):
#     print ('Loading... Calibration Image... ' + IMAGES[i][len(directory):])
#     image = cv2.imread(IMAGES[i])

#     # undistort
#     undst = cv2.undistort(image, intrinsic_matrix, distCoeff, None)

#     cv2.imshow('Undisorted Image',undst)
#     cv2.imwrite(f'{directory}undst-{IMAGES[i][len(directory):]}', undst)  