from ultralytics import YOLO
import cv2
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR
import numpy as np
from sqlalchemy import create_engine, URL, text
import pandas as pd
import time

# Loading config
config_file_path = r'C:\Users\sunilswain\Programming\Python\ANPRWeb\Config.txt'
with open(config_file_path, 'r') as file:
    file_contents = file.read()

paths=[i[i.find("=")+1:] for i in file_contents.split('\n') if i!="" and  not i.startswith("#")]
(DRIVER,SERVER,DATABASE,USERNAME, PASSWORD, DETECTOR_MODEL_PATH, RECOGNIZER_MODEL_DIR, REQUIREMENTS_PATH, LOG_FILE_PATH, STORAGE_PLATE_DIR) = paths
print(f"{DRIVER}, {USERNAME}")

def saveImg(image):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    
    cv2.imwrite(STORAGE_PLATE_DIR+'/'+timestr+'.jpg', image)

def getEngine():
    """Returns a database engine"""

    connection_string = f"Driver={DRIVER};Server={SERVER};Database={DATABASE};uid={USERNAME};pwd={PASSWORD}"

    connection_url = URL.create('mssql+pyodbc', query={"odbc_connect":connection_string})

    engine = create_engine(connection_url)

    return engine

ENGINE = getEngine()

def insertStatus(status):
    """Inserts status into the audi table"""
    INSERT_STRING = text("INSERT INTO ANPR_Transaction(anpr_status) VALUES(:status)")
    values = {'status': status}
    # print(status)
    with ENGINE.connect() as conn:
        
        conn.execute(INSERT_STRING, values)

        conn.commit()


def getDataFrame():
    """Returns Dataframe of Emplyee-Vehicle Information"""
    QUERY_STRING = """SELECT e.EmployeeID, e.EmployeeName, v.Vehicle_Number, v.Model_Name
FROM Employees e JOIN Vehicle_Information v
ON e.EmployeeID = v.EmployeeID"""

#     QUERY_STRING = """SELECT e.Emp_Id, e.Owner_Name, v.Vehicle_Number, v.Model_Name
# FROM Employees e JOIN Vehicle_Information v
# ON e.Emp_Id = v.EmployeeID"""

    
    df = pd.read_sql_query(QUERY_STRING, ENGINE)

    return df

def isExists(plate_val, df):
    """Returns the number plate table as dataframe"""
    plates = list(df['Vehicle_Number'])

    if plate_val in plates:
        insertStatus(f'DETECTED {plate_val}')
        return df.loc[df['Vehicle_Number']==plate_val
][['EmployeeID', 'EmployeeName', 'Model_Name']].to_dict(orient='records')
#         return df.loc[df['Vehicle_Number']==plate_val
# ][['Emp_Id', 'Owner_Name', 'Model_Name']].to_dict(orient='records')
    else:
        insertStatus(f'{plate_val} IS NOT REGISTERED')

    return False

def getPaddle():
    """Returns our CNN OCR Model"""
    ocr = PaddleOCR(use_angle_cls=True, lang='en', rec_model_dir=RECOGNIZER_MODEL_DIR)
    return ocr

def getModel():
    """Returns our Object Detetion Model"""
    model = YOLO(DETECTOR_MODEL_PATH)
    return model


# Function to extract number plate images
def extractNumberPlates(frame):
    """Returns cropped pictures of number plates if present"""
    model = getModel()

    if frame.shape[2] > 3:
        frame = frame[:, :, :3]

    result = model.predict(frame)[0]
    numPlates = []
    for object in result.boxes:
        x_min, y_min, x_max, y_max = [round(i) for i in object.xyxy[0].tolist()]
        conf = round(object.conf[0].item(), 2)
        print(x_min, y_min, x_max, y_max)
        print(conf)
        if conf > 0.70:
            numPlates.append(
                frame[y_min: y_max, x_min: x_max]
            )
    return numPlates

# Function to extract number plate images
# def extractNumberPlates(frame):
    """Returns cropped pictures of number plates if present"""
    model = getModel()

    if frame.shape[2] > 3:
        frame = frame[:, :, :3]

    results = model.predict(frame)[0]
    numPlates = []
    for object in results:
        segmented_coords = np.array(object.masks.xy, dtype=np.int32)
        # Create a mask from segmented coordinates
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [segmented_coords], (255, 255, 255))

        # Extract the segmented part of the image using the mask
        segmented_image = cv2.bitwise_and(frame, frame, mask=mask)

        # Find the bounding box of the segmented area
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        x, y, w, h = cv2.boundingRect(contours[0])

        # Crop the segmented part of the image using the bounding box
        cropped_image = segmented_image[y:y+h, x:x+w]

        numPlates += [cropped_image]
    return numPlates

# # Recognize the characters inside number plate
# def recogFunc(img, paddle):
#     """Predicts the number plate value"""
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     # _, otsu_thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#     # img_binary_lp_er = cv2.erode(otsu_thresh, (3,3))
#     # img_binary_lp = cv2.dilate(img_binary_lp_er, (3,3))  
#     result = paddle.ocr(gray, cls=True)
#     print(result)
#     plate_val = ""
    
#     if result != [None]:
#         for rec in result[0]:
#             if len(rec[1][0]) > 3:
#                 plate_val += rec[1][0]

#     if len(plate_val) > 0:
#         if plate_val[0] == '0':
#             plate_val = 'O'+plate_val[1:]
#         if plate_val[1] == '0':
#             plate_val = plate_val[:1]+'D'+plate_val[2:]
#         if plate_val[2] == 'O':
#             plate_val = plate_val[:2]+'0'+plate_val[3:]
#     return plate_val, result

def recogFunc(img, paddle):
    """Predicts the number plate value"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # _, otsu_thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # img_binary_lp_er = cv2.erode(otsu_thresh, (3,3))
    # img_binary_lp = cv2.dilate(img_binary_lp_er, (3,3))  
    results = paddle.ocr(gray, cls=True)[0]
    img_height, img_width = img.shape

    print(result)
    plate_val = ""
    
    if results != None:
        for result in results:
            cords = np.array(result[0], dtype=np.int32)
            value = result[1][0]

            det_area = round(cv2.contourArea(cords) / (img_height * img_width) * 100, 1)
            # If detection area is greater than 10% of the total image then include it into the plate value
            if det_area > 10:
                plate_val += value

    if len(plate_val) > 0:
        if plate_val[0] == '0':
            plate_val = 'O'+plate_val[1:]
        if plate_val[1] == '0':
            plate_val = plate_val[:1]+'D'+plate_val[2:]
        if plate_val[2] == 'O':
            plate_val = plate_val[:2]+'0'+plate_val[3:]
    return plate_val, result