# AuPAIr
Automated Precipitation Aware Irrigation

This is a long term research project, funded by a grant from the Taylor Geospatial Institute. The goal of this project is to create an automated system that can water plants in a greenhouse or outdoor garden only when watering is needed. The need for watering will be gauged using various sensors, weather APIs, and image processing techniques. 

### Phase 1

The first phase includes setting up a Raspberry Pi with soil moisture sensors and a camera. Every 5 minutes (or however often the user decides), the moisture.py script will run, logging the current soil moisture and taking a picture of the plant to a remote Onedrive folder. This data will be used with a future plantCV script to determine the soil moisture level that indicates wilting in the near future.

Currently, the Adafruit I2C Soil Moisture Sensors and the Sparkfun Resistive Soil Moisture Sensors are supported. The Adafruit sensors can be connected directly to the Pi, if using only one, or to an I2C multiplexer if using multiple. The Sparkfun sensors are connected to the Pi via an Arduino Uno board.

A webcam must also be connected to the Raspberry Pi via USB.

Further hardware connection details pending.

To setup the script, simply install rclone via your package manager, setup a remote connection on rclone called "Onedrive", and setup a CRON job to trigger the script every 5 minutes. Data is logged to the admin/var/<date> directory. If your username is not "admin", modify the script accordingly.

The config.ini file contains several configurable settings for the script.

[DEFAULT]

Sparkfun // true or false, depending on if you are using Sparkfun sensors or not

numSensors // number of sensors you have connected to your Raspberry Pi

[watering] // the watering dates associated with each sensor

1

2

3

...

[cameras]

count // the number of cameras connected, currently only 1 is supported, but more are to be supported in the future

flip // true or false based on if your camera is mounted upside down or not

[files]

prefix // file prefix value, generally the name of the experiment being conducted

### Phase 2

The images produced by the Phase 1 script are to be processed by PlantCV, which produces many phenotype metrics. 

#### analyze.py
This script looks for a folder named "all" that contains subfolders, each named after their respective dates. Inside the date folders should be the images produced by moisture.py.
Each image is processed by PlantCV, and the shape metrics that PlantCV produces are output into a CSV, as well as the images with the plant outlines drawn on them. The script will have to be changed according to how many plants you're capturing at once, and where they're located in the images. It is not likely to work right out of the box.

#### cleanup.py
This scripts takes in a CSV and filters out the outlier data. Pictures taken at night, for instance, will not be as accurate as pictures taken during the day with sufficient lighting. Currently, it simply thresholds the data by removing any record that has an area outside of 20% of the 90th percentile of area for each day.
#### Next Steps:
Correlations between the data points will be anaylzed to determine predictor variables for wilting.
