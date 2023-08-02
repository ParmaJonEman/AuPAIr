import board

import cv2

import os

import time

from datetime import date

from datetime import datetime

from adafruit_seesaw.seesaw import Seesaw



def setupFolderAndFile():
    bashCommand = "rclone --vfs-cache-mode writes mount \"Onedrive\": /home/admin/shared &"
    os.system(bashCommand)
    time.sleep(15)
    
    today = date.today().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H_%M_%S")
    folderPath = '/home/admin/shared/AuPAIr/' + today
    fileName = timestamp + ".jpg"
    if(not os.path.exists(folderPath)):
        os.mkdir(folderPath)
    return today, timestamp, folderPath, fileName

def getSoilSensorReading():
    import logging
    try:
        i2c_bus = board.I2C() 
        ss = Seesaw(i2c_bus, addr=0x36)
        touch = ss.moisture_read()
        temp = ss.get_temp()
        return "temp: " + str(temp) + "  moisture: " + str(touch)
    except Exception as e:
        return "An error occurred taking a soil moisture reading: " + str(e)
        
def takePictureAndSave(directory, file):
    cam = cv2.VideoCapture(0)
    ret, image = cam.read()
    image = cv2.rotate(image, cv2.ROTATE_180)
    print(directory + "/" + file)
    cv2.imwrite(directory + "/" + file, image)
    cam.release()
    
def writeToLog(prefix, reading):
    print("writing to log")
    logFile = open(folderPath + "/log.txt", 'a+')
    logFile.write(prefix + " - " + reading + "\n")
    logFile.close()
    bashCommand = "fusermount -u /home/admin/shared"
    os.system(bashCommand)
    
    
today, timestamp, folderPath, fileName = setupFolderAndFile()



takePictureAndSave(folderPath, fileName)
reading = getSoilSensorReading()
print(reading)
writeToLog(today + " " + timestamp, reading)


