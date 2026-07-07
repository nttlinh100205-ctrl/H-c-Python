import logging
from pathlib import Path

# Cấu hình log
logging.basicConfig(
    level=logging.INFO,
    filename="BT.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def doc_file():
    file_name = input("Nhập tên file muốn đọc: ")
    duong_dan_file = Path(__file__).parent / file_name
    try:
       with open(duong_dan_file,'r',encoding='utf-8') as f:
           content = f.read()
           print(content)
           logging.info(f"Đọc file thành công: {file_name}")
    except FileNotFoundError:
        logging.warning(f"Lỗi khi mở file: {file_name}")
        print(f"Lỗi: File '{file_name}' không tồn tại.")
    except PermissionError:
        logging.warning(f"Lỗi khi mở file: {file_name}")
        print(f"Lỗi: Không có quyền truy cập file '{file_name}'.")
doc_file()