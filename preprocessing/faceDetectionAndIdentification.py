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
import json

def getSceneStartEndFrames(pathToCSV):
    file = open(pathToCSV, "r")
    lines = file.readlines()

    sceneFrameTuples = []
    for i in range(2, len(lines)):
        split = lines[i].split(',')
        sceneFrameTuples.append( (int(split[1]), int(split[4])))
    return sceneFrameTuples


def getContestantInfoAsDataFrame():
    df = pd.read_csv("./contestantInfo.csv")
    retArray = []
    for index, row in df.iterrows():
        retArray.append( row.tolist())
        
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
    for i in tqdm(range(numToPull)):

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

# print("get images")
# images = getImagesFromMP4("epHighQuality.mkv", numToPull=2000)

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
    #    idsToNamesAndFaceEncodings (dict): A map from the contestant id to their name and a list of their face encodings from the pictures
    idsToNamesAndFaceEncodings = {}
    for idx, dir in enumerate(os.listdir(pathToFacePicFolder)):
        
        pathToPersonFolder = os.path.join(pathToFacePicFolder, dir)
        singlesPhotoEncodings = []
        multiplePhotoEncodings = []
        print(dir)
        for pic in os.listdir(pathToPersonFolder):
            image = cv2.imread(os.path.join(pathToPersonFolder, pic))[:,:,::-1]
            locs = face_recognition.face_locations(image, model="cnn")
            encodings = face_recognition.face_encodings(image, known_face_locations = locs, num_jitters=30, model="large")
            if len(encodings) == 0:
                continue
            if len(encodings) == 1:
                singlesPhotoEncodings.append(encodings[0])
            else:
                # print(pic, len(encodings))
                multiplePhotoEncodings.append((image, locs, encodings))
        
        newEncodingsToAdd = []
        encodingBasedOnSingles = np.average(np.array(singlesPhotoEncodings), axis=0)
        for pic, locs, encodings in multiplePhotoEncodings:
            distances = face_recognition.face_distance(encodings, encodingBasedOnSingles)
            indexOfSmallest = np.argmin(distances)
            newEncodingsToAdd.append(encodings[indexOfSmallest])                
                

        individualEncodings = singlesPhotoEncodings + newEncodingsToAdd

        idsToNamesAndFaceEncodings[idx] = (dir, individualEncodings)
        
    return idsToNamesAndFaceEncodings

# idsToNamesAndFaceEncodings = encodeScrapedPictures("./peopleBasePictures")
# print(idsToNamesAndFaceEncodings[0][0])
# input()
# with open("idsToNamesAndFaceEncodings.pkl", 'wb') as  f:
#     pickle.dump(idsToNamesAndFaceEncodings, f)
# exit()

idsToNamesAndFaceEncodings = pickle.load(open("idsToNamesAndFaceEncodings.pkl", 'rb'))
print("loaded idsToNamesAndFaceEncodings")



sceneStartEnd = getSceneStartEndFrames("./epHighQuality-Scenes.csv")

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

def getDetsByScene(sceneTuples, detsByFrame):
    #Gathers the images contained in each scene according to scene tuples

    #Parameters:
    #    sceneTuples (list): A list of tuples where the 0th index is the start frame of the scene and the 1th index is the end frame
    #    detsByFrame (list):A list of lists of tuples where each list is for an image is a list of tuples where the 0th index is the bbox info for the detection and the 1th index is the face encoding

    #Returns:
    #    detsByScene (list): A list of tuples where the 0th index is the scene start/end tuple and the 1th index is a list of lists where each sublist is the list of detections in the frame
    detsByScene = []
    for t in sceneTuples:
        if t[1] >= len(detsByFrame):
            detsByScene.append( ((t[0], len(detsByFrame) -1), detsByFrame[t[0]:]))
            break
        else:
            detsByScene.append((t, detsByFrame[t[0]:t[1]]))
    return detsByScene

def getFaceDetsAndEncodingsForImages(images):
    #Runs facial detection and generates encodings for each image in the images

    #Parameters:
    #    images (list): the images from the video to be processed

    #Returns:
    #    detsForEachImage (list): A list of lists of tuples where each list is for an image is a list of tuples where the 0th index is the bbox info for the detection and the 1th index is the face encoding
    detsForEachImage = []
    for i in tqdm(range(len(images))):
        frame = images[i]
        alteredFrame = frame[:, :, ::-1]
        locs = face_recognition.face_locations(alteredFrame, model="cnn")

        encodings = face_recognition.face_encodings(alteredFrame, known_face_locations = locs, num_jitters=20, model="large")

        faceInfoForThisFrame = []

        for i in range(len(locs)):
            faceInfoForThisFrame.append( (locs[i], encodings[i]))
        detsForEachImage.append(faceInfoForThisFrame)
    return detsForEachImage

detsForEachImage = pickle.load(open("detsForEachImageFirst2kFrames.pkl", 'rb'))

detsByScene = getDetsByScene(sceneStartEnd, detsForEachImage)


def flattenIdsToNamesAndFaceEncodingsWithMap(idsToNamesAndFaceEncodings):
    #Flattens idsToNameAndFaceEncodings and returns that along with a map from the index in the list to the person's id

    #Parameters:
    #    idsToNamesAndFaceEncodings (dict): A map from the contestant id to their name and a list of their face encodings from the pictures
    # 
    #Returns:
    #    encodingsList (list): A list of face encodings
    #    indexToIDMap (dict): A map from the encodings' indices to the relevant ID

    encodingsList = []
    indexToIDMap = {}
    
    currIndex = 0
    for id in idsToNamesAndFaceEncodings:

        for encoding in idsToNamesAndFaceEncodings[id][1]:

            encodingsList.append(encoding)
            indexToIDMap[currIndex] = id
            currIndex += 1

    return encodingsList, indexToIDMap

def assignDetsToPersonForEachScene(detsByScene, idsToNamesAndFaceEncodings):
    #Gathers the images contained in each scene according to scene tuples

    #Parameters:
    #    detsByScene (list): A list of tuples where the 0th index is the scene start/end tuple and the 1th index is a list of lists where each sublist is the list of detections in the frame
    #    idsToNamesAndFaceEncodings (dict): A map from the contestant id to their name and a list of their face encodings from the pictures
    # 
    #Returns:
    #    assignedDetectionsByFrame (list): A list of assigned detections for each frame as tuples in the form (contestant id, bbox info)    

    assignedDetectionsByFrame = []

    
    encodingsList, indexToIDMap = flattenIdsToNamesAndFaceEncodingsWithMap(idsToNamesAndFaceEncodings)
    for sceneDets in detsByScene:
        assignedDetsForScene = assignDetsToPersonForSceneKNNWithBBoxOverlap(sceneDets, encodingsList, indexToIDMap)
        assignedDetectionsByFrame = assignedDetectionsByFrame + assignedDetsForScene
    
    return assignedDetectionsByFrame

def getOverlapFraction(bbox1, bbox2):
    #Calculates the fraction of pixels shared betwen two bounding boxes

    #Parameters:
    #   bbox1 (tuple) :  a bbox descriptor in (top, right, bottom, left) format
    #   bbox2 (tuple) :  a bbox descriptor in (top, right, bottom, left) format

    #Returns:
    #   The fraction of pixels shared between the bounding boxes

    top1, right1, bottom1, left1 = bbox1
    area1 = (bottom1 - top1) * (right1 - left1)
    top2, right2, bottom2, left2 = bbox2
    area2 = (bottom2 - top2) * (right2 - left2)

    dx = min(right1, right2) - max(left1, left2)
    dy = min(bottom1, bottom2) - max(top1, top2)
    if (dx>=0) and (dy>=0):
        overlapArea = dx*dy
    else:
        overlapArea = 0
    return (2*overlapArea)/(area1 + area2)


def assignDetsToPersonForScenePureKNN(sceneDets, encodingsList, indexToIDMap):
    #Gathers the images contained in each scene according to scene tuples

    #Parameters:
    #    sceneDets (list): A tuple where the 0th index is the frame start and end of the scene and the 1th index is a list of lists of tuples where each sub-list is the detections for a given frame with each detection represented as a tuple where the 0th index is bbox info and the 1th index is the encoding
    #    encodingsList (list): A list of face encodings
    #    indexToIDMap (dict): A map from the encodings' indices to the relevant ID
    # 
    #Returns:
    #    assignedDetectionsByFrame (list): A list of tuples where the 0th index of  of assigned detections for each frame as tuples in the form (contestant id, bbox info)

    assignedDetectionsByFrame = []
    frameBoundsOfScene = sceneDets[0]

    for idx, frame in enumerate(sceneDets[1]):
        frameNumAbsolute = frameBoundsOfScene[0] + idx
        IDedDets = []
        for det in frame:
            
            encoding = det[1]
            distances =  face_recognition.face_distance(encodingsList, encoding)
            bestDistIndices = np.argpartition(distances, 3)[:3]
            bestIDsAndDistances = []
            id = None
            topIDs = set()
            for idx in bestDistIndices:
                if(indexToIDMap[idx] in topIDs):
                    id = indexToIDMap[idx]
                    break
                else:
                    topIDs.add(indexToIDMap[idx])
            if id == None:
                id = indexToIDMap[bestDistIndices[0]]
            bbox = det[0]
            if distances[bestDistIndices[0]] <= 0.55:
                IDedDets.append( (id, bbox) )
        if len(IDedDets) > 0:
            assignedDetectionsByFrame.append( (frameNumAbsolute, IDedDets))
    return assignedDetectionsByFrame

def assignDetsToPersonForSceneKNNWithBBoxOverlap(sceneDets, encodingsList, indexToIDMap):
    #Gathers the images contained in each scene according to scene tuples

    #Parameters:
    #    sceneDets (list): A tuple where the 0th index is the frame start and end of the scene and the 1th index is a list of lists of tuples where each sub-list is the detections for a given frame with each detection represented as a tuple where the 0th index is bbox info and the 1th index is the encoding
    #    encodingsList (list): A list of face encodings
    #    indexToIDMap (dict): A map from the encodings' indices to the relevant ID
    # 
    #Returns:
    #    assignedDetectionsByFrame (list): A list of tuples where the 0th index of  of assigned detections for each frame as tuples in the form (contestant id, bbox info)

    assignedDetectionsByFrame = []
    frameBoundsOfScene = sceneDets[0]
    tracks = []
    for idx, frame in enumerate(sceneDets[1]):
        frameNumAbsolute = frameBoundsOfScene[0] + idx

        for det in frame:
            
            encoding = det[1]
            bbox = det[0]

            distances =  face_recognition.face_distance(encodingsList, encoding)
            bestDistIndices = np.argpartition(distances, 3)[:3]
            bestIDsAndDistances = []
            for idx in bestDistIndices:
                bestIDsAndDistances.append( (indexToIDMap[idx], distances[idx]))
    exit()


assignedDetectionsByFrame = assignDetsToPersonForEachScene(detsByScene, idsToNamesAndFaceEncodings)
exit()
mapFrameNumToAssignedDets = {}
for frame in assignedDetectionsByFrame:
    mapFrameNumToAssignedDets[frame[0]] = frame[1]

stringVersion = json.dumps(mapFrameNumToAssignedDets)
KNNWithBBOXOverlapAssignedDetsForEachFrame = open("KNNWithBBOXOverlapAssignedDetsForEachFrame.json", "w+")
KNNWithBBOXOverlapAssignedDetsForEachFrame.write(stringVersion)
exit()


# detsForEachImage = getFaceDetsAndEncodingsForImages(images)
# print(len(detsForEachImage))
# input()
# with open("detsForEachImageFirst2kFrames.pkl", 'wb') as  f:
#     pickle.dump(detsForEachImage, f)
# exit()


def produceLocationsAndRecognitionsForImageList(namesIDsToFaceEncodings, images):
    #Produces a list of information for each frame, and a mapping from the contestant ID's to their information.

    #Parameters:
    #    contestantFaceEncodings (dict): A map from the contestant id to their name and a list of their face encodings from the pictures
    #    images (list): the images from the video to be processed

    #Returns:
    #    contestantFaceEncodings (dict): A map from the contestant id to their name and a list of their face encodings from the pictures
    print("produceLocationsAndRecognitionsForImageList")

    bboxesAndIdentifiersByFrame = []
    for i in tqdm(range(len(images))):
        frame = images[i]

        alteredFrame = frame[:, :, ::-1]
        locs = face_recognition.face_locations(alteredFrame, model="cnn")

        encodings = face_recognition.face_encodings(alteredFrame, known_face_locations = locs, num_jitters=20, model="large")
        
        for id in namesIDsToFaceEncodings:
            name, encodings = namesIDsToFaceEncodings[id]
        
        bboxesWithIdentifiers = []
        # I wanna get the relative score of each face detected in the frame to each face in the contestant set
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
