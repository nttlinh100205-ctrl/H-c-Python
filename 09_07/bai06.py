# tài khoản ngân hàng (OOP)
class TaiKhoanNganHang:
    def __init__(self, stk:str, ten_chu : str, so_du:float=0.0):
        self.stk = stk
        self.ten_chu = ten_chu.title().strip()
        self.so_du = so_du
    def nap_tien(self, so_tien:float):
        if so_tien <=0:
            print("Số tiền cần nạp phải lớn hơn 0")
        else:
            self.so_du +=so_tien
            print(f"Đã nạp thành công : +{so_tien} vào tài khoản {self.stk}. Số dư hiện tại: {self.so_du}")
    def rut_tien(self,so_tien:float):
        if so_tien <=0:
            print("Số tiền cần rút phải lớn hơn 0")
        elif so_tien > self.so_du:
            print(f"Số dư không đủ để rút {so_tien}. Số dư hiện tại: {self.so_du}")
        else:
            self.so_du -=so_tien
            print(f"Đã rút thành công : -{so_tien} từ tài khoản {self.stk}. Số dư hiện tại: {self.so_du}")
    def kiem_tra_so_du(self):
        print("-"*20)
        print(f"THONG TIN TAI KHOAN : {self.stk}")
        print(f"CHỦ TÀI KHOẢN :{self.ten_chu}")
        print(f"Số dư hiện tại của tài khoản {self.stk} là: {self.so_du}")
        print("-"*20)
if __name__ == "__main__":
    print("Khởi tạo tài khoản")
    tk1=TaiKhoanNganHang("123456789","Nguyen Van A",1000)
    tk1.kiem_tra_so_du()
    tk1.nap_tien(500)
    tk1.kiem_tra_so_du()    
    tk1.rut_tien(200)
    tk1.kiem_tra_so_du()
