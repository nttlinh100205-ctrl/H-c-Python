# VD bắt nhiều loại exception trong cùng 1 khối except
try:
    my_dict = {"name":"Linh"}
    key = input("Nhap key muốn truy cập:")
    print(my_dict[key])
except (KeyError, IndexError) as e:
    print(f"Lỗi truy cập dữ liệu: {e}")

