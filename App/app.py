from flask import Flask, request, jsonify
from PIL import Image
from io import BytesIO
from utils import extractNumberPlates, isExists, recogFunc
import numpy as np
import cv2


app = Flask(__name__)

@app.route('/api/extract_plates', methods=['POST'])
def extract_number_plates():
    # Get the image from the request
    image = request.files['image'].read()
    image = np.array(Image.open(BytesIO(image)))
    print(image.shape)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    print(type(image))
    # extracting the number plates
    plates = extractNumberPlates(image)

    plate_info = []
    for plate in plates:
        plate_val = recogFunc(plate)[0]
        plate_stat = isExists(plate_val)
        _, encoded_image = cv2.imencode(".png", plate)
        # Add plate information to the list
        plate_info.append({
            'plate_image': encoded_image.tobytes().decode('latin-1'),  # Convert NumPy array to bytes
            'plate_val': plate_val,
            'plate_status': plate_stat
        })

    # Return the list of plate information as response
    return jsonify({'plates': plate_info})

if __name__ == '__main__':
    app.run(debug=True)
