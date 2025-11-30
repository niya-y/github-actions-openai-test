import shutil
import os
import sys

source = r"C:\Users\MJ\.gemini\antigravity\brain\b78d8569-21eb-4dfd-a15a-9ee70e1de73a\uploaded_image_1_1764151543596.png"
dest1 = r"c:\dev\neulbomcare\frontend\my-app\public\assets\logo_color.png"
dest2 = r"c:\dev\neulbomcare\frontend\my-app\public\assets\logo_heart.png"

try:
    print(f"Copying to {dest1}")
    shutil.copy2(source, dest1)
    print("Success dest1")
    
    print(f"Copying to {dest2}")
    shutil.copy2(source, dest2)
    print("Success dest2")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
