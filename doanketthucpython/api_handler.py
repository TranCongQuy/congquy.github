import requests

# API Key đã được lấy chính xác từ hình ảnh bạn cung cấp.
API_KEY = "0a291052e260f6fadaa6519a3aaa7ccd"

def get_weather_data(city_query):
    """Lấy dữ liệu thời tiết hiện tại từ OpenWeatherMap API."""
    base_url = "http://api.openweathermap.org/data/2.5/weather"

    # Các tham số cho API call
    params = {
        'q': city_query,   # vd: "Hue,VN"
        'appid': API_KEY,
        'units': 'metric', # Để nhận nhiệt độ theo độ C
        'lang': 'vi'       # Để nhận mô tả bằng tiếng Việt
    }

    try:
        response = requests.get(base_url, params=params)
        # Báo lỗi nếu request không thành công (vd: 401, 404, 500)
        response.raise_for_status()
        return response.json() # Trả về dữ liệu dạng dictionary
    except requests.exceptions.HTTPError as errh:
        # In ra lỗi cụ thể hơn để dễ chẩn đoán
        print(f"Lỗi HTTP: {errh}")
        if response.status_code == 401:
            print("=> Gợi ý: Lỗi 401 Unauthorized. API key có thể sai hoặc chưa được kích hoạt hoàn toàn.")
        elif response.status_code == 404:
            print(f"=> Gợi ý: Lỗi 404 Not Found. Thành phố '{city_query}' có thể không được tìm thấy.")
    except requests.exceptions.RequestException as err:
        print(f"Lỗi kết nối hoặc lỗi khác: {err}")

    return None

# --- Thử nghiệm nhanh ---
# Bạn có thể bỏ comment ở dưới để chạy riêng file này và kiểm tra API
# if __name__ == '__main__':
#     data = get_weather_data("London,UK")
#     if data:
#         print(data)