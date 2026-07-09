# quản lý nhân sự (kế thừa)
class Person:
    def __init__(self, hoten:str, tuoi:int):
        self.hoten=hoten.title().strip()
        self.tuoi=tuoi
    def hien_thi(self):
        print(f"Họ và tên: {self.hoten}")
        print(f"Tuổi: {self.tuoi}")
class Employee(Person):
    def __init__(self, hoten:str,tuoi:int,manv:str,phong_ban:str,luong : float):
        super().__init__(hoten,tuoi)
        self.manv=manv
        self.phong_ban=phong_ban
        self.luong=luong
    def tinh_luong(self)->float:
        return self.luong
    def cap_nhat_moi(self,phong_ban_moi:str):
        self.phong_ban = phong_ban_moi
        print(f"Đã chuyển nhân viên {self.hoten} sang phòng : {self.phong_ban}")

    def tang_luong(self, tien_tang:float):
        if tien_tang > 0:
            self.luong += tien_tang
            print(f"{self.hoten} đã được tăng lương thêm {tien_tang}")
        else:
            print("Số tiền không hợp lệ")

    def hien_thi(self):
        print(f"Mã nhân viên:{self.manv}")
        super().hien_thi()
        print(f"Phòng ban :{self.phong_ban}")
        print(f"Lương: {self.tinh_luong()}")
class Manager(Employee):
    def __init__(self,hoten:str, tuoi:int,manv:str,phong_ban:str,luong : float,phu_cap_ql:str):
        super().__init__(hoten,tuoi,manv,phong_ban,luong)
        self.phu_cap_ql=phu_cap_ql
    def tinh_luong(self):
        return super().tinh_luong() + self.phu_cap_ql    
if __name__=="__main__":
    print("Khởi tạo nhân viên và quản lý")
    nv1=Employee("Nguyễn Văn Linh",45,"NV01","PB02",5000000)
    nv2=Employee("Bui Van Lam",23,"NV02","PB07",3500000)
    nv3=Employee("ABC",26,"NV03","Phòng giám sát",7000000)
    ql1=Manager("Nguyen Cong Đạt",50,"QL01","Phòng Ban Quản Lý",15000000,2000000)
    print("-"*40)
    nv1.hien_thi()
    print("-"*40)
    nv2.hien_thi()
    print("-"*40)
    nv3.hien_thi()
    print("-"*40)
    ql1.hien_thi()
    print("-"*40)
    print("CHYỂN PHÒNG BAN")
    nv1.cap_nhat_moi("Phòng nhân sự")
    print("-"*40)
    nv1.hien_thi()
    print("-"*40)
    print("TĂNG LƯƠNG")
    nv2.tang_luong(1000000)
    print("-"*40)
    nv2.hien_thi()
    print("-"*40)




