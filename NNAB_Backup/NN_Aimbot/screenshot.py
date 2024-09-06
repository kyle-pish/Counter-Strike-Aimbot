# Custom script for taking screenshots to collect data

import os
import time
import pyautogui

def take_screenshot(folder):
    # Create the folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Set initial counter
    i = 1
    
    while True:
        if i < 10:
            # Capture screenshot
            screenshot = pyautogui.screenshot()
            
            # Save screenshot with a unique filename
            screenshot.save(os.path.join(folder, f"csdata_{i}.png"))
            print(f"Saved csdata_{i}.png to {folder}" )
            # Increment counter
            i += 1
            
            # Wait for 1 second
            time.sleep(0.5)
        
        else:
            print("All data collected!")
            break

# Define the folder where screenshots will be saved
folder_name = "/Users/kylepish/Desktop/NN_Aimbot/data_raw"

# Call the function to start taking screenshots
take_screenshot(folder_name)
