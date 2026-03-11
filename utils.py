import os
import shutil
import datetime
from PIL import Image, ImageTk
import itertools
import time
import sys

CURRENT_VERSION_FILE = "C:\\Heater_Test_Check\\version.txt"

is_animating = False

def get_current_version():
    if os.path.exists(CURRENT_VERSION_FILE):
        with open(CURRENT_VERSION_FILE, "r") as file:
            return file.read().strip()
    return "0.0.0"

def show_image(label, image_path):
    global is_animating
    is_animating = False 
    img = Image.open(image_path)
    img = img.resize((60, 60), Image.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    label.config(image=photo)
    label.image = photo

def show_image_narrow(label, image_path):
    global is_animating
    is_animating = False 
    img = Image.open(image_path)
    img = img.resize((30, 30), Image.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    label.config(image=photo)
    label.image = photo

def show_image_mes(label, image_path):
    global is_animating
    is_animating = False 
    img = Image.open(image_path)
    img = img.resize((20, 20), Image.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    label.config(image=photo)
    label.image = photo

def show_image1(label, image_path):
    global is_animating
    is_animating = True  
    img = Image.open(image_path)
    frames = []
    try:
        while True:
            frames.append(ImageTk.PhotoImage(img.copy().resize((200, 200), Image.LANCZOS)))
            img.seek(len(frames))  # Tìm đến frame tiếp theo
    except EOFError:
        pass

    def update_frame(frame_index):
        if not is_animating:  
            return
        frame = frames[frame_index]
        label.config(image=frame)
        label.image = frame
        frame_index = (frame_index + 1) % len(frames)
        label.after(100, update_frame, frame_index)  
    update_frame(0)