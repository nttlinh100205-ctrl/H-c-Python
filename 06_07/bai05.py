# danh sách SV bắt lỗi
import logging
logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
students = ["An","Binh","Cuong"]
while True:
    try:
        vi_tri=int(input("Nhap vị trí cần xem:"))
        if vi_tri < 0:
           raise IndexError
        print("Học sinh tại vị trí đó :", students[vi_tri])
        break
    except IndexError:
        logging.error("Vị trí nhập nằm ngoài phạm vi")
        print("Lỗi: Vị trí nhập nằm ngoài phạm vi danh sách")
    except ValueError:
        logging.error("Nhap mot so nguyen")
        print("Lỗi: Vui lòng nhập 1 số nguyên ")

        
