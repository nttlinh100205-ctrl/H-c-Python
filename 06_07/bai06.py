# quản lý TKNH 
import logging

logging.basicConfig(
    filename="giao_dich.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
so_du=0
def nap_tien():
    global so_du
    try:
        so_tien=float(input("Nhập số tiền muốn nạp:"))
        if so_tien <0:
            raise ValueError("Số tiền không được âm")
        so_du +=so_tien
        print(f"Nạp tiền thành công:{so_du}")
    except ValueError as e:
        logging.error("Lỗi nạp tiền")
        print("Lỗi vui lòng nhập số tiền hợp lệ")
def rut_tien():
    global so_du
    try:
        so_tien=float(input("Nhập số tiền cần rút:"))
        if so_tien <0:
            raise ValueError("Số tiền không được âm")
        if so_tien > so_du:
            raise Exception("Số dư không đủ")
        so_du -=so_tien
    except ValueError as e:
        logging.error("Lỗi rút tiền")
        print(f"Lỗi : Vui lòng nhập số tiền hợp lệ")
    except Exception as e:
        logging.error("Lỗi rút tiền ")
        print(f"Lỗi: {e}")
def xem_so_du():
    print(f"Số dư hiện tại :{so_du}")
while True:
    print("1.Nạp tiền")
    print("2.Rút tiền")
    print("3. Xem số dư")
    print("4. Thoát")
    choice =input("chọn chức năng  :")
    if choice == "1":
        nap_tien()
    elif choice == "2":
        rut_tien()
    elif choice == "3":
        xem_so_du()
    elif choice == "4":
        print("Thoát")
        break
    else:
        print("Lựa chọn ko hợp lệ")
        



