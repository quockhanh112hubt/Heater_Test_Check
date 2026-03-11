import os
from datetime import datetime
import tkinter as tk
import time

def get_log_file_path():
    current_time = time.localtime()
    date_str = time.strftime('%Y%m%d', current_time)
    
    log_dir = os.path.join(os.getcwd(), 'logs', date_str)
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file_path = os.path.join(log_dir, f'log_{date_str}.txt')
    return log_file_path

def log_message(message):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    formatted_message = f"{current_time} - {message}"
    
    log_file_path = get_log_file_path()
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{formatted_message}\n")
