import tkinter as tk
from tkinter import font, ttk, messagebox
# from log import log_message
from PIL import Image, ImageTk
import cx_Oracle
import pyodbc
from datetime import datetime
import threading
from config_manager import get_sql_connection_string, get_oracle_connection_params, load_config, save_config
import pygame


def connect_to_database():
    """Kết nối đến SQL Server database"""
    conn = None
    try:
        conn_string = get_sql_connection_string()
        conn = pyodbc.connect(conn_string)
    except pyodbc.Error as e:
        print(f"Error connecting to SQL Server database: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        return conn


def execute_query_afa(conn, heater_id):
    """Thực hiện query trên SQL Server"""
    if conn:
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT ISNULL(MAX(A.TOTAL_JUDGMENT), 'SKIP') AS RESULT, 
                        MAX(A.WORK_TIME) AS WORK_TIME
                    FROM (
                        SELECT HEATER_ID, TOTAL_JUDGMENT, WORK_TIME, 
                            RANK() OVER (PARTITION BY HEATER_ID ORDER BY WORK_TIME DESC) AS RNK
                        FROM [ITMV_KTNG_DB].dbo.AFA_P2HB3_RESISTANCE_TEST_HISTORY
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


def execute_query_oracle(heater_id):
    """Thực hiện query trên Oracle database"""
    try:
        oracle_params = get_oracle_connection_params()
        connection = cx_Oracle.connect(**oracle_params)
        
        query = """
            SELECT NVL(MAX(A.TOTAL_JUDGMENT), 'SKIP') AS RESULT, 
                MAX(A.TRANS_TIME) AS TRANS_TIME
            FROM (
                SELECT HEATER_ID, TOTAL_JUDGMENT, TRANS_TIME, 
                    RANK() OVER (PARTITION BY HEATER_ID ORDER BY TRANS_TIME DESC) AS RNK
                FROM MIGHTY.ADC_P3_RESISTANCE_TEST_HISTORY
                WHERE HEATER_ID = :HEATER_ID
            ) A 
            WHERE A.RNK = 1
        """
        
        cursor = connection.cursor()
        cursor.execute(query, heater_id=heater_id)
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if result:
            return result
        return None
    except cx_Oracle.DatabaseError as e:
        print(f"Database error: {e}")
        return None


class ModernCard(tk.Frame):
    """Widget Card hiện đại với shadow effect"""
    def __init__(self, parent, title="", bg_color="#ffffff", **kwargs):
        super().__init__(parent, bg="#f5f7fa", **kwargs)
        
        # Card container với padding
        self.card = tk.Frame(self, bg=bg_color, relief="flat", bd=0)
        self.card.pack(padx=5, pady=5, fill="both", expand=True)
        
        # Shadow effect simulation
        self.configure(bg="#d0d5dd")
        
        if title:
            title_frame = tk.Frame(self.card, bg=bg_color)
            title_frame.pack(fill="x", padx=20, pady=(15, 10))
            
            title_label = tk.Label(
                title_frame, 
                text=title, 
                font=("Segoe UI", 12, "bold"),
                bg=bg_color,
                fg="#1a1a1a"
            )
            title_label.pack(side="left")
    
    def get_content_frame(self):
        """Trả về frame để thêm nội dung"""
        content = tk.Frame(self.card, bg=self.card["bg"])
        content.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        return content


class StatusIndicator(tk.Canvas):
    """Indicator trạng thái với animation"""
    def __init__(self, parent, size=12, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        highlightthickness=0, bg=parent["bg"], **kwargs)
        self.size = size
        self.status = "unknown"
        self.draw_indicator()
    
    def draw_indicator(self):
        self.delete("all")
        colors = {
            "connected": "#10b981",
            "disconnected": "#ef4444",
            "checking": "#f59e0b"
        }
        color = colors.get(self.status, "#9ca3af")
        
        # Outer circle (glow effect)
        self.create_oval(1, 1, self.size-1, self.size-1, 
                        fill=color, outline=color, width=0)
        
        # Inner circle
        margin = 3
        self.create_oval(margin, margin, self.size-margin, self.size-margin,
                        fill=color, outline="white", width=1)
    
    def set_status(self, status):
        self.status = status
        self.draw_indicator()


def create_gui_P230(create_login_ui, create_gui_P1, create_gui_P4):
    
    # Variables - will be initialized after root window is created
    check_history = []
    total_checks = 0
    pass_count = 0
    fail_count = 0
    history_filter = "All"  # Filter for history display
    
    def logout():
        root_P230.destroy()
        create_login_ui()

    def switch_to_P1():
        # root_P230.destroy()
        # create_gui_P1(create_login_ui, create_gui_P230, create_gui_P4)
        messagebox.showinfo("Thông báo", "Plant P1 đang trong quá trình phát triển!")

    def switch_to_P4():
        # root_P230.destroy()
        # create_gui_P4(create_login_ui, create_gui_P1, create_gui_P230)
        messagebox.showinfo("Thông báo", "Plant P4 đang trong quá trình phát triển!")

    def log_to_gui(message):
        """Thêm log message vào GUI"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        log_text.see(tk.END)
        log_text.update_idletasks()

    def update_statistics():
        """Cập nhật thống kê"""
        pass_rate = (pass_count / total_checks * 100) if total_checks > 0 else 0
        
        stats_labels['total'].config(text=str(total_checks))
        stats_labels['pass'].config(text=str(pass_count))
        stats_labels['fail'].config(text=str(fail_count))
        stats_labels['rate'].config(text=f"{pass_rate:.1f}%")

    def display_result(result, work_time=None):
        """Hiển thị kết quả với layout mới"""
        nonlocal total_checks, pass_count, fail_count
        
        # Clear previous result
        result_label.config(image='', text='')
        
        # Normalize result (Oracle returns 'OK', SQL Server returns 'PASS')
        if result in ['OK', 'PASS']:
            result = 'PASS'
        
        # Update counts
        total_checks += 1
        if result == 'PASS':
            pass_count += 1
            img = ok_image
            status_color = "#10b981"
            status_text = "✓ PASSED"
            status_bg = "#d1fae5"
        elif result == 'SKIP':
            fail_count += 1
            status_color = "#f59e0b"
            status_text = "⊘ SKIP"
            status_bg = "#fef3c7"
            img = ng_image
        else:  # NG or FAILED
            fail_count += 1
            img = ng_image
            status_color = "#ef4444"
            status_text = "✗ FAILED"
            status_bg = "#fee2e2"
        
        # Play sound based on result
        play_result_sound(result)

        # Show image or icon
        if img:
            result_label.config(image=img, bg="#f3f4f6")
            result_label.image = img
        else:
            # Show text icon for SKIP
            result_label.config(
                text="⊘",
                font=("Segoe UI", 60),
                fg="#f59e0b",
                bg="#f3f4f6"
            )
        
        # Update status with badge style
        result_status_label.config(text=status_text, fg=status_color)
        result_status_frame.config(bg=status_bg)
        result_status_label.config(bg=status_bg)
        
        # Update work time
        if work_time:
            result_time_label.config(text=str(work_time))
        else:
            result_time_label.config(text="N/A")
        
        # Update timestamp
        result_timestamp_label.config(
            text=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Update statistics
        update_statistics()

    def add_to_history(heater_id, result, work_time):
        """Thêm vào lịch sử kiểm tra"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Normalize result for consistency
        if result not in ['PASS', 'SKIP']:
            result = 'FAIL'
        
        # Thêm vào đầu list
        check_history.insert(0, {
            'time': timestamp,
            'heater_id': heater_id,
            'result': result,
            'work_time': work_time
        })
        
        # Không giới hạn số lượng records - lưu tất cả cho đến khi tắt chương trình
        # Data sẽ được reset khi restart application
        
        # Update history display
        update_history_display()

    def update_history_display():
        """Cập nhật hiển thị lịch sử với filter"""
        # Clear current items
        for item in history_tree.get_children():
            history_tree.delete(item)
        
        # Filter history based on selected filter
        filtered_history = check_history
        if history_filter != "All":
            filtered_history = [item for item in check_history if item['result'] == history_filter]
        
        # Chỉ hiển thị 200 records gần nhất để UI mượt mà
        # Toàn bộ data vẫn được lưu trong check_history
        display_limit = 200
        displayed_history = filtered_history[:display_limit]
        
        # Add history items
        for item in displayed_history:
            if item['result'] == 'PASS':
                result_icon = "✓"
            elif item['result'] == 'SKIP':
                result_icon = "⊘"
            else:
                result_icon = "✗"
            
            history_tree.insert('', 'end', values=(
                item['time'],
                item['heater_id'][:20] + '...' if len(item['heater_id']) > 20 else item['heater_id'],
                result_icon,
                item['result']
            ), tags=(item['result'].lower(),))
        
        # Update filter label with total count info
        total_count = len(check_history)
        filtered_count = len(filtered_history)
        if history_filter != "All":
            filter_label.config(text=f"Filter: {history_filter} ({filtered_count}/{total_count} records)")
        else:
            filter_label.config(text=f"Filter: All ({total_count} records)")
        
        # Show warning if displaying limited results
        if len(filtered_history) > display_limit:
            filter_label.config(text=f"Filter: {history_filter} (Showing {display_limit}/{filtered_count} records)")

    
    def show_filter_menu(event):
        """Hiển thị menu filter khi click vào header Result"""
        # Create popup menu
        filter_menu = tk.Menu(root_P230, tearoff=0)
        
        def set_filter(filter_value):
            nonlocal history_filter
            history_filter = filter_value
            update_history_display()
        
        filter_menu.add_command(
            label="✓ All" if history_filter == "All" else "  All",
            command=lambda: set_filter("All")
        )
        filter_menu.add_separator()
        filter_menu.add_command(
            label="✓ PASS" if history_filter == "PASS" else "  PASS",
            command=lambda: set_filter("PASS")
        )
        filter_menu.add_command(
            label="✓ FAIL" if history_filter == "FAIL" else "  FAIL",
            command=lambda: set_filter("FAIL")
        )
        filter_menu.add_command(
            label="✓ SKIP" if history_filter == "SKIP" else "  SKIP",
            command=lambda: set_filter("SKIP")
        )
        
        # Show menu at cursor position
        try:
            filter_menu.tk_popup(event.x_root, event.y_root)
        finally:
            filter_menu.grab_release()

    def check_heater_id(event=None):
        """Kiểm tra HEATER ID"""
        heater_id = entry.get().strip()
        
        if not heater_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập HEATER QR Code!")
            return
        
        # Show loading state (clear previous image)
        result_label.config(text="Đang kiểm tra...", image='', bg="#f3f4f6", fg="#9ca3af")
        result_label.image = None
        HEATER_label.config(text="Loading...")
        root_P230.update_idletasks()
        
        try:
            # Query based on mode
            mode = query_mode.get()
            if mode == "SQL Server":
                conn = connect_to_database()
                result = execute_query_afa(conn, heater_id)
                if conn:
                    conn.close()
            else:  # Oracle
                result = execute_query_oracle(heater_id)
            
            if result:
                display_result(result[0], result[1])
                HEATER_label.config(text=heater_id)
                log_to_gui(f"✓ Checked heater_id: {heater_id} - Result: {result[0]}")
                # Normalize result for history (Oracle returns 'OK', SQL Server returns 'PASS')
                if result[0] in ['OK', 'PASS']:
                    normalized_result = 'PASS'
                elif result[0] == 'SKIP':
                    normalized_result = 'SKIP'
                else:
                    normalized_result = 'FAIL'
                add_to_history(heater_id, normalized_result, result[1])
            else:
                display_result('NG')
                HEATER_label.config(text=heater_id)
                log_to_gui(f"✗ Checked heater_id: {heater_id} - No data found")
                add_to_history(heater_id, 'FAIL', None)
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
            log_to_gui(f"✗ Error checking heater_id: {heater_id} - {str(e)}")
        
        # Clear entry
        entry.delete(0, tk.END)
        entry.focus()

    def check_connections():
        """Kiểm tra kết nối database"""
        def check_async():
            # Oracle
            oracle_indicator.set_status("checking")
            oracle_label.config(text="Checking...")
            root_P230.update_idletasks()
            
            oracle_connected = test_oracle_connection()
            oracle_indicator.set_status("connected" if oracle_connected else "disconnected")
            oracle_label.config(
                text="Connected" if oracle_connected else "Disconnected",
                fg="#10b981" if oracle_connected else "#ef4444"
            )
            
            # SQL Server
            sql_indicator.set_status("checking")
            sql_label.config(text="Checking...")
            root_P230.update_idletasks()
            
            sql_connected = test_sql_connection()
            sql_indicator.set_status("connected" if sql_connected else "disconnected")
            sql_label.config(
                text="Connected" if sql_connected else "Disconnected",
                fg="#10b981" if sql_connected else "#ef4444"
            )
            
            log_to_gui(f"Connection check - Oracle: {oracle_connected}, SQL: {sql_connected}")
        
        # Run in thread to avoid blocking UI
        threading.Thread(target=check_async, daemon=True).start()

    def test_oracle_connection():
        """Test Oracle connection"""
        try:
            oracle_params = get_oracle_connection_params()
            connection = cx_Oracle.connect(**oracle_params)
            connection.close()
            return True
        except:
            return False

    def test_sql_connection():
        """Test SQL Server connection"""
        try:
            conn_string = get_sql_connection_string()
            conn = pyodbc.connect(conn_string)
            conn.close()
            return True
        except:
            return False

    def open_settings():
        """Mở cửa sổ Settings"""
        settings_window = tk.Toplevel(root_P230)
        settings_window.title("⚙️ Settings - Configuration")
        settings_window.geometry("700x650")
        settings_window.configure(bg='#f5f7fa')
        settings_window.resizable(False, False)
        settings_window.grab_set()
        
        current_config = load_config()
        
        header = tk.Frame(settings_window, bg='#1e3a8a', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="⚙️ SETTINGS", font=("Segoe UI", 20, "bold"), bg='#1e3a8a', fg='white').pack(pady=15)
        
        main_frame = tk.Frame(settings_window, bg='#f5f7fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(main_frame, bg='#f5f7fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f7fa')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # UPDATE SETTINGS
        update_frame = tk.LabelFrame(scrollable_frame, text="🔄 Update Configuration", font=("Segoe UI", 11, "bold"), bg='white', fg='#1e3a8a', padx=15, pady=15)
        update_frame.pack(fill='x', pady=(0, 15))
        
        update_entries = {}
        for idx, (key, label, value) in enumerate([
            ('program_directory', 'Program Directory:', current_config['update'].get('program_directory', 'C:\\HEATER_CHECK')),
            ('ftp_server', 'FTP Server IP:', current_config['update'].get('ftp_server', '192.168.110.12')),
            ('ftp_username', 'FTP Username:', current_config['update'].get('ftp_username', 'update')),
            ('ftp_password', 'FTP Password:', current_config['update'].get('ftp_password', 'update')),
            ('update_path', 'Update Path:', current_config['update'].get('update_path', '/KhanhDQ/Update_Program/HEATER_CHECK/'))
        ]):
            tk.Label(update_frame, text=label, bg='white', font=("Segoe UI", 9)).grid(row=idx, column=0, sticky='w', pady=5)
            entry = tk.Entry(update_frame, font=("Segoe UI", 9), width=50, show='*' if key == 'ftp_password' else '')
            entry.insert(0, value)
            entry.grid(row=idx, column=1, pady=5, padx=10)
            update_entries[key] = entry
        
        # SQL SERVER SETTINGS
        sql_frame = tk.LabelFrame(scrollable_frame, text="🗄️ SQL Server Configuration", font=("Segoe UI", 11, "bold"), bg='white', fg='#1e3a8a', padx=15, pady=15)
        sql_frame.pack(fill='x', pady=(0, 15))
        
        sql_entries = {}
        for idx, (key, label, value) in enumerate([
            ('driver', 'Driver:', current_config['database']['sql_server']['driver']),
            ('server', 'Server:', current_config['database']['sql_server']['server']),
            ('port', 'Port:', current_config['database']['sql_server']['port']),
            ('database', 'Database:', current_config['database']['sql_server']['database']),
            ('username', 'Username:', current_config['database']['sql_server']['username']),
            ('password', 'Password:', current_config['database']['sql_server']['password'])
        ]):
            tk.Label(sql_frame, text=label, bg='white', font=("Segoe UI", 9)).grid(row=idx, column=0, sticky='w', pady=5)
            entry = tk.Entry(sql_frame, font=("Segoe UI", 9), width=50, show='*' if key == 'password' else '')
            entry.insert(0, value)
            entry.grid(row=idx, column=1, pady=5, padx=10)
            sql_entries[key] = entry
        
        # ORACLE SETTINGS
        oracle_frame = tk.LabelFrame(scrollable_frame, text="🗄️ Oracle Database Configuration", font=("Segoe UI", 11, "bold"), bg='white', fg='#1e3a8a', padx=15, pady=15)
        oracle_frame.pack(fill='x', pady=(0, 15))
        
        oracle_entries = {}
        for idx, (key, label, value) in enumerate([
            ('host', 'Host:', current_config['database']['oracle']['host']),
            ('port', 'Port:', current_config['database']['oracle']['port']),
            ('service_name', 'Service Name:', current_config['database']['oracle']['service_name']),
            ('username', 'Username:', current_config['database']['oracle']['username']),
            ('password', 'Password:', current_config['database']['oracle']['password'])
        ]):
            tk.Label(oracle_frame, text=label, bg='white', font=("Segoe UI", 9)).grid(row=idx, column=0, sticky='w', pady=5)
            entry = tk.Entry(oracle_frame, font=("Segoe UI", 9), width=50, show='*' if key == 'password' else '')
            entry.insert(0, value)
            entry.grid(row=idx, column=1, pady=5, padx=10)
            oracle_entries[key] = entry
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        button_frame = tk.Frame(settings_window, bg='#f5f7fa')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        def save_settings():
            try:
                new_config = {
                    "update": {k: update_entries[k].get() for k in update_entries},
                    "database": {
                        "sql_server": {k: sql_entries[k].get() for k in sql_entries},
                        "oracle": {k: oracle_entries[k].get() for k in oracle_entries}
                    }
                }
                if save_config(new_config):
                    messagebox.showinfo("Success", "✓ Settings saved!\n\nRestart application for changes.")
                    settings_window.destroy()
                else:
                    messagebox.showerror("Error", "Failed to save settings!")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)}")
        
        def reset_to_default():
            from config_manager import DEFAULT_CONFIG
            if messagebox.askyesno("Confirm", "Reset all settings to default?"):
                if save_config(DEFAULT_CONFIG):
                    messagebox.showinfo("Success", "✓ Reset complete! Restart application.")
                    settings_window.destroy()
        
        tk.Button(button_frame, text="💾 Save Settings", command=save_settings, bg='#10b981', fg='white', font=("Segoe UI", 10, "bold"), relief='flat', padx=20, pady=10, cursor='hand2').pack(side='left', padx=5)
        tk.Button(button_frame, text="🔄 Reset to Default", command=reset_to_default, bg='#f59e0b', fg='white', font=("Segoe UI", 10, "bold"), relief='flat', padx=20, pady=10, cursor='hand2').pack(side='left', padx=5)
        tk.Button(button_frame, text="❌ Cancel", command=settings_window.destroy, bg='#6b7280', fg='white', font=("Segoe UI", 10, "bold"), relief='flat', padx=20, pady=10, cursor='hand2').pack(side='right', padx=5)

    # ==================== MAIN WINDOW ====================
    root_P230 = tk.Tk()
    root_P230.title("HEATER Function Checker - Model P230")
    root_P230.geometry("1400x900")
    root_P230.configure(bg="#f5f7fa")
    
    # Initialize query_mode after root window is created
    query_mode = tk.StringVar(value="SQL Server")
    
    # Style configuration
    style = ttk.Style()
    style.theme_use('clam')
    
    # Pre-load images with larger size for emphasis
    try:
        ok_image = ImageTk.PhotoImage(Image.open(r"Resource\Ok.png").resize((200, 200)))
        ng_image = ImageTk.PhotoImage(Image.open(r"Resource\NG.png").resize((200, 200)))
    except:
        ok_image = None
        ng_image = None
        print("Warning: Could not load images")

    # Initialize sound system
    sound_enabled = True
    try:
        pygame.mixer.init()
    except Exception as e:
        sound_enabled = False
        print(f"Warning: Could not initialize sound system: {e}")

    def play_result_sound(result):
        if not sound_enabled:
            return
        try:
            if result == 'PASS':
                pygame.mixer.music.load(r"Resource\OK.mp3")
            else:
                pygame.mixer.music.load(r"Resource\NG.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Warning: Could not play sound: {e}")

    # ==================== MENU BAR ====================
    menubar = tk.Menu(root_P230)
    
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="🏭 Switch to ECIGA-P1", command=switch_to_P1)
    file_menu.add_command(label="🏭 Switch to ECIGA-P4", command=switch_to_P4)
    file_menu.add_separator()
    file_menu.add_command(label="🚪 Logout", command=logout)
    menubar.add_cascade(label="Menu", menu=file_menu)
    
    tools_menu = tk.Menu(menubar, tearoff=0)
    tools_menu.add_command(label="🔄 Check Connections", command=check_connections)
    tools_menu.add_command(label="⚙️ Settings", command=open_settings)
    menubar.add_cascade(label="Tools", menu=tools_menu)
    
    root_P230.config(menu=menubar)

    # ==================== HEADER ====================
    header_frame = tk.Frame(root_P230, bg="#1e3a8a", height=100)
    header_frame.pack(fill="x", side="top")
    header_frame.pack_propagate(False)
    
    header_content = tk.Frame(header_frame, bg="#1e3a8a")
    header_content.pack(expand=True)
    
    title_label = tk.Label(
        header_content,
        text="HEATER FUNCTION CHECKER",
        font=("Segoe UI", 28, "bold"),
        bg="#1e3a8a",
        fg="white"
    )
    title_label.pack()
    
    subtitle_label = tk.Label(
        header_content,
        text="Model P230 - Production Testing System",
        font=("Segoe UI", 14),
        bg="#1e3a8a",
        fg="#93c5fd"
    )
    subtitle_label.pack()

    # ==================== MAIN CONTENT ====================
    main_container = tk.Frame(root_P230, bg="#f5f7fa")
    main_container.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Left Panel (60%)
    left_panel = tk.Frame(main_container, bg="#f5f7fa")
    left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    # Right Panel (40%)
    right_panel = tk.Frame(main_container, bg="#f5f7fa")
    right_panel.pack(side="right", fill="both", padx=(10, 0))
    
    # ==================== INPUT CARD ====================
    input_card = ModernCard(left_panel, title="🔍 HEATER QR Code Scanner")
    input_card.pack(fill="x", pady=(0, 15))
    
    input_content = input_card.get_content_frame()
    
    input_frame = tk.Frame(input_content, bg="white")
    input_frame.pack(fill="x", pady=10)
    
    entry = tk.Entry(
        input_frame,
        font=("Segoe UI", 16),
        relief="solid",
        bd=1,
        fg="#1a1a1a"
    )
    entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))
    entry.bind('<Return>', check_heater_id)
    entry.focus()
    
    check_button = tk.Button(
        input_frame,
        text="CHECK",
        command=check_heater_id,
        font=("Segoe UI", 12, "bold"),
        bg="#1e3a8a",
        fg="white",
        relief="flat",
        padx=30,
        pady=10,
        cursor="hand2"
    )
    check_button.pack(side="right")
    
    hint_label = tk.Label(
        input_content,
        text="💡 Scan or enter HEATER QR Code and press Enter",
        font=("Segoe UI", 9),
        bg="white",
        fg="#6b7280"
    )
    hint_label.pack(anchor="w")

    # ==================== RESULT CARD ====================
    result_card = ModernCard(left_panel, title="📊 Test Result")
    result_card.pack(fill="both", expand=True, pady=(0, 15))
    
    result_content = result_card.get_content_frame()
    
    # Fixed height container to prevent expansion
    result_container = tk.Frame(result_content, bg="white", height=320)
    result_container.pack(fill="x")
    result_container.pack_propagate(False)  # Prevent auto-resize
    
    # Top section: HEATER ID
    HEATER_frame = tk.Frame(result_container, bg="white")
    HEATER_frame.pack(fill="x", pady=(5, 10))
    
    HEATER_title = tk.Label(
        HEATER_frame,
        text="HEATER ID:",
        font=("Segoe UI", 9),
        bg="white",
        fg="#6b7280"
    )
    HEATER_title.pack(side="left")
    
    HEATER_label = tk.Label(
        HEATER_frame,
        text="Waiting for scan...",
        font=("Segoe UI", 11, "bold"),
        bg="white",
        fg="#1a1a1a"
    )
    HEATER_label.pack(side="left", padx=10)
    
    # Main Result Display - Horizontal Layout
    result_main_frame = tk.Frame(result_container, bg="white")
    result_main_frame.pack(fill="both", expand=True, pady=5)
    
    # Left: Image/Icon with border (square)
    result_image_frame = tk.Frame(result_main_frame, bg="#f3f4f6", width=220, height=220, relief="solid", bd=1)
    result_image_frame.pack(side="left", padx=(10, 0), pady=10)
    result_image_frame.pack_propagate(False)
    
    result_label = tk.Label(
        result_image_frame,
        text="Ready",
        font=("Segoe UI", 14),
        bg="#f3f4f6",
        fg="#9ca3af"
    )
    result_label.pack(expand=True)
    
    # Right: Status Information
    result_info_container = tk.Frame(result_main_frame, bg="white")
    result_info_container.pack(side="left", fill="both", expand=True, padx=25)
    
    # Status Badge
    result_status_frame = tk.Frame(result_info_container, bg="white", relief="solid", bd=1)
    result_status_frame.pack(fill="x", pady=(10, 5))
    
    result_status_label = tk.Label(
        result_status_frame,
        text="",
        font=("Segoe UI", 24, "bold"),
        bg="white",
        fg="#6b7280",
        pady=10
    )
    result_status_label.pack(anchor="w", padx=15)
    
    # Divider line
    divider = tk.Frame(result_info_container, bg="#e5e7eb", height=1)
    divider.pack(fill="x", pady=8)
    
    # Work Time
    result_time_frame = tk.Frame(result_info_container, bg="white")
    result_time_frame.pack(fill="x", pady=3)
    
    tk.Label(
        result_time_frame,
        text="⏱ Work Time:",
        font=("Segoe UI", 9),
        bg="white",
        fg="#6b7280"
    ).pack(side="left")
    
    result_time_label = tk.Label(
        result_time_frame,
        text="N/A",
        font=("Segoe UI", 9, "bold"),
        bg="white",
        fg="#1a1a1a"
    )
    result_time_label.pack(side="left", padx=5)
    
    # Timestamp
    result_timestamp_frame = tk.Frame(result_info_container, bg="white")
    result_timestamp_frame.pack(fill="x", pady=3)
    
    tk.Label(
        result_timestamp_frame,
        text="🕐 Checked:",
        font=("Segoe UI", 9),
        bg="white",
        fg="#6b7280"
    ).pack(side="left")
    
    result_timestamp_label = tk.Label(
        result_timestamp_frame,
        text="N/A",
        font=("Segoe UI", 9),
        bg="white",
        fg="#9ca3af"
    )
    result_timestamp_label.pack(side="left", padx=5)

    # ==================== STATISTICS CARD ====================
    stats_card = ModernCard(right_panel, title="📈 Statistics")
    stats_card.pack(fill="x", pady=(0, 15))
    
    stats_content = stats_card.get_content_frame()
    stats_labels = {}
    
    # Grid layout for stats
    stats_grid = tk.Frame(stats_content, bg="white")
    stats_grid.pack(fill="x")
    
    stats_items = [
        ("Total Checks", "total", "#3b82f6"),
        ("Passed", "pass", "#10b981"),
        ("Failed", "fail", "#ef4444"),
        ("Pass Rate", "rate", "#8b5cf6")
    ]
    
    for idx, (label, key, color) in enumerate(stats_items):
        row = idx // 2
        col = idx % 2
        
        stat_frame = tk.Frame(stats_grid, bg="white")
        stat_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        value_label = tk.Label(
            stat_frame,
            text="0",
            font=("Segoe UI", 24, "bold"),
            bg="white",
            fg=color
        )
        value_label.pack()
        
        name_label = tk.Label(
            stat_frame,
            text=label,
            font=("Segoe UI", 9),
            bg="white",
            fg="#6b7280"
        )
        name_label.pack()
        
        stats_labels[key] = value_label
    
    stats_grid.columnconfigure(0, weight=1)
    stats_grid.columnconfigure(1, weight=1)

    # ==================== CONNECTION STATUS CARD ====================
    connection_card = ModernCard(right_panel, title="🔌 Database Connection")
    connection_card.pack(fill="x", pady=(0, 15))
    
    conn_content = connection_card.get_content_frame()
    
    # Query Mode Selector
    mode_frame = tk.Frame(conn_content, bg="white")
    mode_frame.pack(fill="x", pady=(0, 15))
    
    mode_label = tk.Label(
        mode_frame,
        text="Query Mode:",
        font=("Segoe UI", 10, "bold"),
        bg="white"
    )
    mode_label.pack(side="left", padx=(0, 10))
    
    sql_radio = tk.Radiobutton(
        mode_frame,
        text="SQL Server",
        variable=query_mode,
        value="SQL Server",
        font=("Segoe UI", 9),
        bg="white",
        activebackground="white"
    )
    sql_radio.pack(side="left", padx=5)
    
    oracle_radio = tk.Radiobutton(
        mode_frame,
        text="Oracle",
        variable=query_mode,
        value="Oracle",
        font=("Segoe UI", 9),
        bg="white",
        activebackground="white"
    )
    oracle_radio.pack(side="left", padx=5)
    
    # Oracle Status
    oracle_frame = tk.Frame(conn_content, bg="white")
    oracle_frame.pack(fill="x", pady=5)
    
    oracle_indicator = StatusIndicator(oracle_frame, size=12)
    oracle_indicator.pack(side="left", padx=(0, 10))
    
    tk.Label(
        oracle_frame,
        text="Oracle:",
        font=("Segoe UI", 10),
        bg="white"
    ).pack(side="left")
    
    oracle_label = tk.Label(
        oracle_frame,
        text="Not checked",
        font=("Segoe UI", 10),
        bg="white",
        fg="#6b7280"
    )
    oracle_label.pack(side="left", padx=10)
    
    # SQL Server Status
    sql_frame = tk.Frame(conn_content, bg="white")
    sql_frame.pack(fill="x", pady=5)
    
    sql_indicator = StatusIndicator(sql_frame, size=12)
    sql_indicator.pack(side="left", padx=(0, 10))
    
    tk.Label(
        sql_frame,
        text="SQL Server:",
        font=("Segoe UI", 10),
        bg="white"
    ).pack(side="left")
    
    sql_label = tk.Label(
        sql_frame,
        text="Not checked",
        font=("Segoe UI", 10),
        bg="white",
        fg="#6b7280"
    )
    sql_label.pack(side="left", padx=10)
    
    # Check button
    check_conn_button = tk.Button(
        conn_content,
        text="🔄 Check Connections",
        command=check_connections,
        font=("Segoe UI", 9),
        bg="#f3f4f6",
        fg="#1a1a1a",
        relief="flat",
        pady=8,
        cursor="hand2"
    )
    check_conn_button.pack(fill="x", pady=(15, 0))

    # ==================== HISTORY CARD ====================
    history_card = ModernCard(right_panel, title="📜 Recent History")
    history_card.pack(fill="both", expand=True)
    
    history_content = history_card.get_content_frame()
    
    # Filter control frame
    filter_control_frame = tk.Frame(history_content, bg="white")
    filter_control_frame.pack(fill="x", pady=(0, 8))
    
    filter_label = tk.Label(
        filter_control_frame,
        text="Filter: All",
        font=("Segoe UI", 9),
        bg="white",
        fg="#6b7280"
    )
    filter_label.pack(side="left")
    
    filter_hint_label = tk.Label(
        filter_control_frame,
        text="💡 Click 'Result' to filter",
        font=("Segoe UI", 8, "italic"),
        bg="white",
        fg="#9ca3af"
    )
    filter_hint_label.pack(side="right")
    
    # Treeview for history
    history_tree = ttk.Treeview(
        history_content,
        columns=('Time', 'HEATER ID', 'Icon', 'Result'),
        show='headings',
        height=8,
        selectmode='browse'
    )
    
    history_tree.heading('Time', text='Time')
    history_tree.heading('HEATER ID', text='HEATER ID')
    history_tree.heading('Icon', text='')
    history_tree.heading('Result', text='Result 🔽')
    
    history_tree.column('Time', width=70)
    history_tree.column('HEATER ID', width=150)
    history_tree.column('Icon', width=30)
    history_tree.column('Result', width=60)
    
    # Tags for colors
    history_tree.tag_configure('pass', foreground='#10b981')
    history_tree.tag_configure('fail', foreground='#ef4444')
    history_tree.tag_configure('skip', foreground='#f59e0b')
    
    # Bind click event to Result column header
    def on_header_click(event):
        region = history_tree.identify_region(event.x, event.y)
        if region == "heading":
            column = history_tree.identify_column(event.x)
            if column == '#4':  # Result column
                show_filter_menu(event)
    
    history_tree.bind('<Button-1>', on_header_click)
    
    history_tree.pack(fill="both", expand=True)

    # ==================== LOG CARD ====================
    log_card = ModernCard(left_panel, title="📝 Activity Log")
    log_card.configure(height=220)
    log_card.pack(fill="x")
    log_card.pack_propagate(False)
    
    log_content = log_card.get_content_frame()
    
    log_frame = tk.Frame(log_content, bg="white")
    log_frame.pack(fill="both", expand=True)
    
    log_scroll = tk.Scrollbar(log_frame)
    log_scroll.pack(side="right", fill="y")
    
    log_text = tk.Text(
        log_frame,
        height=5,
        font=("Consolas", 9),
        bg="#1e1e1e",
        fg="#d4d4d4",
        relief="flat",
        yscrollcommand=log_scroll.set
    )
    log_text.pack(side="left", fill="both", expand=True)
    log_scroll.config(command=log_text.yview)

    # ==================== FOOTER ====================
    footer_frame = tk.Frame(root_P230, bg="#f5f7fa", height=40)
    footer_frame.pack(side="bottom", fill="x", pady=(10, 0))
    footer_frame.pack_propagate(False)
    
    copyright_label = tk.Label(
        footer_frame,
        text="© 2025 ITM Semiconductor Vietnam - IT Team - KhanhIT | All Rights Reserved",
        font=("Segoe UI", 9),
        bg="#f5f7fa",
        fg="#6b7280"
    )
    copyright_label.pack(expand=True)

    # ==================== INITIAL SETUP ====================
    # Check connections on startup
    root_P230.after(1000, check_connections)
    
    # Welcome log
    log_to_gui("System initialized successfully")
    log_to_gui(f"Query mode: {query_mode.get()}")
    
    root_P230.mainloop()
