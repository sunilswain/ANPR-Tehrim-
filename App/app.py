from flask import Flask, request, jsonify
from PIL import Image
from io import BytesIO
from utils import extractNumberPlates, isExists, recogFunc, getPaddle, getModel, getDataFrame
import numpy as np
import cv2
from flask_cors import CORS
from ngrok import werkzeug_develop, Listener, forward
import base64 
import os

# Define your tunnel configuration
tunnel_config = {
    "addr": "192.168.7.86:5000",
    "hostname": "valued-lynx-climbing.ngrok-free.app"
}
listener = forward(
    # session configuration
    addr=tunnel_config['addr'],
    authtoken_from_env=True,
    domain=tunnel_config['hostname'],
)
# Initializing important entities for optimisation
df = getDataFrame()

paddle = getPaddle()

# listener = werkzeug_develop() # Required for ngrok



app = Flask(__name__)

CORS(app, origins='*') # Required for CORS

print(listener.url())
@app.route('/api/extract_plates', methods=['POST'])
def extract_number_plates():
    # Get the image from the request
    print('-'*16)
    imgString = request.json['image']
    print(imgString[:55])

    # Decode the base64 string
    image_data = base64.b64decode(imgString)

    # This line converts image bytes into numpy array
    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), 1)
    print(image.shape)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # extracting the number plates
    plates = extractNumberPlates(image)

    plate_info = []
    for plate in plates:
        plate_val = recogFunc(plate, paddle)[0]
        plate_stat = isExists(plate_val, df)
        if plate_stat: plate_stat = plate_stat[0]
        _, encoded_image = cv2.imencode(".png", plate)
        # Add plate information to the list
        plate_info.append({
            'plate_image': base64.b64encode(encoded_image).decode('latin-1'),  # Convert NumPy array to bytes
            'plate_val': plate_val,
            'plate_status': plate_stat
        })

    # Return the list of plate information as response
    return jsonify({'plates': plate_info})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

