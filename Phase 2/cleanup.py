import numpy as np
import pandas as pd

if __name__ == '__main__':
    file_path = 'Two Plant Experiment Data - plant1.csv'
    data = pd.read_csv(file_path)
    data_cleaned = pd.Series()
    days = data.iloc[:, 1].unique()
    for day in days:
        print(day)
        listOfAreas = data[data.iloc[:,1] == day].iloc[:, 6]
        percentileValue = np.percentile(listOfAreas, 90)
        print(percentileValue)
        day_cleaned = data[data.iloc[:,1] == day]
        day_cleaned = day_cleaned[day_cleaned.iloc[:, 6] > (percentileValue*.8)]
        day_cleaned = day_cleaned[day_cleaned.iloc[:, 6] < (percentileValue*1.2)]
        day_cleaned = day_cleaned[day_cleaned.iloc[:, 3] != 0]
        data_cleaned = data_cleaned.combine_first(day_cleaned)
    print(data_cleaned)
    data_cleaned.to_csv('allclean.csv')