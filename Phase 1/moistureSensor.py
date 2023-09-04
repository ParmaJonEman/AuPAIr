import board

import cv2

import os

import time

import sys, getopt

from datetime import date

from datetime import datetime

from adafruit_seesaw.seesaw import Seesaw

import configparser

from Adafruit_IO import Client, Feed, RequestError

def readConfig():
    config = configparser.ConfigParser()
    config.read("config.ini")
    cameraFlip = False
    rollingAverage = False
    numReadings = 1
    if(config['cameras']['flip'] == 'true'):
        cameraFlip = True
    if(config['DEFAULT']['rollingAverage'] == 'true'):
        rollingAverage = True
        numReadings = int(config['DEFAULT']['numReadings'])
    cameraCount = config['cameras']['count']
    filePrefix = config['files']['prefix']
    return cameraFlip, cameraCount, filePrefix, rollingAverage, numReadings

def setupFolderAndFile(labMode, filePrefix):
    if(labMode):
        print("Lab Mode On")
        print("Press Spacebar to take a reading or ESC to quit")
        baseDirectory = '/home/admin/Desktop/'
        if(not os.path.exists(baseDirectory + 'AuPAIr')):
            os.mkdir(baseDirectory + 'AuPAIr/')
    else:
        baseDirectory = '/home/admin/shared/'
        bashCommand = "rclone --vfs-cache-mode writes mount \"Onedrive\": /home/admin/shared &"
        try:
            os.system(bashCommand)
        except:
            deleteCacheCommand = "rmdir -r /home/admin/.cache/rclone/vfs/Onedrive"
            os.system(deleteCacheCommand)
            time.sleep(5)
            os.system(bashCommand)
        time.sleep(15)
    
    today = date.today().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H_%M_%S")
    folderPath = baseDirectory + 'AuPAIr/' + today
    fileName = filePrefix + "_" + timestamp
    if(not os.path.exists(folderPath)):
        os.mkdir(folderPath)
    return today, timestamp, folderPath, fileName

def getSoilSensorReading():
    try:
        i2c_bus = board.I2C() 
        ss = Seesaw(i2c_bus, addr=0x36)
        touch = ss.moisture_read()
        temp = ss.get_temp()
        return "temp: " + str(temp) + "  moisture: " + str(touch), str(touch)
    except Exception as e:
        return "An error occurred taking a soil moisture reading: " + str(e)
    
def getSoilSensorReadingRollingAverage(numReadings):
    try:
        i2c_bus = board.I2C() 
        ss = Seesaw(i2c_bus, addr=0x36)
        touch = ss.moisture_read()
        temp = ss.get_temp()
        f = open("rollingMoistureData.txt", "a+")
        f.seek(0)
        listOfReadings = f.readlines()
        print(listOfReadings)
        while(len(listOfReadings) > (numReadings - 1)):
            listOfReadings.pop(0)
        listOfReadings.append(str(touch) + "\n")
        print("truncating")
        f.seek(0)
        f.truncate()
        print("writing list of readings")
        print(listOfReadings)
        f.writelines(listOfReadings)
        f.close()
        sum = 0
        for x in listOfReadings:
            sum += int(x)
        average = sum/len(listOfReadings)
        print("average: " + str(average))
        return "temp: " + str(temp) + "  moisture: " + str(average), str(average)
    except Exception as e:
        print(str(e))
        return "An error occurred taking a soil moisture reading: " + str(e), "Error"
        
def takePictureAndSave(directory, file, cameraFlip):
    cam = cv2.VideoCapture(0)            
    ret, image = cam.read()
    if(cameraFlip):
        image = cv2.rotate(image, cv2.ROTATE_180)
    print(directory + "/" + file)
    cv2.imwrite(directory + "/" + file, image)
    cam.release()
    
def takeLabModePicture(directory, file, image):
    print(directory + "/" + file)
    cv2.imwrite(directory + "/" + file, image)
    
def labModeViewer(folderPath, today, cameraFlip, filePrefix):
    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        if(cameraFlip):
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        cv2.imshow('Live View', frame)
        c = cv2.waitKey(1)
        if c == 27:
            cv2.destroyAllWindows()
            cam.release()
            break
        if c == 32:
            timestamp = datetime.now().strftime("%H_%M_%S")
            reading, moisture = getSoilSensorReading()
            print(reading)
            writeToLog(filePrefix + " " + today + " " + timestamp, reading, folderPath, 1)
            fileName = filePrefix + "_" + timestamp + "_" + moisture + ".jpg"
            takeLabModePicture(folderPath, fileName, frame)
    
def writeToLog(prefix, reading, folderPath, labMode):
    print("writing to log")
    logFile = open(folderPath + "/log.txt", 'a+')
    logFile.write(prefix + " - " + reading + "\n")
    logFile.close()
    if(not labMode):
        bashCommand = "fusermount -u /home/admin/shared"
        os.system(bashCommand)
        
def parseArgs(argv):
    opts, args = getopt.getopt(argv,"hl")
    for opt, arg in opts:
      if opt == '-h':
         print ('moist.py [-l]')
         sys.exit()
      elif opt in ("-l"):
          return 1
    return 0

def main(argv):
    labMode = parseArgs(argv)
    cameraFlip, cameraCount, filePrefix, rollingAverage, numReadings = readConfig()
    
    today, timestamp, folderPath, fileName = setupFolderAndFile(labMode, filePrefix)

    if(labMode):
        labModeViewer(folderPath, today, cameraFlip, filePrefix)
    else:
        if(rollingAverage):
            reading, moisture = getSoilSensorReadingRollingAverage(numReadings)
        else:
            reading, moisture = getSoilSensorReading()
        print(reading)
        writeToLog(filePrefix + " " + today + " " + timestamp, reading, folderPath, 0)
        fileName = fileName + "_" + moisture + ".jpg"
        takePictureAndSave(folderPath, fileName, cameraFlip)
        
if __name__ == "__main__":
   main(sys.argv[1:])



