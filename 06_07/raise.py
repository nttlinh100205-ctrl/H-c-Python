#Ví dụ trong cuộc sống: Bạn đi khám bệnh, bác sĩ (hàm) kiểm tra nhiệt độ (dữ liệu) của bạn. Nếu nhiệt độ trên 38°C (điều kiện không hợp lệ), bác sĩ sẽ "raise" một cảnh báo "Bệnh nhân bị sốt!" để y tá xử lý.
def set_age(age):
    if not isinstance(age, int):
        raise TypeError("Tuoi phai la so nguyen")
    if age < 0:
        raise ValueError("Tuoi khong the la 1 số âm")
    print(f"Tuoi da duoc dat la : {age}")
try:
    set_age(-5)
except(TypeError, ValueError) as e:
    print(f"Loi khi dat tuoi : {e}")
    