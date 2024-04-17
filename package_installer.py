import subprocess
import datetime
import sys

python_path = sys.executable

# Loading config
config_file_path = r'C:\Users\sunilswain\Programming\Python\ANPRWeb\Config.txt'
with open(config_file_path, 'r') as file:
    file_contents = file.read()

paths=[i[i.find("=")+1:] for i in file_contents.split('\n') if i!="" and  not i.startswith("#")]
(DRIVER,SERVER,DATABASE,USERNAME, PASSWORD, DETECTOR_MODEL_PATH, RECOGNIZER_MODEL_DIR, REQUIREMENTS_PATH, LOG_FILE_PATH, STORAGE_PLATE_DIR) = paths

def installer():
    try:
        subprocess.check_call([python_path,"-m","pip", "install","requests"])
    except subprocess.CalledProcessError as e:
        with open(LOG_FILE_PATH, 'a') as log_file:
        # print(f"An Error has occurred please check {Audit_location}")
            log_file.write(f"\n\nAn unexpected error occurred:- {e} \n on datetime :- {datetime.now()}") 

    import requests


    # URL to download the Visual C++ Redistributable package
    download_url = "https://aka.ms/vs/16/release/vc_redist.x64.exe"

    # File path to save the downloaded installer
    installer_path = "vc_redist.x64.exe"

    def download_installer(url, filepath):
        print("Downloading Visual C++ Redistributable installer...")
        response = requests.get(url)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print("Download completed.")

    def install_installer(filepath):
        print("Installing Visual C++ Redistributable...")
        # Silent installation command
        command = f'{filepath} /quiet /norestart'
        # Execute the command silently in the background
        subprocess.run(command, shell=True)
        print("Installation completed.")

    def main():
        download_installer(download_url, installer_path)
        install_installer(installer_path)
        os.remove(installer_path)  # Remove the installer after installation

    main() ## Calling Visuall C++ installer
    try:
        subprocess.check_call([python_path,"-m","pip", "install","-r", REQUIREMENTS_PATH])
    except subprocess.CalledProcessError as e:
        with open(LOG_FILE_PATH, 'a') as log_file:
        # print(f"An Error has occurred please check {Audit_location}")
            log_file.write(f"\n\nAn unexpected error occurred:- {e} \n on datetime :- {datetime.now()}") 