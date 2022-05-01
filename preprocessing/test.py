# from deepface import DeepFace

from PIL import Image
import face_recognition
import cv2
import time
from tqdm import tqdm
import numpy as np
import pandas as pd
import os
from lowerJitters import returnLowJitterList
from notDumb import getNotDumb

def getSceneStartEndFrames(pathToCSV):
    file = open(pathToCSV, "r")
    lines = file.readlines()

    sceneFrameTuples = []
    for i in range(2, len(lines)):
        split = lines[i].split(',')
        sceneFrameTuples.append( (split[1], split[4]))
    return sceneFrameTuples

def detectFacesWithCV2(images):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    listOfFrameDetections = []
    for image in tqdm(images):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        listOfFrameDetections.append(faces)
    return listOfFrameDetections

def detectFacesWithFaceRec(images):
    listOfFrameDetections = []
    for image in tqdm(images):
        altered = image[:, :, ::-1]
        locs = face_recognition.face_locations(altered, model="cnn")
        
        listOfFrameDetections.append(locs)
        # print(locs)
    return listOfFrameDetections

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
        returnImages.append(image)
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

print("get images")
images = getImagesFromMP4("The_Bachelor_Season_22_Episode_6.mp4", numToPull=700)
# lowerJitters = getNotDumb()
# for i in range(len(images)):
#     frameInfo = lowerJitters[i]
#     print(i)
#     for person in frameInfo[1]:
#         (top, right, bottom, left) = person[1]
#         print(person)
#         cv2.rectangle(images[i], (left, top), (right, bottom),  (255,0,0), 2)
#         cv2.imshow("thing", images[i])
#         cv2.waitKey()
# exit()


def encodeScrapedPictures(pathToFacePicFolder):
    print("ENCODE SCRAPED")
    namesAndEncodings = []
    id = 0
    for idx, dir in enumerate(os.listdir(pathToFacePicFolder)):
        
        pathToPersonFolder = os.path.join(pathToFacePicFolder, dir)
        singlesPhotoEncodings = []
        multiplePhotoEncodings = []
        for pic in os.listdir(pathToPersonFolder):
            image = cv2.imread(os.path.join(pathToPersonFolder, pic))
            encodings = face_recognition.face_encodings(image, num_jitters=15, model="large")
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
            if distances[indexOfSmallest] < 0.6:
                newEncodingsToAdd.append(set[indexOfSmallest])
        # print(dir)
        # print(len(singlesPhotoEncodings))
        # print(len(newEncodingsToAdd))
        individualEncodings = singlesPhotoEncodings + newEncodingsToAdd
        finalFaceEncoding = np.average(np.array(individualEncodings), axis=0)
        print(dir)
        print(face_recognition.face_distance([encodingBasedOnSingles], finalFaceEncoding))
        input()
        # print("final singles")
        # print(face_recognition.face_distance(singlesPhotoEncodings, finalFaceEncoding))
        # print('first singles')
        # print(face_recognition.face_distance(singlesPhotoEncodings, encodingBasedOnSingles))
        # if len(newEncodingsToAdd) != 0:
        #     print('final')
        #     print(face_recognition.face_distance(newEncodingsToAdd, finalFaceEncoding))
        #     print("first")
        #     print(face_recognition.face_distance(newEncodingsToAdd, encodingBasedOnSingles))
        # input()
            

        namesAndEncodings.append( (dir, id, finalFaceEncoding))
        id += 1
        
    return [ [(x[0], x[1]) for x in namesAndEncodings] , [x[2] for x in namesAndEncodings]]

namesToFaceEncodings = encodeScrapedPictures("./peopleBasePictures")


def produceLocationsAndRecognitionsForImageList(namesIDsToFaceEncodings, images):
    print("produceLocationsAndRecognitionsForImageList")
    facesToLookFor = namesIDsToFaceEncodings[1]

    bboxesAndIdentifiersByFrame = []
    for i in tqdm(range(len(images))):
        frame = images[i]

        alteredFrame = frame[:, :, ::-1]
        locs = face_recognition.face_locations(alteredFrame, model="cnn")

        encodings = face_recognition.face_encodings(alteredFrame, known_face_locations = locs, num_jitters=3)
        
        
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

print(bboxesAndIdentifiersByFrame)
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

# ---------------------------------

# ---------------------------
# images = getImagesFromMP4("The_Bachelor_Season_22_Episode_6.mp4", numToPull=1000)
# # params for ShiTomasi corner detection
# feature_params = dict( maxCorners = 100,
#                        qualityLevel = 0.3,
#                        minDistance = 7,
#                        blockSize = 7 )
# # Parameters for lucas kanade optical flow
# lk_params = dict( winSize  = (15, 15),
#                   maxLevel = 2,
#                   criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
# # Create some random colors
# color = np.random.randint(0, 255, (100, 3))
# # Take first frame and find corners in it

# old_gray = cv2.cvtColor(images[0], cv2.COLOR_BGR2GRAY)
# p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)
# # Create a mask image for drawing purposes
# mask = np.zeros_like(images[0])
# for frame in images[1:]:
    
#     frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     # calculate optical flow
#     p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
#     if not st.any():
#         cv2.imshow('frame', frame)
#         print(st)
#         cv2.waitKey()
#     old_gray = frame_gray.copy()
#     continue
#     # Select good points
#     # if p1 is not None:
#     #     good_new = p1[st==1]
#     #     good_old = p0[st==1]
#     # # draw the tracks
#     # for i, (new, old) in enumerate(zip(good_new, good_old)):
#     #     a, b = new.ravel()
#     #     c, d = old.ravel()
#     #     mask = cv2.line(mask, (int(a), int(b)), (int(c), int(d)), color[i].tolist(), 2)
#     #     frame = cv2.circle(frame, (int(a), int(b)), 5, color[i].tolist(), -1)
#     # img = cv2.add(frame, mask)
#     if not st:
#         cv2.imshow('frame', frame)
#     k = cv2.waitKey(30) & 0xff
#     # if k == 27:
#     #     break
#     # Now update the previous frame and previous points
#     old_gray = frame_gray.copy()
#     # p0 = good_new.reshape(-1, 1, 2)
# cv2.destroyAllWindows()
# --------------------


# start_time = time.time()
# print("rectangles")
# for i in range(len(images)):
#     drawRectanglesAndSaveImage(faceDetections[i], images[i], "./processedImages/" + str(i) + ".png")
# print(start_time - time.time())

# result = DeepFace.analyze(img_path = "twoBros.webp", actions=[])
# print(result)
# im = Image.open('twoBros.webp')

# x,y,w,h = result["region"]["x"],result["region"]["y"],result["region"]["w"],result["region"]["h"]
# drawBoundingBox(x,y,w,h,im)