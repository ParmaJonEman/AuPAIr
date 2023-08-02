# AuPAIr
Automated Precipitation Aware Irrigation

This is a long term research project, funded by a grant from the Taylor Geospatial Institute. The goal of this project is to create an automated system that can water plants in a greenhouse or outdoor garden only when watering is needed. The need for watering will be gauged using various sensors, weather APIs, and image processing techniques. 

### Phase 1

The first phase includes setting up a Raspberry Pi with soil moisture sensors and a camera. Every 30 minutes (or however often the user decides), the moistureSensor.py script will run, logging the current soil moisture and taking a picture of the plant to a remote Onedrive folder. This data will be used with a future plantCV script to determine the soil moisture level that indicates wilting in the near future.

To setup the script, simply install rclone via your package manager, setup a remote connection on rclone called "Onedrive", connect an Adafruit Soil Moisture Sensor to a Raspberry Pi using the default setup, connect any USB camera, and setup a CRON job to trigger the script every 30 minutes. Data is logged to the admin/var/<date> directory. If your username is not "admin", modify the script accordingly.

####Next Steps:
The capability for more soil sensors and cameras will be added to the moistureSensor.py script using an I2C multiplexer.
