from ultralytics import YOLO
import cv2
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR
import numpy as np
from sqlalchemy import create_engine, URL
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv('App/os.env')

def isExists(plate_val):
    DRIVER = os.getenv('DRIVER')
    SERVER = os.getenv('SERVER')
    DATABASE = os.getenv('DATABASE')
    USERNAME = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    print(DRIVER, USERNAME)

    connection_string = f"Driver={DRIVER};Server={SERVER};Database={DATABASE};uid={USERNAME};pwd={PASSWORD}"

    connection_url = URL.create('mssql+pyodbc', query={"odbc_connect":connection_string})

    engine = create_engine(connection_url)
    df = pd.read_sql_table('PlateDetails', engine)

    plates = list(df['Vehicle_Number'])

    if plate_val in plates:
        return df.loc[df['Vehicle_Number']==plate_val
][['Emp_Id', 'Owner_Name']].to_dict(orient='records')

    return False

def getPaddle():
    """Returns our CNN OCR Model"""
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    return ocr

# Function to extract number plate images
def extractNumberPlates(frame):
    """Returns cropped pictures of number plates if present"""
    model = YOLO('App/best_1.pt')
    result = model.predict(frame)[0]
    numPlates = []
    for object in result.boxes:
        x_min, y_min, x_max, y_max = [round(i) for i in object.xyxy[0].tolist()]
        conf = conf = round(object.conf[0].item(), 2)
        print(x_min, y_min, x_max, y_max)
        print(conf)
        if conf > 0.70:
            numPlates.append(
                frame[y_min: y_max, x_min: x_max]
            )
    return numPlates

# Recognize the characters inside number plate
def recogFunc(img):
    """Predicts the number plate value"""
    paddle = getPaddle()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # _, otsu_thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # img_binary_lp_er = cv2.erode(otsu_thresh, (3,3))
    # img_binary_lp = cv2.dilate(img_binary_lp_er, (3,3))  
    result = paddle.ocr(gray, cls=True)
    print(result)
    plate_val = ""
    
    if result != [None]:
        for rec in result[0]:
            if len(rec[1][0]) > 3:
                plate_val += rec[1][0]

    # # Fixing some characters in the number plate
    # plate_val = fixNumberPlate(plate_val)
    if len(plate_val) > 0:
        if plate_val[0] == '0':
            plate_val = 'O'+plate_val[1:]
        if plate_val[1] == '0':
            plate_val = plate_val[:1]+'D'+plate_val[2:]
        if plate_val[2] == 'O':
            plate_val = plate_val[:2]+'0'+plate_val[3:]
    return plate_val, result
