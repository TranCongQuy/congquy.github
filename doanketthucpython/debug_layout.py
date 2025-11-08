# ==============================================================================
# FILE: final_app.py (PHIÊN BẢN SỬA LỖI BỐ CỤC)
# Tác giả: Chuyên gia lập trình Python
# Mô tả: Sử dụng phương pháp bố cục thay thế (chỉ dùng pack) để đảm bảo
# hiển thị chính xác trên mọi môi trường.
# ==============================================================================

import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk
import pyodbc
import json
import requests
from datetime import datetime, timedelta

# PHẦN 1: LOGIC API (Không đổi)
API_KEY = "0a291052e260f6fadaa6519a3aaa7ccd" # <-- Nhớ thay key của bạn nếu cần

def get_weather_data(city_query):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': city_query, 'appid': API_KEY, 'units': 'metric', 'lang': 'vi'}
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Lỗi API: {err}")
        return None

# PHẦN 2: LOGIC CSDL (Không đổi)
DB_CONFIG = {
    'server': 'TranCongQuy',
    'database': 'weather_app_db',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def create_connection():
    try:
        conn_str = f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};Trusted_Connection=yes;"
        return pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        print(f"Lỗi kết nối CSDL: '{e}'")
        return None

# ... (Các hàm CSDL khác giữ nguyên, không cần dán lại cho ngắn gọn, chỉ cần copy từ code gốc) ...
def get_location(city_name, country):
    conn = create_connection()
    if not conn: return None
    cursor = conn.cursor()
    query = "SELECT * FROM locations WHERE city_name = ? AND country = ?"
    cursor.execute(query, (city_name, country))
    columns = [column[0] for column in cursor.description]
    row = cursor.fetchone()
    conn.close()
    return dict(zip(columns, row)) if row else None

def add_location(city_name, country, lat, lon):
    conn = create_connection()
    if not conn: return None
    cursor = conn.cursor()
    query = "INSERT INTO locations (city_name, country, latitude, longitude) OUTPUT INSERTED.id VALUES (?, ?, ?, ?)"
    try:
        cursor.execute(query, (city_name, country, lat, lon))
        location_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return location_id
    except pyodbc.IntegrityError:
        conn.close()
        return None

def add_weather_cache(location_id, data):
    conn = create_connection()
    if not conn: return
    cursor = conn.cursor()
    query = "INSERT INTO weather_cache (location_id, timestamp, temperature, humidity, description, wind_speed, icon_code, data_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    params = (location_id, datetime.now(), data['main']['temp'], data['main']['humidity'], data['weather'][0]['description'], data['wind']['speed'], data['weather'][0]['icon'], json.dumps(data))
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def get_recent_weather(location_id, minutes=30):
    conn = create_connection()
    if not conn: return None
    cursor = conn.cursor()
    time_threshold = datetime.now() - timedelta(minutes=minutes)
    query = "SELECT TOP 1 * FROM weather_cache WHERE location_id = ? AND timestamp >= ? ORDER BY timestamp DESC"
    cursor.execute(query, (location_id, time_threshold))
    columns = [column[0] for column in cursor.description]
    row = cursor.fetchone()
    conn.close()
    if row:
        weather_dict = dict(zip(columns, row))
        weather_dict['data_json'] = json.loads(weather_dict['data_json'])
        return weather_dict
    return None


# PHẦN 3: LOGIC GIAO DIỆN (ĐÃ SỬA LỖI BỐ CỤC)
def fetch_weather_data_for_gui(city_input):
    # ... (Hàm này giữ nguyên) ...
    parts = [p.strip() for p in city_input.split(',')]
    city_name, country_code = (parts[0], parts[1].upper()) if len(parts) > 1 else (parts[0], None)
    if not country_code:
        messagebox.showerror("Lỗi Đầu Vào", "Vui lòng nhập theo định dạng 'Thành phố, Mã quốc gia'.")
        return None, None
    location = get_location(city_name, country_code)
    if location:
        weather_from_cache = get_recent_weather(location['id'])
        if weather_from_cache:
            return weather_from_cache['data_json'], "Cache 💾"
    new_weather_data = get_weather_data(f"{city_name},{country_code}")
    if new_weather_data:
        location_id = location['id'] if location else None
        if not location_id:
            coords = new_weather_data.get('coord', {})
            location_id = add_location(new_weather_data.get('name'), new_weather_data.get('sys', {}).get('country'), coords.get('lat'), coords.get('lon'))
        if location_id:
            add_weather_cache(location_id, new_weather_data)
        return new_weather_data, "API 📡"
    messagebox.showwarning("Không Tìm Thấy", f"Không thể tìm thấy thông tin cho '{city_input}'.")
    return None, None

# --- Thiết lập giao diện ---
BG_COLOR, FRAME_COLOR, TEXT_COLOR = "#F5F5F5", "#FFFFFF", "#1F1F1F"
BUTTON_COLOR, BUTTON_TEXT = "#4A90E2", "#FFFFFF"
TITLE_FONT, RESULT_FONT, DEFAULT_FONT = ("Helvetica", 24, "bold"), ("Helvetica", 14), ("Helvetica", 12)

root = tk.Tk()
root.title("Ứng Dụng Thời Tiết - Final Fix")
root.geometry("450x550")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

main_frame = tk.Frame(root, bg=BG_COLOR, padx=20, pady=20)
main_frame.pack(fill=tk.BOTH, expand=True)

input_frame = tk.Frame(main_frame, bg=FRAME_COLOR, padx=15, pady=15)
input_frame.pack(fill=tk.X)
tk.Label(input_frame, text="Nhập (Thành phố, Mã quốc gia):", font=DEFAULT_FONT, bg=FRAME_COLOR, fg=TEXT_COLOR).pack()
city_entry = tk.Entry(input_frame, font=("Helvetica", 14), width=25, relief=tk.FLAT, justify='center')
city_entry.pack(pady=10)
city_entry.insert(0, "Da Nang, VN")

main_result_frame = tk.Frame(main_frame, bg=FRAME_COLOR, pady=20)
main_result_frame.pack(fill=tk.X, pady=20)
location_label = tk.Label(main_result_frame, text="---", font=TITLE_FONT, bg=FRAME_COLOR, fg=TEXT_COLOR)
location_label.pack(pady=10)
icon_label = tk.Label(main_result_frame, bg=FRAME_COLOR)
icon_label.pack()
temp_label = tk.Label(main_result_frame, text="--°C", font=("Helvetica", 48, "bold"), bg=FRAME_COLOR, fg=TEXT_COLOR)
temp_label.pack()
desc_label = tk.Label(main_result_frame, text="---", font=("Helvetica", 16, "italic"), bg=FRAME_COLOR, fg=TEXT_COLOR)
desc_label.pack()

# =================================================================
# === KHUNG CHI TIẾT ĐÃ ĐƯỢC THIẾT KẾ LẠI ĐỂ TRÁNH LỖI ===
# =================================================================
details_frame = tk.Frame(main_frame, bg=FRAME_COLOR, padx=15, pady=15)
details_frame.pack(fill=tk.X, expand=True)

humidity_label = tk.Label(details_frame, text="Độ ẩm: --%", font=RESULT_FONT, bg=FRAME_COLOR, fg=TEXT_COLOR)
humidity_label.pack(side=tk.LEFT) # Đặt bên trái

wind_label = tk.Label(details_frame, text="Gió: -- m/s", font=RESULT_FONT, bg=FRAME_COLOR, fg=TEXT_COLOR)
wind_label.pack(side=tk.RIGHT) # Đặt bên phải
# =================================================================

status_label = tk.Label(main_frame, text="", font=("Helvetica", 10, "italic"), bg=BG_COLOR, fg=TEXT_COLOR)
status_label.pack(pady=10)

def update_ui(weather_data, source):
    # ... (Hàm này giữ nguyên) ...
    if weather_data:
        location_label.config(text=f"{weather_data['name']}, {weather_data['sys']['country']}")
        temp_label.config(text=f"{weather_data['main']['temp']:.0f}°C")
        desc_label.config(text=weather_data['weather'][0]['description'].capitalize())
        humidity_label.config(text=f"Độ ẩm: {weather_data['main']['humidity']}%")
        wind_label.config(text=f"Gió: {weather_data['wind']['speed']} m/s")
        status_label.config(text=f"Nguồn: {source}")
        icon_code = weather_data['weather'][0]['icon']
        try:
            image = Image.open(f"icons/{icon_code}.png")
            photo = ImageTk.PhotoImage(image)
            icon_label.config(image=photo)
            icon_label.image = photo
        except FileNotFoundError:
            icon_label.config(image=None, text=f"({icon_code})")
    else:
        location_label.config(text="---")
        temp_label.config(text="--°C")
        desc_label.config(text="---")
        humidity_label.config(text="Độ ẩm: --%")
        wind_label.config(text="Gió: -- m/s")
        status_label.config(text="")
        icon_label.config(image=None)

def on_search_click(event=None):
    # ... (Hàm này giữ nguyên) ...
    city = city_entry.get()
    if not city: return
    search_button.config(state="disabled")
    status_label.config(text="Đang tìm kiếm...")
    root.update_idletasks()
    weather_data, source = fetch_weather_data_for_gui(city)
    update_ui(weather_data, source)
    search_button.config(state="normal")

search_button = tk.Button(input_frame, text="Xem Thời Tiết", font=DEFAULT_FONT, bg=BUTTON_COLOR, fg=BUTTON_TEXT, relief=tk.FLAT, activebackground="#357ABD", activeforeground=BUTTON_TEXT, command=on_search_click)
search_button.pack(pady=10)
city_entry.bind("<Return>", on_search_click)

root.mainloop()