import streamlit as st
import requests
import base64
from PIL import Image
import io
import numpy as np
import cv2
from datetime import datetime

# API endpoint (replace with your actual API URL)
API_URL = "http://localhost:5000/api/extract_plates"

st.title("Automatic Number Plate Recognition (ANPR) System")

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def display_plate_info(plate_info):
    """Display plate information in a formatted way"""
    st.subheader("Number Plate Recognition Results")
    
    for i, plate in enumerate(plate_info):
        st.markdown(f"### Plate {i+1}")
        
        # Display plate image
        plate_img_data = base64.b64decode(plate['plate_image'].encode('latin-1'))
        plate_img = Image.open(io.BytesIO(plate_img_data))
        st.image(plate_img, caption="Detected Number Plate", width=300)
        
        # Display plate value
        st.markdown(f"**Plate Number:** {plate['plate_val']}")
        
        # Display status information
        if plate['plate_status']:
            status = plate['plate_status'] 
            st.success("✅ Registered Vehicle")
            st.markdown(f"**Employee ID:** {status.get('EmployeeID', 'N/A')}")
            st.markdown(f"**Employee Name:** {status.get('EmployeeName', 'N/A')}")
            st.markdown(f"**Vehicle Model:** {status.get('Model_Name', 'N/A')}")
        else:
            st.error("❌ Unregistered Vehicle")

def capture_and_process():
    """Main function to capture image and process it"""
    st.header("Capture Number Plate")
    
    # Image upload option
    uploaded_file = st.file_uploader("Upload an image of a vehicle", type=["jpg", "jpeg", "png"])
    
    # Or use camera input
    use_camera = st.checkbox("Use camera instead")
    
    img = None
    
    if use_camera:
        img_file = st.camera_input("Take a picture of a vehicle")
        if img_file:
            img = Image.open(img_file)
    elif uploaded_file:
        img = Image.open(uploaded_file)
    
    if img is not None:
        # Display the captured image
        st.image(img, caption="Captured Image", use_container_width=True)
        
        # Convert to base64 for API
        img_base64 = image_to_base64(img)
        
        # Call the ANPR API
        with st.spinner("Processing number plate..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"image": img_base64},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('plates'):
                        display_plate_info(result['plates'])
                    else:
                        st.warning("No number plates detected in the image.")
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the ANPR API: {str(e)}")
                st.info("Please ensure the ANPR API is running and accessible.")

# Run the main function
capture_and_process()

# Add some documentation
st.sidebar.title("About")
st.sidebar.info(
    """
    This application uses Automatic Number Plate Recognition (ANPR) technology to:
    - Detect vehicle number plates in images
    - Recognize the plate numbers
    - Check against a registered database
    - Display vehicle information if registered
    """
)

# Add a timestamp
st.sidebar.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")