import board
import adafruit_tca9548a
import cv2
import os
import time
import sys, getopt
import smtplib, ssl
from datetime import date
from datetime import datetime
from adafruit_seesaw.seesaw import Seesaw
import configparser
import shutil
import socket
import serial

logFileName = ""
attempts = 0

def readConfig():
    global logFileName
    hostname = os.popen("hostname").read()
    hostname = hostname.replace("\n", "")
    config = configparser.ConfigParser()
    config.read("config.ini")
    cameraFlip = False
    rollingAverage = False
    Sparkfun = False
    numReadings = 1
    if(config['cameras']['flip'] == 'true'):
        cameraFlip = True
    if(config['DEFAULT']['rollingAverage'] == 'true'):
        rollingAverage = True
        numReadings = int(config['DEFAULT']['numReadings'])
    numSensors = config['DEFAULT']['numSensors']
    if(config['DEFAULT']['Sparkfun'] == 'true'):
        Sparkfun = True
    cameraCount = config['cameras']['count']
    filePrefix = hostname + "_" + config['files']['prefix']
    for n in range(int(numSensors)):
        filePrefix = filePrefix + "_w" + config['watering'][str(n + 1)]
    print("file prefix is: " + filePrefix)
    logFileName = hostname + ".txt"
    return cameraFlip, cameraCount, filePrefix, rollingAverage, numReadings, Sparkfun, numSensors

def setWaterDate(plantNumber):
    config = configparser.ConfigParser()
    config.read("config.ini")
    today = date.today().strftime("%m%d%Y")
    config['watering'][str(plantNumber)] = today
    with open('config.ini', 'w') as configfile:    # save
        config.write(configfile)

def setupFolderAndFile(labMode, filePrefix):
    if(labMode == 1):
        print("Lab Mode On")
        print("Press Spacebar to take a reading or ESC to quit")
    if(labMode == 1 or labMode == 2):
        baseDirectory = '/home/admin/Desktop/'
        if(not os.path.exists(baseDirectory + 'AuPAIr')):
            os.mkdir(baseDirectory + 'AuPAIr/')
    else:
        baseDirectory = '/home/admin/shared/'
        bashCommand = "rclone --vfs-cache-mode writes mount \"Onedrive\": /home/admin/shared &"
        try:
            print("deleting cache")
            deleteCacheCommand = "rm -rf /home/admin/.cache/rclone/vfs/Onedrive"
            os.system(deleteCacheCommand)
            time.sleep(5)
            os.system(bashCommand)
            #os.system(bashCommand)
            print("bash command done")
        except:
            print("deleting cache")
            deleteCacheCommand = "rm -rf /home/admin/.cache/rclone/vfs/Onedrive"
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
    if(not (labMode == 1 or labMode == 2)):
        if(os.path.exists("/home/admin/Desktop/AuPAIr")):
            print("labmode folder exists")
            if(os.path.exists("/home/admin/Desktop/AuPAIr/" + today)):
                print("todays labmode folder exists")
                shutil.copytree("/home/admin/Desktop/AuPAIr/" + today, folderPath, dirs_exist_ok = True)
    return today, timestamp, folderPath, fileName

def getSoilSensorReading():
    global attempts
    exception = ""
    if(attempts<3):
        try:
            i2c_bus = board.I2C() 
            ss = Seesaw(i2c_bus, addr=0x36)
            touch = ss.moisture_read()
            temp = ss.get_temp()
            return "temp: " + str(temp) + "  moisture: " + str(touch), str(touch), str(temp)
        except Exception as e:
            attempts = attempts + 1
            exception = str(e)
            time.sleep(1)
            return getSoilSensorReading()
    else:
        return "An error occurred taking a soil moisture reading: " + exception, exception, exception

def getSoilSensorReadingMultiplexer(index):
    global attempts
    exception = ""
    if(attempts<3):
        try:
            i2c = board.I2C()
            tca = adafruit_tca9548a.TCA9548A(i2c)
            ss = Seesaw(tca[index], addr=0x36)
            touch = ss.moisture_read()
            temp = ss.get_temp()
            attempts = 0
            return "sensor " + str(index + 1) + "- temp: " + str(temp) + "  moisture: " + str(touch) + "\n", str(touch), str(temp)
        except Exception as e:
            exception = str(e)
            attempts = attempts + 1
            return getSoilSensorReadingMultiplexer(index)
    else:
        return "An error occurred taking a soil moisture reading: " + str(exception), str(exception), str(exception)

def getSoilMoistureReadingSparkfun(index):
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=9600,
    )
    x = 0
    while True:
        x = x + 1
        ser.write(str(index + 1).encode())
        if ser.in_waiting:
            data = ser.readline().decode('utf-8').rstrip()
            #print(data)
            if(data!="0" or x > 5):
                ser.close()
                break
        time.sleep(1)
    return "sensor " + str(index + 1) + "- temp: 0" + "  moisture: " + str(data) + "\n", str(data), "0"

def takePictureAndSave(directory, file, cameraFlip):
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FPS, 30)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
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
    global attempts
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FPS, 30)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cv2.namedWindow("Live View", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Live View", 192, 108)
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
            reading, moisture, temp = getSoilSensorReading()
            attempts = 0
            print(reading)
            writeToLog(filePrefix + "\t" + today + "\t" + timestamp, "\t" + str(moisture) + "\t" + str(temp), folderPath, 1, "log")
            fileName = filePrefix + "_" + timestamp + "_" + moisture + ".jpg"
            takeLabModePicture(folderPath, fileName, frame)

def labModeMultiple(folderPath, today, filePrefix, index, Sparkfun):
    global logFileName
    logFileName = logFileName.replace(".txt", str(index + 1) + ".txt")
    logFileName = logFileName.replace(str(index), "")
    timestamp = datetime.now().strftime("%H_%M_%S")

    print("Please visually inspect plant " + str(index + 1) + " and enter the hardiness level from 1 to 3")
    print("1 is wilted")
    print("2 is middling")
    print("3 is hardy")
    hardiness = input(":")
    while(int(hardiness) > 3 or int(hardiness) < 1):
        hardiness = input("Please enter 1, 2, or 3: ")
    print("Hardiness level recorded as: " + hardiness)
    comment = input("Please describe the plant or leave a comment: ")
    manualMeasure1 = input("Please measure pot " + str(index + 1) + ": ")
    print("Manual moisture reading recorded as: " + manualMeasure1)
    if(Sparkfun):
        reading, moisture, temp = getSoilMoistureReadingSparkfun(index)
    else:
        reading, moisture, temp = getSoilSensorReadingMultiplexer(index)
    print("Actual Reading: " + moisture)
    didYouWaterIt = input("Did you water it? y/n: ")
    if(didYouWaterIt == "y"):
        setWaterDate(index + 1)
    if(not os.path.isfile(folderPath + "/" + logFileName)):
        logFile = open(folderPath + "/" + logFileName, 'a+')
        logFile.write("prefix\tdate\ttimestamp\thardiness\tmanual measure\tmoisture reading\ttemp reading\tcomment\n")
        logFile.close()
    writeToLog(filePrefix + "\t" + today + "\t" + timestamp + "\t", hardiness + "\t" + manualMeasure1 + "\t" + moisture + "\t" + temp + "t" + comment, folderPath, 1, logFileName)
    return moisture

def sendEmail(error):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "greenhousehssu@gmail.com"  # Enter your address
    receiver_email = ["jefkn@umsystem.edu", "sanjiv@umsl.edu", "meyerre@hssu.edu", "meyerr@hssu.edu"]  # Enter receiver address
    password = "yigp kkwm lafm ulei"
    message = "From: " + sender_email + "\n"
    message = message + "Subject: An error occurred while trying to write to the log \n\n\n"
    message = message + "The error was: " + error

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    
def writeToLog(prefix, reading, folderPath, labMode, logName):
    try:
        print("writing to log")
        logFile = open(folderPath + "/" + logName, 'a+')
        logFile.write(prefix + reading + "\n")
        logFile.close()
    except Exception as e:
        with open('errors.txt', 'r+') as f:
            if str(e) in f.read():
                print("Error already logged")
                print(str(e))
            else:
                print(str(e))
                f.write(str(e) + '\n')
                sendEmail(str(e))
        print("deleting cache")
        deleteCacheCommand = "rm -r /home/admin/.cache/rclone/vfs/Onedrive"
        os.system(deleteCacheCommand)
        time.sleep(5)
    if(not labMode):
        bashCommand2 = "rclone --vfs-cache-mode writes mount \"Onedrive\": /home/admin/shared &"
        bashCommand = "fusermount -u /home/admin/shared"
        os.system(bashCommand)
        time.sleep(5)
        os.system(bashCommand2)
        time.sleep(15)
        os.system(bashCommand)
        
def parseArgs(argv):
    opts, args = getopt.getopt(argv,"hlm")
    for opt, arg in opts:
      if opt == '-h':
         print ('moist.py [-l]')
         sys.exit()
      elif opt in ("-l"):
          return 1
      elif opt in("-m"):
          return 2
    return 0

def isLogFileOld(folderPath):
    global logFileName
    try:
        bashCommandLastModified = "date -r " + folderPath + "/" + logFileName + " +%s"
        bashCommandRightNow = "date +%s"
        lastModified = os.popen(bashCommandLastModified).read()
        rightNow = os.popen(bashCommandRightNow).read()
        howOldIsTheLogFile = int(rightNow)-int(lastModified)
        print("The log file is: " + str(howOldIsTheLogFile) + " seconds old")
        if(howOldIsTheLogFile > 3600):
            e = "The log file has not been updated in an hour"
            with open('errors.txt', 'r+') as f:
                if str(e) in f.read():
                    print("Error already logged")
                else:
                    print(str(e))
                    f.write(str(e) + '\n')
                    sendEmail(str(e))
        
    except Exception as e:
        print(str(e))

def main(argv):
    global logFileName
    labMode = parseArgs(argv)
    cameraFlip, cameraCount, filePrefix, rollingAverage, numReadings, Sparkfun, numSensors = readConfig()
    today, timestamp, folderPath, fileName = setupFolderAndFile(labMode, filePrefix)

    if(labMode == 1):
        logFileName = "labmode_" + logFileName
        filePrefix = filePrefix + "_labmode"
        labModeViewer(folderPath, today, cameraFlip, filePrefix)
    elif(labMode == 2):
        logFileName = "labmode_" + logFileName
        filePrefix = filePrefix + "_labmode"
        print(r"""     __
  .-/  \-.
 (  \__/  )
/`-./;;\.-`\
\ _.\;;/._ /		Welcome to multi-sensor lab mode
 (  /  \  )
  '-\__/-'.-,
 ,    \\ (-. )
 |\_   ||/.-`
 \'.\_ |;`
  '--,\||     ,
      `;|   _/|
       // _/.'/
      //_/,--'
     ||'-`""")
        print("Your config file says you have " + numSensors + " sensors")
        isThisRight = input("Is this correct? y/n ")
        if(isThisRight == "n"):
            print("Fix the config.ini and try again")
        else:
            while True:
                moistureAll = ""
                for n in range(int(numSensors)):
                    moistureAll = moistureAll + "_" + labModeMultiple(folderPath, today, filePrefix, n, Sparkfun)
                moreReadings = input("Do you want to take another round of readings? y/n ")
                if moreReadings == 'n':
                    break
            takePicture = input("Do you want to take a picture? y/n ")
            if takePicture == 'y':
                fileName = fileName + "_labmode" + moistureAll + ".jpg"
                takePictureAndSave(folderPath, fileName, cameraFlip)

    else:
        isLogFileOld(folderPath)
        if(int(numSensors) > 1):
            moisture = ""
            reading = ""
            for n in range(int(numSensors)):
                if(Sparkfun):
                    print("Reading " + str(n + 1))
                    instanceReading, instanceMoisture, instanceTemp = getSoilMoistureReadingSparkfun(n)
                    print(instanceMoisture)
                else:
                    instanceReading, instanceMoisture, instanceTemp = getSoilSensorReadingMultiplexer(n)
                reading = reading + "\t" + instanceMoisture + "\t" + instanceTemp
                moisture = moisture + "_" + instanceMoisture
        else:
            reading, moisture, temp = getSoilSensorReading()
            reading = "\t" + moisture + "\t" + temp
        print(reading)
        fileName = fileName + "_" + moisture + ".jpg"
        takePictureAndSave(folderPath, fileName, cameraFlip)
        writeToLog(filePrefix + "\t" + today + "\t" + timestamp, reading, folderPath, 0, logFileName)
        
if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as e:
        with open('errors.txt', 'r+') as f:
            if str(e) in f.read():
                print("Error already logged")
                print(str(e))
            else:
                print(str(e))
                f.write(str(e) + '\n')
                sendEmail(str(e))




