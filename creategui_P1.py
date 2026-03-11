import tkinter as tk
from tkinter import font
from tkinter import ttk, messagebox
from tkinter import font as tkFont, Menu
from tkinter import scrolledtext
from log import log_message
from utils import show_image, show_image_narrow, show_image_mes
from PIL import Image, ImageTk
from datetime import datetime
from date import format_trans_time
from utils import get_current_version
from tkinter import Label
import cx_Oracle
import pyodbc
import pygame


def connect_to_database():
    conn = None
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=192.168.35.32,1433;'
            'DATABASE=ITMV_KTNG_DB;'
            'UID=ITMV_KTNG;'
            'PWD=!itm@semi!12;'
        )
    except pyodbc.Error as e:
        print(f"Error connecting to SQL Server database: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        return conn

def execute_query_afa(conn, heater_id):
    if conn:
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT ISNULL(MAX(A.TOTAL_JUDGMENT), 'SKIP') AS RESULT, 
                        MAX(A.WORK_TIME) AS WORK_TIME
                    FROM (
                        SELECT HEATER_ID, TOTAL_JUDGMENT, WORK_TIME, 
                            RANK() OVER (PARTITION BY HEATER_ID ORDER BY WORK_TIME DESC) AS RNK
                        FROM [ITMV_KTNG_DB].dbo.AFA_RESISTANCE_TEST_HISTORY
                        WHERE HEATER_ID = ?
                    ) A 
                    WHERE A.RNK = 1
                """
                cursor.execute(query, (heater_id,))
                product_codes = cursor.fetchone()
                return product_codes
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu: {e}")
            return None
    else:
        print("Không có kết nối đến cơ sở dữ liệu.")
        return None


def execute_query(heater_id):
    connection = cx_Oracle.connect(
        user="mighty",
        password="mighty",
        dsn="(DESCRIPTION=(LOAD_BALANCE=yes)(ADDRESS=(PROTOCOL=TCP)(HOST=192.168.35.20)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=192.168.35.20)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=ITMVPACKMES)(FAILOVER_MODE=(TYPE=SELECT)(METHOD=BASIC))))"
    )
    
    query = """
            SELECT NVL(MAX(A.TOTAL_JUDGMENT), 'SKIP') AS RESULT, 
                MAX(A.TRANS_TIME) AS TRANS_TIME
            FROM (
                SELECT HEATER_ID, TOTAL_JUDGMENT, TRANS_TIME, 
                    RANK() OVER (PARTITION BY HEATER_ID ORDER BY TRANS_TIME DESC) AS RNK
                FROM MIGHTY.ADC_RESISTANCE_TEST_HISTORY
                WHERE HEATER_ID = :HEATER_ID
            ) A 
            WHERE A.RNK = 1
    """
    try:
        cursor = connection.cursor()
        cursor.execute(query, heater_id=heater_id)
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except cx_Oracle.DatabaseError as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()
        connection.close()





def create_gui_P1(create_login_ui, create_gui_P230, create_gui_P4):
    def logout():
        root_P1.destroy()
        create_login_ui()

    def switch_to_P230():
        root_P1.destroy()
        create_gui_P230(create_login_ui, create_gui_P1, create_gui_P4)

    def switch_to_P4():
        root_P1.destroy()
        create_gui_P4(create_login_ui, create_gui_P1, create_gui_P230)


    root_P1 = tk.Tk()
    icon_mesconnect = ttk.Label(root_P1, text="")
    icon_mesconnect.place(x=10, y=795, width=25, height=25)
    name_mesconnect = ttk.Label(root_P1, text="", anchor="w")
    name_mesconnect.place(x=40, y=795, width=200, height=25)
    Copyright = ttk.Label(root_P1, text="Powered by ITM Semiconductor Vietnam Company Limited - IT Team. Copyright © 2024 all rights reserved.", anchor="center")
    Copyright.pack(side="bottom", pady=10)

    menubar = tk.Menu(root_P1)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Chuyển sang ECIGA-P2 3.0", command=switch_to_P230)
    file_menu.add_command(label="Chuyển sang ECIGA-P4", command=switch_to_P4)
    file_menu.add_command(label="Thoát", command=logout)
    menubar.add_cascade(label="Menu", menu=file_menu)
    
    root_P1.config(menu=menubar)



    def display_result(result):
        result_label.config(image='', text='')
        result_label.update_idletasks()

        # Khởi tạo pygame mixer
        pygame.mixer.init()

        if result == 'PASS':
            img = Image.open(r'Resource\Ok.png')
            pygame.mixer.music.load(r'Resource\OK.mp3')
        else:
            img = Image.open(r'Resource\NG.png')
            pygame.mixer.music.load(r'Resource\NG.mp3')

        pygame.mixer.music.play()
        
        img = ImageTk.PhotoImage(img)
        result_label.config(image=img)
        result_label.image = img

    def check_heater_id(event=None):
        heater_id = entry.get()
        if not heater_id:
            return

        # Sử dụng kết nối SQL Server hoặc Oracle tùy thuộc vào nhu cầu
        conn = connect_to_database()
        result = execute_query_afa(conn, heater_id)

        # result = execute_query(heater_id)  # Nếu bạn muốn dùng Oracle

        result_time = format_trans_time(result[1])

        if result[0] == 'PASS':
            display_result(result[0])  # Hiển thị kết quả trả về từ SQL Server hoặc Oracle
            name.config(text=f"{heater_id}")
            log_message(f"Check HEATER_ID: {heater_id} in Model P1 result {result[0]} at {result_time}!.\n")
        else:

            if result[0] == 'FAIL':
                display_result('NG')
                name.config(text=f"{heater_id}")
                log_message(f"Check HEATER_ID: {heater_id} in Model P1 result {result[0]} at {result_time}!.\n")
                
            else:
                display_result('NG')
                name.config(text=f"{heater_id}")
                log_message(f"Check HEATER_ID: {heater_id} in Model P1 does not exist!.\n")
        
        entry.delete(0, tk.END)

    root_P1.title(f"P1 Heater ID Result Checker Version {get_current_version()}")
    root_P1.geometry("1065x800")
    # root.resizable(False, False)
    font_entry = font.Font(family="Helvetica", size=16, weight="bold")

    label = tk.Label(root_P1, text="Enter HEATER_ID:")
    label.pack(pady=10)

    entry = tk.Entry(root_P1, width=40, font=font_entry)
    entry.pack(pady=10)

    entry.bind('<Return>', check_heater_id)

    result_label = Label(root_P1)
    result_label.pack(pady=10)

    name = tk.Label(root_P1, text='HEATER_ID', font=("Arial Bold", 26))
    name.pack(pady=10)


    # ui = Ui_InextendChecker(root_P1)
    root_P1.mainloop()

