import pyodbc
import json
from datetime import datetime, timedelta

# --- Cấu hình cho Windows Authentication (Khi quên mật khẩu 'sa') ---
# Chúng ta sẽ dùng quyền đăng nhập Windows của bạn, không cần username/password.
DB_CONFIG = {
    'server': 'TranCongQuy', # Server name của bạn
    'database': 'weather_db',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def create_connection():
    """Tạo kết nối đến CSDL SQL Server bằng Windows Authentication."""
    connection = None
    try:
        # Chuỗi kết nối đặc biệt có 'Trusted_Connection=yes'
        conn_str = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"Trusted_Connection=yes;"
        )
        connection = pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        print(f"Lỗi kết nối CSDL: '{e}'")
        print("Gợi ý: Hãy chắc chắn bạn đã chạy SQL Server Management Studio bằng 'Windows Authentication' thành công.")
    return connection

def get_location(city_name, country):
    """Lấy thông tin địa điểm từ CSDL."""
    conn = create_connection()
    if not conn: return None
    cursor = conn.cursor()
    query = "SELECT * FROM locations WHERE city_name = ? AND country = ?"
    cursor.execute(query, (city_name, country))
    columns = [column[0] for column in cursor.description]
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(zip(columns, row))
    return None

def add_location(city_name, country, lat, lon):
    """Thêm một địa điểm mới và trả về id của nó."""
    conn = create_connection()
    if not conn: return None
    cursor = conn.cursor()
    # OUTPUT INSERTED.id là cú pháp của SQL Server để lấy ID vừa chèn
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
    """Lưu dữ liệu thời tiết mới vào cache."""
    conn = create_connection()
    if not conn: return
    cursor = conn.cursor()
    query = """
    INSERT INTO weather_cache
    (location_id, timestamp, temperature, humidity, description, wind_speed, icon_code, data_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        location_id,
        datetime.now(),
        data['main']['temp'],
        data['main']['humidity'],
        data['weather'][0]['description'],
        data['wind']['speed'],
        data['weather'][0]['icon'],
        json.dumps(data) # Chuyển dictionary Python thành chuỗi JSON
    )
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def get_recent_weather(location_id, minutes=30):
    """Lấy dữ liệu thời tiết gần đây từ cache (trong vòng 30 phút)."""
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
        weather_dict['data_json'] = json.loads(weather_dict['data_json']) # Chuyển chuỗi JSON về lại dictionary
        return weather_dict
    return None