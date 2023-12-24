import board

import cv2

import os

import time

import sys, getopt

from datetime import date

from datetime import datetime

from adafruit_seesaw.seesaw import Seesaw

import configparser

import RPi.GPIO as GPIO

from Adafruit_IO import Client, Feed, RequestError

pulse_count = 0
start_time = time.time()

def readConfig():
    config = configparser.ConfigParser()
    config.read("config.ini")
    cameraFlip = False
    rollingAverage = False
    pimoroni = False
    numReadings = 1
    if(config['cameras']['flip'] == 'true'):
        cameraFlip = True
    if(config['DEFAULT']['rollingAverage'] == 'true'):
        rollingAverage = True
        numReadings = int(config['DEFAULT']['numReadings'])
    if(config['DEFAULT']['pimoroni'] == 'true'):
        pimoroni = True
    cameraCount = config['cameras']['count']
    filePrefix = config['files']['prefix']
    return cameraFlip, cameraCount, filePrefix, rollingAverage, numReadings, pimoroni

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
        return "An error occurred taking a soil moisture reading: " + str(e), str(e)
    
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
        
def count_pulse(channel):
    global pulse_count
    pulse_count += 1        
    
def getSoilMoisturePimoroni(sensor_pin):
    global start_time
    global pulse_count
    pulses_per_second = 0
    for i in range(0,2):
        # Calculate pulses per second
        current_time = time.time()
        elapsed_time = current_time - start_time
        pulses_per_second = pulse_count / elapsed_time

        # Print the result
        # print(f"Pulses per second: {pulses_per_second:.2f}")

        # Reset counters
        pulse_count = 0
        start_time = current_time
        i = i + 1
        time.sleep(5)  # Update every 5 seconds
    pulses_per_second = round(pulses_per_second, 2)
    return "pulses per second: " + str(pulses_per_second), str(pulses_per_second)

        
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
    
def labModeViewer(folderPath, today, cameraFlip, filePrefix, pimoroni):
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
            print("Taking reading, this may take a moment...")
            timestamp = datetime.now().strftime("%H_%M_%S")
            reading = ""
            moisture = ""
            if(pimoroni):
                reading, moisture = getSoilMoisturePimoroni(4)
            else:
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
    cameraFlip, cameraCount, filePrefix, rollingAverage, numReadings, pimoroni = readConfig()
    
    today, timestamp, folderPath, fileName = setupFolderAndFile(labMode, filePrefix)
    
    if(pimoroni):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.IN)
        GPIO.add_event_detect(4, GPIO.RISING, callback=count_pulse)

    if(labMode):
        labModeViewer(folderPath, today, cameraFlip, filePrefix, pimoroni)
    else:
        if(pimoroni):
            reading, moisture = getSoilMoisturePimoroni(4)
        elif(rollingAverage):
            reading, moisture = getSoilSensorReadingRollingAverage(numReadings)
        else:
            reading, moisture = getSoilSensorReading()
        print(reading)
        fileName = fileName + "_" + moisture + ".jpg"
        takePictureAndSave(folderPath, fileName, cameraFlip)
        writeToLog(filePrefix + " " + today + " " + timestamp, reading, folderPath, 0)
        
if __name__ == "__main__":
   main(sys.argv[1:])



