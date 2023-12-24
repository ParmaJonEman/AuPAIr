import csv
import os
from plantcv import plantcv as pcv
import cv2

def segmentPlantsA(img, filename):
	# finds the plants based on a channel
    gray_img = pcv.rgb2gray_lab(rgb_img=img, channel="a")
    bin_img = pcv.threshold.binary(gray_img=gray_img, threshold=123, object_type='dark')
    bin_img = pcv.fill(bin_img=bin_img, size=200)

	# crops the image using partial crop
    rect_roi = pcv.roi.rectangle(img=img, x=222, y=0, w=1560, h=1070)
    bin_img = pcv.roi.filter(mask=bin_img, roi=rect_roi, roi_type='partial')
	
	# crops the image using cutto crop
    rect_roi = pcv.roi.rectangle(img=img, x=280, y=270, w=1500, h=760)
    bin_img = pcv.roi.filter(mask=bin_img, roi=rect_roi, roi_type='cutto')
	
	# defines a grid so that we can label plant 1 and 2
    grid_rois = pcv.roi.multi(img=img, coord=(600, 600), radius=200, spacing=(900, 0), nrows=1, ncols=2)
    labeled_mask, num = pcv.create_labels(mask=bin_img, rois=grid_rois, roi_type="partial")
	
	# analyzes size pheno measurements
    shape_image = pcv.analyze.size(img=img, labeled_mask=labeled_mask, n_labels=num)
    print(filename)
	
	# writes an image with the plant boundaries drawn
    cv2.imwrite(filename + "processed.jpg", shape_image)
	
	# have not tried this yet, this is for color analysis
    #pcv.analyze.color(rgb_img=img, labeled_mask=labeled_mask, n_labels=num, colorspaces='hsv')

if __name__ == '__main__':
    parentDirectory = 'all'
	plant1OutputFile = 'output1.txt'
	plant2OutputFile = 'output2.txt'
	
	# iterates through all date folders in the 'all' directory
    for experimentDate in os.listdir(parentDirectory):
        print(experimentDate)
        directory = parentDirectory + "/" + experimentDate
        images = []
        filenames = []
        experimentList = []
        timeList = []
        tempList = []
        moistureList = []
        moistureList2 = []
        tempList2 = []

        # lists to hold pheno values for plant1
        inBoundsList = []
        areaList = []
        convexHullAreaList = []
        solidityList = []
        perimeterList = []
        widthList = []
        heightList = []
        longestPathList = []
        centerOfMass1List = []
        centerOfMass2List = []
        convexHullVerticesList = []
        objectInFrameList = []
        ellipseCenter1List = []
        ellipseCenter2List = []
        ellipseMajorAxisList = []
        ellipseMinorAxisList = []
        ellipseAngleList = []
        ellipseEccentricityList = []

        # lists to hold pheno values for plant2
        inBoundsList2 = []
        areaList2 = []
        convexHullAreaList2 = []
        solidityList2 = []
        perimeterList2 = []
        widthList2 = []
        heightList2 = []
        longestPathList2 = []
        centerOfMass1List2 = []
        centerOfMass2List2 = []
        convexHullVerticesList2 = []
        objectInFrameList2 = []
        ellipseCenter1List2 = []
        ellipseCenter2List2 = []
        ellipseMajorAxisList2 = []
        ellipseMinorAxisList2 = []
        ellipseAngleList2 = []
        ellipseEccentricityList2 = []
		
		# goes through each date directory, looking for images
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if os.path.isfile(f):
                if(".jpg" in filename):
                    x = filename.split("_")
                    time = filename.replace(x[-1], "")
                    time = time[:-1]
                    #print(time)
                    time1 = time[-8:]
                    time2 = time[20:].replace("_", ":")
                    print(time1)
                    print(time2)
					# if the images timestamp is in the log, add it to the list of files to analyze
                    if(time1 in timeList or time2 in timeList):
                        images.append(f)
                        filenames.append(filename)
                        print(filename)
				# when it finds the log file, it extracts experiment names, times, temps, and moistures
                if(".txt" in filename):
                    with open(f, 'r') as f:
                        reader = csv.reader(f, delimiter='\t')
                        for row in reader:
                            experimentList.append(row[0])
                            timeList.append(row[2])
                            tempList.append(row[3])
                            moistureList.append(row[4])
		# opens and analyzes all images
        for i in range(0, len(images)):
            img, path, filename = pcv.readimage(images[i])
            processedDirectory = "allProcessed/" + experimentDate
            if(not os.path.exists("allProcessed")):
                os.mkdir("allProcessed")
            if(not os.path.exists(processedDirectory)):
                os.mkdir(processedDirectory)
            processedPath = processedDirectory + "\\" + filenames[i].split('.')[0]
            segmentPlantsA(img, processedPath)
			
			
			# adds all plant1 values to the plant1 arrays
            inBoundsList.append(pcv.outputs.observations['default1']['in_bounds']['value'])
            areaList.append(pcv.outputs.observations['default1']['area']['value'])
            convexHullAreaList.append(pcv.outputs.observations['default1']['convex_hull_area']['value'])
            solidityList.append(pcv.outputs.observations['default1']['solidity']['value'])
            perimeterList.append(pcv.outputs.observations['default1']['perimeter']['value'])
            widthList.append(pcv.outputs.observations['default1']['width']['value'])
            heightList.append(pcv.outputs.observations['default1']['height']['value'])
            longestPathList.append(pcv.outputs.observations['default1']['longest_path']['value'])
            centerOfMass1List.append(pcv.outputs.observations['default1']['center_of_mass']['value'][0])
            centerOfMass2List.append(pcv.outputs.observations['default1']['center_of_mass']['value'][1])
            convexHullVerticesList.append(pcv.outputs.observations['default1']['convex_hull_vertices']['value'])
            objectInFrameList.append(pcv.outputs.observations['default1']['object_in_frame']['value'])
            ellipseCenter1List.append(pcv.outputs.observations['default1']['ellipse_center']['value'][0])
            ellipseCenter2List.append(pcv.outputs.observations['default1']['ellipse_center']['value'][0])
            ellipseMajorAxisList.append(pcv.outputs.observations['default1']['ellipse_major_axis']['value'])
            ellipseMinorAxisList.append(pcv.outputs.observations['default1']['ellipse_minor_axis']['value'])
            ellipseAngleList.append(pcv.outputs.observations['default1']['ellipse_angle']['value'])
            ellipseEccentricityList.append(pcv.outputs.observations['default1']['ellipse_eccentricity']['value'])

			# adds all plant2 values to the plant2 arrays, note: temp and moisture are 0 because theres no sensor in that pot
            tempList2.append('0')
            moistureList2.append('0')
            inBoundsList2.append(pcv.outputs.observations['default2']['in_bounds']['value'])
            areaList2.append(pcv.outputs.observations['default2']['area']['value'])
            convexHullAreaList2.append(pcv.outputs.observations['default2']['convex_hull_area']['value'])
            solidityList2.append(pcv.outputs.observations['default2']['solidity']['value'])
            perimeterList2.append(pcv.outputs.observations['default2']['perimeter']['value'])
            widthList2.append(pcv.outputs.observations['default2']['width']['value'])
            heightList2.append(pcv.outputs.observations['default2']['height']['value'])
            longestPathList2.append(pcv.outputs.observations['default2']['longest_path']['value'])
            centerOfMass1List2.append(pcv.outputs.observations['default2']['center_of_mass']['value'][0])
            centerOfMass2List2.append(pcv.outputs.observations['default2']['center_of_mass']['value'][1])
            convexHullVerticesList2.append(pcv.outputs.observations['default2']['convex_hull_vertices']['value'])
            objectInFrameList2.append(pcv.outputs.observations['default2']['object_in_frame']['value'])
            ellipseCenter1List2.append(pcv.outputs.observations['default2']['ellipse_center']['value'][0])
            ellipseCenter2List2.append(pcv.outputs.observations['default2']['ellipse_center']['value'][0])
            ellipseMajorAxisList2.append(pcv.outputs.observations['default2']['ellipse_major_axis']['value'])
            ellipseMinorAxisList2.append(pcv.outputs.observations['default2']['ellipse_minor_axis']['value'])
            ellipseAngleList2.append(pcv.outputs.observations['default2']['ellipse_angle']['value'])
            ellipseEccentricityList2.append(pcv.outputs.observations['default2']['ellipse_eccentricity']['value'])
            pcv.outputs.clear()

		# writes plant1 values to file
        with open(plant1OutputFile, 'a') as f:
            for i in range(0, len(images)):
                f.write(str(experimentList[i]) + "\t" +
                        str(experimentDate) + "\t" +
                        str(timeList[i]) + "\t" +
                        str(tempList[i]) + "\t" +
                        str(moistureList[i]) + "\t" +
                        str(inBoundsList[i]) + "\t" +
                        str(areaList[i]) + "\t" +
                        str(convexHullAreaList[i]) + "\t" +
                        str(solidityList[i]) + "\t" +
                        str(perimeterList[i]) + "\t" +
                        str(widthList[i]) + "\t" +
                        str(heightList[i]) + "\t" +
                        str(longestPathList[i]) + "\t" +
                        str(centerOfMass1List[i]) + "\t" +
                        str(centerOfMass2List[i]) + "\t" +
                        str(convexHullAreaList[i]) + "\t" +
                        str(objectInFrameList[i]) + "\t" +
                        str(ellipseCenter1List[i]) + "\t" +
                        str(ellipseCenter2List[i]) + "\t" +
                        str(ellipseMajorAxisList[i]) + "\t" +
                        str(ellipseMinorAxisList[i]) + "\t" +
                        str(ellipseAngleList[i]) + "\t" +
                        str(ellipseEccentricityList[i]) + "\n")
						
		# writes plant2 values to file
        with open(plant2OutputFile, 'a') as f:
            for i in range(0, len(images)):
                f.write(str(experimentList[i]) + "\t" +
                        str(experimentDate) + "\t" +
                        str(timeList[i]) + "\t" +
                        str(tempList2[i]) + "\t" +
                        str(moistureList2[i]) + "\t" +
                        str(inBoundsList2[i]) + "\t" +
                        str(areaList2[i]) + "\t" +
                        str(convexHullAreaList2[i]) + "\t" +
                        str(solidityList2[i]) + "\t" +
                        str(perimeterList2[i]) + "\t" +
                        str(widthList2[i]) + "\t" +
                        str(heightList2[i]) + "\t" +
                        str(longestPathList2[i]) + "\t" +
                        str(centerOfMass1List2[i]) + "\t" +
                        str(centerOfMass2List2[i]) + "\t" +
                        str(convexHullAreaList2[i]) + "\t" +
                        str(objectInFrameList2[i]) + "\t" +
                        str(ellipseCenter1List2[i]) + "\t" +
                        str(ellipseCenter2List2[i]) + "\t" +
                        str(ellipseMajorAxisList2[i]) + "\t" +
                        str(ellipseMinorAxisList2[i]) + "\t" +
                        str(ellipseAngleList2[i]) + "\t" +
                        str(ellipseEccentricityList2[i]) + "\n")