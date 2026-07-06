# mở file và đọc 1 file do người dùng nhập. Dùng 1 khối except để bắt lỗi FileNotFoundError (file không tồn tại) và PermissionError (không có quyền truy cập file)
try:
    
    file_name = input("Nhap ten file muon doc:")
    with open(file_name,"r") as f:
        content = f.read()
        print(content)
except (FileNotFoundError, PermissionError) as e:
    print(f"Loi khi mo file: {e}")