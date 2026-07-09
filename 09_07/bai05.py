import logging
logging.basicConfig(
    filename="bai05.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def tinh_bmi():
    while True:
        try:
            can_nang = float(input("Nhập cân nặng (kg): "))
            chieu_cao = float(input("Nhập chiều cao (m): "))
            if chieu_cao == 0:
                raise ZeroDivisionError
            break
        except ValueError:
            logging.error("Lỗi: Vui lòng nhập các giá trị hợp lệ!")
            print("Vui lòng nhập các giá trị hợp lệ!")
        except ZeroDivisionError:
            logging.error("Lỗi: Chiều cao không thể bằng 0!")
            print("Chiều cao không thể bằng 0!")

    bmi = can_nang / (chieu_cao ** 2)
    print(f"Chỉ số BMI của bạn là: {bmi:.2f}")

    if bmi < 18.5:
        return "Thiếu cân"
    elif bmi < 25:
        return "Bình thường"
    elif bmi < 30:
        return "Thừa cân"
    else:
        return "Béo phì"


if __name__ == "__main__":
    ket_qua = tinh_bmi()
    print(ket_qua)

