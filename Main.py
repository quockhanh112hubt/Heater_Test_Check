import urllib.request
import subprocess
import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
from tkinter import messagebox
from creategui_P230_new import create_gui_P230
from creategui_P4 import create_gui_P4
from creategui_P1 import create_gui_P1
from utils import get_current_version
from config_manager import load_config, save_config, get_update_config, get_ftp_base_url, get_version_url

# Load configuration from config.json
config = load_config()
update_config = get_update_config()

# Đường dẫn tới thư mục chứa các file chương trình
PROGRAM_DIRECTORY = update_config.get('program_directory', 'C:\\Heater_Test_Check')
UPDATE_SCRIPT_EXECUTABLE = os.path.join(PROGRAM_DIRECTORY, "update_script.exe")

# Đường dẫn tới FTP Server
FTP_BASE_URL = get_ftp_base_url()
VERSION_URL = get_version_url()


def login():
    selected_option = option_var.get()
    root.destroy()
    
    if selected_option == "ECIGA-P1 4.0":
        # create_gui_P1(create_login_ui, create_gui_P230, create_gui_P4)
        Plant_Comming_Soon()
    elif selected_option == "ECIGA-P2 3.0":
        create_gui_P230(create_login_ui, create_gui_P1, create_gui_P4)
    elif selected_option == "ECIGA-P4":
        # create_gui_P4(create_login_ui, create_gui_P1, create_gui_P230)
        Plant_Comming_Soon()
    elif selected_option == "ECIGA-P2 4.0(Coming Soon)":
        Plant_Comming_Soon()


def Plant_Comming_Soon():
    messagebox.showinfo("Thông báo", "Plant đang trong quá trình phát triển!")
    create_login_ui()

def get_latest_version():
    try:
        with urllib.request.urlopen(VERSION_URL) as response:
            latest_version = response.read().decode('utf-8').strip()
        return latest_version
    except Exception as e:
        print(f"Không thể lấy phiên bản mới nhất: {e}")
        return None

def check_for_updates():
    current_version = get_current_version()
    latest_version = get_latest_version()
    
    if latest_version and latest_version > current_version:
        initiate_update()

def initiate_update():
    print("Đang chuẩn bị cập nhật và khởi động lại chương trình...")
    process = subprocess.Popen([UPDATE_SCRIPT_EXECUTABLE])
    print(f"Đã khởi chạy {UPDATE_SCRIPT_EXECUTABLE}, PID: {process.pid}")
    sys.exit()

def cancel():
    root.destroy()
    sys.exit()


def open_settings():
    """Mở cửa sổ Settings"""
    settings_window = tk.Toplevel(root)
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "Resource", "ico.ico")
        settings_window.iconbitmap(icon_path)
    except Exception as e:
        print(f"Warning: Could not set window icon: {e}")
    settings_window.title("⚙️ Settings - Configuration")
    settings_window.geometry("700x650")
    settings_window.configure(bg='#f5f7fa')
    settings_window.resizable(False, False)
    settings_window.grab_set()  # Modal window
    
    # Load current config
    current_config = load_config()
    
    # Header
    header = tk.Frame(settings_window, bg='#1e3a8a', height=60)
    header.pack(fill='x')
    header.pack_propagate(False)
    
    tk.Label(
        header,
        text="⚙️ SETTINGS",
        font=("Segoe UI", 20, "bold"),
        bg='#1e3a8a',
        fg='white'
    ).pack(pady=15)
    
    # Main content with scrollbar
    main_frame = tk.Frame(settings_window, bg='#f5f7fa')
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Canvas for scrolling
    canvas = tk.Canvas(main_frame, bg='#f5f7fa', highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#f5f7fa')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # ===== UPDATE SETTINGS =====
    update_frame = tk.LabelFrame(
        scrollable_frame,
        text="🔄 Update Configuration",
        font=("Segoe UI", 11, "bold"),
        bg='white',
        fg='#1e3a8a',
        padx=15,
        pady=15
    )
    update_frame.pack(fill='x', pady=(0, 15))
    
    update_entries = {}
    update_fields = [
        ('program_directory', 'Program Directory:', current_config['update'].get('program_directory', 'C:\\Heater_Test_Check')),
        ('ftp_server', 'FTP Server IP:', current_config['update'].get('ftp_server', '192.168.110.12')),
        ('ftp_username', 'FTP Username:', current_config['update'].get('ftp_username', 'update')),
        ('ftp_password', 'FTP Password:', current_config['update'].get('ftp_password', 'update')),
        ('update_path', 'Update Path:', current_config['update'].get('update_path', '/KhanhDQ/Update_Program/Heater_Test_Check/'))
    ]
    
    for idx, (key, label, value) in enumerate(update_fields):
        tk.Label(update_frame, text=label, bg='white', font=("Segoe UI", 9)).grid(row=idx, column=0, sticky='w', pady=5)
        entry = tk.Entry(update_frame, font=("Segoe UI", 9), width=50, show='*' if key == 'ftp_password' else '')
        entry.insert(0, value)
        entry.grid(row=idx, column=1, pady=5, padx=10)
        update_entries[key] = entry
    
    # ===== SQL SERVER SETTINGS =====
    sql_frame = tk.LabelFrame(
        scrollable_frame,
        text="🗄️ SQL Server Configuration",
        font=("Segoe UI", 11, "bold"),
        bg='white',
        fg='#1e3a8a',
        padx=15,
        pady=15
    )
    sql_frame.pack(fill='x', pady=(0, 15))
    
    sql_entries = {}
    sql_fields = [
        ('driver', 'Driver:', current_config['database']['sql_server']['driver']),
        ('server', 'Server:', current_config['database']['sql_server']['server']),
        ('port', 'Port:', current_config['database']['sql_server']['port']),
        ('database', 'Database:', current_config['database']['sql_server']['database']),
        ('username', 'Username:', current_config['database']['sql_server']['username']),
        ('password', 'Password:', current_config['database']['sql_server']['password'])
    ]
    
    for idx, (key, label, value) in enumerate(sql_fields):
        tk.Label(sql_frame, text=label, bg='white', font=("Segoe UI", 9)).grid(row=idx, column=0, sticky='w', pady=5)
        entry = tk.Entry(sql_frame, font=("Segoe UI", 9), width=50, show='*' if key == 'password' else '')
        entry.insert(0, value)
        entry.grid(row=idx, column=1, pady=5, padx=10)
        sql_entries[key] = entry
    
    # ===== ORACLE SETTINGS =====
    oracle_frame = tk.LabelFrame(
        scrollable_frame,
        text="🗄️ Oracle Database Configuration",
        font=("Segoe UI", 11, "bold"),
        bg='white',
        fg='#1e3a8a',
        padx=15,
        pady=15
    )
    oracle_frame.pack(fill='x', pady=(0, 15))
    
    oracle_entries = {}
    oracle_fields = [
        ('host', 'Host:', current_config['database']['oracle']['host']),
        ('port', 'Port:', current_config['database']['oracle']['port']),
        ('service_name', 'Service Name:', current_config['database']['oracle']['service_name']),
        ('username', 'Username:', current_config['database']['oracle']['username']),
        ('password', 'Password:', current_config['database']['oracle']['password'])
    ]
    
    for idx, (key, label, value) in enumerate(oracle_fields):
        tk.Label(oracle_frame, text=label, bg='white', font=("Segoe UI", 9)).grid(row=idx, column=0, sticky='w', pady=5)
        entry = tk.Entry(oracle_frame, font=("Segoe UI", 9), width=50, show='*' if key == 'password' else '')
        entry.insert(0, value)
        entry.grid(row=idx, column=1, pady=5, padx=10)
        oracle_entries[key] = entry
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # ===== BUTTONS =====
    button_frame = tk.Frame(settings_window, bg='#f5f7fa')
    button_frame.pack(fill='x', padx=20, pady=(0, 20))
    
    def save_settings():
        """Save settings to config.json"""
        try:
            new_config = {
                "update": {
                    "program_directory": update_entries['program_directory'].get(),
                    "ftp_server": update_entries['ftp_server'].get(),
                    "ftp_username": update_entries['ftp_username'].get(),
                    "ftp_password": update_entries['ftp_password'].get(),
                    "update_path": update_entries['update_path'].get()
                },
                "database": {
                    "sql_server": {
                        "driver": sql_entries['driver'].get(),
                        "server": sql_entries['server'].get(),
                        "port": sql_entries['port'].get(),
                        "database": sql_entries['database'].get(),
                        "username": sql_entries['username'].get(),
                        "password": sql_entries['password'].get()
                    },
                    "oracle": {
                        "host": oracle_entries['host'].get(),
                        "port": oracle_entries['port'].get(),
                        "service_name": oracle_entries['service_name'].get(),
                        "username": oracle_entries['username'].get(),
                        "password": oracle_entries['password'].get()
                    }
                }
            }
            
            if save_config(new_config):
                messagebox.showinfo("Success", "✓ Settings saved successfully!\n\nPlease restart the application for changes to take effect.")
                settings_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to save settings!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")
    
    def reset_to_default():
        """Reset to default configuration"""
        from config_manager import DEFAULT_CONFIG
        if messagebox.askyesno("Confirm", "Are you sure you want to reset all settings to default?"):
            if save_config(DEFAULT_CONFIG):
                messagebox.showinfo("Success", "✓ Settings reset to default!\n\nPlease restart the application.")
                settings_window.destroy()
    
    tk.Button(
        button_frame,
        text="💾 Save Settings",
        command=save_settings,
        bg='#10b981',
        fg='white',
        font=("Segoe UI", 10, "bold"),
        relief='flat',
        padx=20,
        pady=10,
        cursor='hand2'
    ).pack(side='left', padx=5)
    
    tk.Button(
        button_frame,
        text="🔄 Reset to Default",
        command=reset_to_default,
        bg='#f59e0b',
        fg='white',
        font=("Segoe UI", 10, "bold"),
        relief='flat',
        padx=20,
        pady=10,
        cursor='hand2'
    ).pack(side='left', padx=5)
    
    tk.Button(
        button_frame,
        text="❌ Cancel",
        command=settings_window.destroy,
        bg='#6b7280',
        fg='white',
        font=("Segoe UI", 10, "bold"),
        relief='flat',
        padx=20,
        pady=10,
        cursor='hand2'
    ).pack(side='right', padx=5)


def create_login_ui():
    global root, option_var

    root = tk.Tk()
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "Resource", "ico.ico")
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Warning: Could not set window icon: {e}")
    root.title(f"Heater Test DCR Checker Version {get_current_version()}")
    root.geometry("660x600")
    root.configure(bg='#00a99d')
    root.resizable(False, False)

    # Tải ảnh nền
    background_image = Image.open("Resource/background.jpg")
    background_photo = ImageTk.PhotoImage(background_image)
    canvas = tk.Canvas(root, width=200, height=250)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Frame chính giữa
    frame = tk.Frame(root, bg='#003366', bd=0)
    frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=300)

    # Icon người dùng
    user_name = tk.Label(frame, bg='#003366', text="HEATER TEST DCR CHECKER", fg='#66CCFF', font=("Arial Black", 18))
    user_name.place(relx=0.5, y=25, anchor='center')
    user_icon = tk.Label(frame, bg='#003366', text="ITM Semiconductor Vietnam", fg='#66CCFF', font=("Cascadia Mono SemiBold", 9))
    user_icon.place(relx=0.5, y=50, anchor='center')

    # Tiêu đề đăng nhập
    title = tk.Label(frame, text="Select Production Model", fg='#66CCFF', bg='#003366', font=("Arial Black", 16))
    title.place(relx=0.5, y=100, anchor='center')

    # Tạo combobox cho các lựa chọn
    option_var = tk.StringVar()
    option_frame = tk.Frame(frame, bg='#e0f7fa', bd=1, relief='solid')
    option_frame.place(relx=0.5, y=150, anchor='center', width=300, height=40)
    combo = ttk.Combobox(option_frame, textvariable=option_var, font=("Arial", 12), state="readonly")
    combo['values'] = ("ECIGA-P1 4.0", "ECIGA-P2 3.0", "ECIGA-P4", "ECIGA-P2 4.0(Coming Soon)")
    combo.place(relx=0.5, rely=0.5, anchor='center', width=240, height=30)
    combo.current(1)

    # Nút đăng nhập
    login_button = tk.Button(frame, text="START", command=login, bg='#00796b', fg='#003366', font=("Arial", 14))
    login_button.place(relx=0.5, y=200, anchor='center', width=150, height=40)
    root.bind('<Return>', lambda event: login())
    
    # Nút Settings ở góc dưới bên phải
    settings_button = tk.Button(
        frame,
        text="⚙️ Settings",
        command=open_settings,
        bg='#4b5563',
        fg='white',
        font=("Arial", 9),
        relief='flat',
        cursor='hand2'
    )
    settings_button.place(relx=0.95, rely=0.95, anchor='se', width=100, height=30)

    root.mainloop()


if __name__ == "__main__":
    check_for_updates()
    create_login_ui()

