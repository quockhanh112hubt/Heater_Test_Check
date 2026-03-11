import tkinter as tk
from tkinter import ttk

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Giao Diện PMI")
root.geometry("1200x600")

# Các biến để lưu trữ thông tin từ Entry
sub_id_var = tk.StringVar()
pack_id_var = tk.StringVar()

# Tạo Frame chính để chứa các widget
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Các Frame con
frame_input_data = ttk.Frame(main_frame)
frame_input_data.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

frame_ng_data = ttk.Frame(main_frame)
frame_ng_data.grid(row=1, column=0, sticky="nsew")

frame_info = ttk.Frame(main_frame)
frame_info.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(10, 0))

# Cài đặt các Grid row và column
main_frame.grid_columnconfigure(0, weight=2)
main_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)

# Input Data Section
label_sub_id = tk.Label(frame_input_data, text="Sub ID", bg="#9ACD32", fg="black", font=("Arial", 12))
label_sub_id.grid(row=0, column=0, sticky="nsew", ipadx=5, ipady=5)

entry_sub_id = ttk.Entry(frame_input_data, textvariable=sub_id_var, font=("Arial", 12), width=25)
entry_sub_id.grid(row=0, column=1, sticky="nsew", ipadx=5, ipady=5)

label_spec_count = tk.Label(frame_input_data, text="Spec Count", bg="#9ACD32", fg="black", font=("Arial", 12))
label_spec_count.grid(row=0, column=2, sticky="nsew", ipadx=5, ipady=5)

label_spec_value = tk.Label(frame_input_data, text="1", bg="#F0E68C", fg="black", font=("Arial", 12), width=12)
label_spec_value.grid(row=0, column=3, sticky="nsew", ipadx=5, ipady=5)

button_clear = ttk.Button(frame_input_data, text="Clear")
button_clear.grid(row=0, column=4, sticky="nsew", ipadx=5, ipady=5)

label_pack_id = tk.Label(frame_input_data, text="Pack ID", bg="#9ACD32", fg="black", font=("Arial", 12))
label_pack_id.grid(row=1, column=0, sticky="nsew", ipadx=5, ipady=5)

entry_pack_id = ttk.Entry(frame_input_data, textvariable=pack_id_var, font=("Arial", 12), width=25)
entry_pack_id.grid(row=1, column=1, sticky="nsew", ipadx=5, ipady=5)

label_scan_count = tk.Label(frame_input_data, text="Scan Count", bg="#9ACD32", fg="black", font=("Arial", 12))
label_scan_count.grid(row=1, column=2, sticky="nsew", ipadx=5, ipady=5)

label_scan_value = tk.Label(frame_input_data, text="1", bg="#F0E68C", fg="black", font=("Arial", 12), width=12)
label_scan_value.grid(row=1, column=3, sticky="nsew", ipadx=5, ipady=5)

button_execute = ttk.Button(frame_input_data, text="Execute", state="disabled")
button_execute.grid(row=1, column=4, sticky="nsew", ipadx=5, ipady=5)

# Frame con cho phần Input Data
frame_table_input = ttk.Frame(frame_input_data)
frame_table_input.grid(row=2, column=0, columnspan=5, sticky="nsew", pady=(10, 0))

# Table cho Input Data
columns = ('Cell ID', 'Sub ID', 'Pack ID', 'Skip', 'Result')
tree_input = ttk.Treeview(frame_table_input, columns=columns, show='headings', height=6)

# Đặt tên cho các cột
for col in columns:
    tree_input.heading(col, text=col)
    tree_input.column(col, minwidth=0, width=200, stretch=False)

# Thêm dữ liệu ví dụ vào bảng
tree_input.insert('', 'end', values=("L4L63DE244N1153169", "T0448240829100001", "LESBAT0448XXXXR1000001240829", "SKIP", "OK"))

tree_input.pack(fill='both', expand=True)

# NG Data Section
frame_table_ng = ttk.Frame(frame_ng_data)
frame_table_ng.grid(row=0, column=0, columnspan=5, sticky="nsew")

# Table cho NG Data
columns_ng = ('Sub ID', 'Pack ID', 'Overlap')
tree_ng = ttk.Treeview(frame_table_ng, columns=columns_ng, show='headings', height=6)

# Đặt tên cho các cột
for col in columns_ng:
    tree_ng.heading(col, text=col)
    tree_ng.column(col, minwidth=0, width=200, stretch=False)

tree_ng.pack(fill='both', expand=True)

# Frame cho phần thông tin bên phải
info_labels = [
    ("Line", "PMI Main 1"), ("Order", "S20240828002"),
    ("Model", "BAT0448"), ("Process", "Pack and Jig Matching"),
    ("Cell Input Qty", "Single (1)"), ("Total Judge", "OK")
]

for i, (label_text, value) in enumerate(info_labels):
    label = tk.Label(frame_info, text=label_text, bg="#4682B4", fg="white", font=("Arial", 12))
    label.grid(row=i, column=0, sticky="nsew", ipadx=5, ipady=5)

    value_label = tk.Label(frame_info, text=value, bg="#B0E0E6", fg="black", font=("Arial", 12))
    value_label.grid(row=i, column=1, sticky="nsew", ipadx=5, ipady=5)

# Cột cuối cho các nút OK, NG và Reset
button_ok = ttk.Button(frame_info, text="OK(1)")
button_ok.grid(row=6, column=0, columnspan=2, sticky="nsew", ipadx=5, ipady=10)

button_ng = ttk.Button(frame_info, text="NG(0)")
button_ng.grid(row=7, column=0, columnspan=2, sticky="nsew", ipadx=5, ipady=10)

button_reset = ttk.Button(frame_info, text="Reset")
button_reset.grid(row=8, column=0, columnspan=2, sticky="nsew", ipadx=5, ipady=10)

# Khung hiển thị Work Date và Message Tag
frame_bottom = ttk.Frame(main_frame)
frame_bottom.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(10, 0))

work_date_label = ttk.Label(frame_bottom, text="Work Date : 2024.08.29", font=("Arial", 12))
work_date_label.pack(side="right", padx=(0, 10))

message_tag_label = ttk.Label(frame_bottom, text="Message Tag :", font=("Arial", 12))
message_tag_label.pack(side="left", padx=(10, 0))

root.mainloop()
