import database as db
import api_handler as api
import time

def display_weather(weather_data, source="API"):
    """Hiển thị thông tin thời tiết một cách đẹp mắt."""
    # Lấy thông tin từ dictionary dữ liệu thời tiết
    city_name = weather_data.get('name', 'N/A')
    country = weather_data.get('sys', {}).get('country', 'N/A')
    description = weather_data.get('weather', [{}])[0].get('description', 'N/A').capitalize()
    temp = weather_data.get('main', {}).get('temp', 'N/A')
    humidity = weather_data.get('main', {}).get('humidity', 'N/A')
    wind_speed = weather_data.get('wind', {}).get('speed', 'N/A')

    print("\n" + "="*40)
    print(f"Thông tin thời tiết cho: {city_name}, {country} (Nguồn: {source})")
    print("="*40)
    print(f"🌡️  Nhiệt độ: {temp}°C")
    print(f"💧 Độ ẩm: {humidity}%")
    print(f"💨 Tốc độ gió: {wind_speed} m/s")
    print(f"📝 Tình trạng: {description}")
    print("="*40 + "\n")

def main():
    """Hàm chạy chính của ứng dụng."""
    while True:
        city_input = input("Nhập tên thành phố, mã quốc gia (VD: Hue, VN) (hoặc 'exit' để thoát): ").strip()
        if not city_input:
            continue
        if city_input.lower() == 'exit':
            print("👋 Cảm ơn đã sử dụng ứng dụng!")
            break

        # Tách tên thành phố và mã quốc gia
        parts = [p.strip() for p in city_input.split(',')]
        city_name = parts[0]
        country_code = parts[1].upper() if len(parts) > 1 else None

        if not country_code:
            print("⚠️ Vui lòng nhập theo định dạng 'Thành phố, Mã quốc gia' (VD: Hanoi, VN).")
            continue

        # 1. Kiểm tra CSDL xem có địa điểm này chưa
        location = db.get_location(city_name, country_code)

        weather_from_cache = None
        if location:
            print(f"📍 Đã tìm thấy '{city_name}' trong CSDL. Kiểm tra cache...")
            weather_from_cache = db.get_recent_weather(location['id'], minutes=30)

        if weather_from_cache:
            # 2. Nếu có cache hợp lệ -> Hiển thị
            print("✅ Dữ liệu mới! Lấy từ cache thành công.")
            display_weather(weather_from_cache['data_json'], source="Cache")
        else:
            # 3. Nếu không có cache -> Gọi API
            print("📡 Không có dữ liệu cache hợp lệ. Đang gọi API...")
            api_query = f"{city_name},{country_code}"
            new_weather_data = api.get_weather_data(api_query)

            if new_weather_data:
                # 4. Lưu kết quả mới vào CSDL
                location_id = location['id'] if location else None

                if not location_id:
                    print("✨ Địa điểm mới, đang thêm vào CSDL...")
                    coords = new_weather_data.get('coord', {})
                    location_id = db.add_location(
                        new_weather_data.get('name'),
                        new_weather_data.get('sys', {}).get('country'),
                        coords.get('lat'),
                        coords.get('lon')
                    )

                if location_id:
                    db.add_weather_cache(location_id, new_weather_data)
                    print("💾 Đã lưu dữ liệu mới vào cache.")

                display_weather(new_weather_data, source="API")
            else:
                print(f"❌ Không thể tìm thấy thông tin thời tiết cho '{city_input}'. Vui lòng thử lại.")

        time.sleep(1)

if __name__ == '__main__':
    main()