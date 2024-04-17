import requests

# Set the API endpoint URL
api_url = "http://127.0.0.1:5000/api/extract_plates"

# Set the path to the image you want to rotate
image_path = r"C:\Users\sunilswain\Downloads\vehcle14.jpg"

# Open and read the image file as bytes
with open(image_path, "rb") as file:
    image_bytes = file.read()

# Create a dictionary with the image file for the POST request
files = {'image': (image_path, image_bytes)}

# Make the API request
response = requests.post(api_url, files=files)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Get the rotated image bytes from the response
    rotated_image_bytes = response.json()['plates'][0]['plate_image']
    
    # Save or process the rotated image as needed
    with open("cropped.jpg", "wb") as rotated_file:
        rotated_file.write(rotated_image_bytes.encode('latin-1'))
    print("Rotated image saved successfully.")
else:
    # Print the error message if the request was not successful
    print("Error:", response.json()['error'])
