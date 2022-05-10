# from deepface import DeepFace

from PIL import Image
import face_recognition
import cv2
import time
from tqdm import tqdm
import numpy as np
import pandas as pd
import os
from notDumb import getNotDumb
from deepface import DeepFace
import pickle 

def getSceneStartEndFrames(pathToCSV):
    file = open(pathToCSV, "r")
    lines = file.readlines()

    sceneFrameTuples = []
    for i in range(2, len(lines)):
        split = lines[i].split(',')
        sceneFrameTuples.append( (split[1], split[4]))
    return sceneFrameTuples


def getContestantInfoAsDataFrame():
    df = pd.read_csv("./contestantInfo.csv")
    retArray = []
    for index, row in df.iterrows():
        retArray.append([index] + row.tolist())
        
    return retArray

dataFrameAsList = getContestantInfoAsDataFrame()


def drawRectanglesAndSaveImage(faces, img, savePath):
    for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    # cv2.imwrite(savePath, img)


def getImagesFromMP4(vidPath, numToPull=30):
    vidcap = cv2.VideoCapture(vidPath)
    success,image = vidcap.read()
    returnImages = []
    keep = False
    for i in range(numToPull):

        if not success:
            break
        returnImages.append(image[:,:,::-1])
        success,image = vidcap.read()

    return returnImages

def frameNum(vidPath, numToPull=30):
    vidcap = cv2.VideoCapture(vidPath)
    success,image = vidcap.read()
    i = 0
    while(success):
        if not success:
            break
        success,image = vidcap.read()
        i += 1

    print(i)



# frameNum("Debate_ 10th Republican Presidential Candidate Debate - February 25, 2016.mp4")
# exit()
        

# -------------------------------
# Pipleline to make my tags currently
# start_time = time.time()

# sceneStartEndTuples = getSceneStartEndFrames("./sceneInfo/The_Bachelor_Season_22_Episode_6-Scenes.csv")

# print(DeepFace.find(".\peopleBasePictures\Lauren-Burnham\LaurenBurnham0.jpeg", ".\peopleBasePictures",  model_name="Dlib"))
# exit()
print("get images")
# images = getImagesFromMP4("torrentedBachS22E6.mkv", numToPull=700)
images = getImagesFromMP4("epHighQuality.mkv", numToPull=1000)

# lowerJitters = pickle.load(open("output.pkl", "rb"))
# for i in range(len(images)):
#     frameInfo = lowerJitters[i]
#     print(i)
#     new = images[i][:,:,::-1]
#     for person in frameInfo[1]:
#         (top, right, bottom, left) = person[1]
#         print(person)
#         new = cv2.rectangle(new, (left, top), (right, bottom),  (255,0,0), 2)
#         cv2.imshow("thing", new)
#         cv2.waitKey()
# exit()



def encodeScrapedPictures(pathToFacePicFolder):
    #Returns the encoded faces from all the pictures of all the contestants.

    #Parameters:
    #    pathToFacePicFolder (str):the path to the folder containing the contestant images with each sub folder containing several images of the contestants.

    #Returns:
    #    contestantFaceEncodings (dict): A map from the contestant id to their name and a list of their face encodings from the pictures
    idsToNamesAndFaceEncodings = {}
    for idx, dir in enumerate(os.listdir(pathToFacePicFolder)):
        
        pathToPersonFolder = os.path.join(pathToFacePicFolder, dir)
        singlesPhotoEncodings = []
        multiplePhotoEncodings = []
        print(dir)
        for pic in os.listdir(pathToPersonFolder):
            image = cv2.imread(os.path.join(pathToPersonFolder, pic))[:,:,::-1]
            locs = face_recognition.face_locations(image, model="cnn")
            encodings = face_recognition.face_encodings(image, known_face_locations = locs, num_jitters=20, model="large")
            if len(encodings) == 0:
                continue
            if len(encodings) == 1:
                singlesPhotoEncodings.append(encodings[0])
            else:
                # print(pic, len(encodings))
                multiplePhotoEncodings.append(encodings)
        
        newEncodingsToAdd = []
        encodingBasedOnSingles = np.average(np.array(singlesPhotoEncodings), axis=0)
        for set in multiplePhotoEncodings:
            distances = face_recognition.face_distance(set, encodingBasedOnSingles)
            indexOfSmallest = np.argmin(distances)
            print(distances[indexOfSmallest])

            if distances[indexOfSmallest] < 0.6:
                
                newEncodingsToAdd.append(set[indexOfSmallest])

        individualEncodings = singlesPhotoEncodings + newEncodingsToAdd

        print("done appendings")
        idsToNamesAndFaceEncodings[dir] = (idx, individualEncodings)
        
    return idsToNamesAndFaceEncodings

namesToFaceEncodings = encodeScrapedPictures("./peopleBasePictures")


# Split images by scene
# For each scene 
#   for each image in scene
#       for each face detected
#           get distance for each picture of person
#   Decide which group of detections is which in between frames
#   define tracks as a list
#   for each image
#       for each detection in image:
#           if first image make a new track
#           else see if they have significant overlap with existing track (even if the there hasn't been a detection for some frames)
#           I will have to keep dormat and non-dormant tracks separate
#   Assign groups of detections based no their (lowest? aggregate?) dostance from each person in the databse

def produceLocationsAndRecognitionsForImageList(namesIDsToFaceEncodings, images):
    #Produces a list of information for each frame, and a mapping from the contestant ID's to their information.

    #Parameters:
    #    contestantFaceEncodings (dict): A map from the contestant id to their name and a list of their face encodings from the pictures
    #    images (list): the images from the video to be processed

    #Returns:
    #    contestantFaceEncodings (dict): A map from the contestant id to their name and a list of their face encodings from the pictures
    print("produceLocationsAndRecognitionsForImageList")
    facesToLookFor = namesIDsToFaceEncodings[1]

    bboxesAndIdentifiersByFrame = []
    for i in tqdm(range(len(images))):
        frame = images[i]

        alteredFrame = frame[:, :, ::-1]
        locs = face_recognition.face_locations(alteredFrame, model="cnn")

        encodings = face_recognition.face_encodings(alteredFrame, known_face_locations = locs, num_jitters=20, model="large")
        
        for id in namesIDsToFaceEncodings:
            name, encodings = namesIDsToFaceEncodings[id]
        
        bboxesWithIdentifiers = []
        for j in range(len(encodings)):
            distances = face_recognition.face_distance(facesToLookFor, encodings[j])
            bestFace = np.argmin(distances)
            lowestDistance = distances[bestFace]
            if lowestDistance <= 0.6:
                bboxesWithIdentifiers.append((namesIDsToFaceEncodings[0][bestFace][0], locs[j], lowestDistance))
                
        bboxesAndIdentifiersByFrame.append((i, bboxesWithIdentifiers))
    return bboxesAndIdentifiersByFrame

bboxesAndIdentifiersByFrame = produceLocationsAndRecognitionsForImageList(namesToFaceEncodings, images)

with open("output.pkl", 'wb') as  f:
    pickle.dump(bboxesAndIdentifiersByFrame, f)
exit()


start_time = time.time()
print("detect faces")
faceDetections = detectFacesWithFaceRec(images)
file = open("hi.txt", "w+")

for i in range(len(faceDetections)):
    for faceDet in faceDetections[i]:
        strToWrite = str(i) + ','
        for num in faceDet:
            strToWrite += str(num) + ','
        strToWrite = strToWrite[:-1] + '$'
        file.write(strToWrite)
