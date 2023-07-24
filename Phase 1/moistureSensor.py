import board

import cv2

import os

from datetime import date

from datetime import datetime

from adafruit_seesaw.seesaw import Seesaw



def setupFolderAndFile():
    today = date.today().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H:%M:%S")
    folderPath = '/home/admin/' + today
    fileName = timestamp + ".jpg"
    if(not os.path.exists(folderPath)):
        os.mkdir(folderPath)
    return today, timestamp, folderPath, fileName

def getSoilSensorReading():
    i2c_bus = board.I2C() 
    ss = Seesaw(i2c_bus, addr=0x36)
    touch = ss.moisture_read()
    temp = ss.get_temp()
    return "temp: " + str(temp) + "  moisture: " + str(touch)

def takePictureAndSave(directory, file):
    cam = cv2.VideoCapture(0)
    ret, image = cam.read()
    print(directory + "/" + file)
    cv2.imwrite(directory + "/" + file, image)
    cam.release()
    
def writeToLog(prefix, reading):
    logFile = open(folderPath + "/log.txt", 'a+')
    logFile.write(prefix + " - " + reading + "\n")
    logFile.close()
    
today, timestamp, folderPath, fileName = setupFolderAndFile()



takePictureAndSave(folderPath, fileName)
reading = getSoilSensorReading()
print(reading)
writeToLog(today + " " + timestamp, reading)



