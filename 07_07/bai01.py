import logging
logging.basicConfig (
    level=logging.INFO,
    filename="test.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)
while True:
    try:
        a=int(input("Nhập a: "))
        b=int(input("Nhập b: "))
        c=a/b
        print("Kết quả:",c)
        logging.info(f"Chia thành công :{a}/{b}={c}")
        break
    except ValueError as e:
        logging.exception("Loi nhạp dữ liệu")
        print("Lỗi: Vui lòng nhập số nguyên hợp lệ.")
    except ZeroDivisionError as e:
        logging.exception("Lỗi chia cho 0")
        print("Lỗi: Không thể chia cho 0.")
        