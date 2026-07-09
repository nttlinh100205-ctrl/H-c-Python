# Quản lý nhân sự (OOP)
class Department:
    def __init__(self, ten_phong: str):
        self.ten_phong = ten_phong
        self.danh_sach_nv = []

    def them_nhan_vien(self, nhan_vien):
        if nhan_vien not in self.danh_sach_nv:
            self.danh_sach_nv.append(nhan_vien)

    def hien_thi_thanh_vien(self):
        print(f"\n NHÂN VIÊN PHÒNG: {self.ten_phong.upper()}")
        if not self.danh_sach_nv:
            print("  (Chưa có nhân viên nào)")
        for nv in self.danh_sach_nv:
            print(f"  - [{nv.manv}] {nv.hoten}")

class LeaveRequest:
    def __init__(self, manv: str, ngay_nghi: str, ly_do: str):
        self.manv = manv
        self.ngay_nghi = ngay_nghi
        self.ly_do = ly_do
        self.status = "Chờ duyệt" 


class Person:
    def __init__(self, hoten: str, tuoi: int):
        self.hoten = hoten.title().strip()
        self.tuoi = tuoi

    def hien_thi(self):
        print(f"Họ và tên: {self.hoten}")
        print(f"Tuổi: {self.tuoi}")

class Employee(Person):
  
    def __init__(self, hoten: str, tuoi: int, manv: str, phong_ban: Department, luong: float):
        super().__init__(hoten, tuoi)
        self.manv = manv
        self.phong_ban = phong_ban
        self.luong = luong
        self.danh_sach_don = []  

        self.phong_ban.them_nhan_vien(self)

    def tinh_luong(self) -> float:
        return self.luong

    def cap_nhat_moi(self, phong_ban_moi: Department):
        self.phong_ban = phong_ban_moi
        self.phong_ban.them_nhan_vien(self)
        print(f"Đã chuyển nhân viên {self.hoten} sang phòng: {self.phong_ban.ten_phong}")

    def tang_luong(self, tien_tang: float):
        if tien_tang > 0:
            self.luong += tien_tang
            print(f"{self.hoten} đã được tăng lương thêm {tien_tang:,.0f} VNĐ")
        else:
            print("Số tiền không hợp lệ")

    def xin_nghi(self, ngay_nghi: str, ly_do: str) -> LeaveRequest:
        don_moi = LeaveRequest(self.manv, ngay_nghi, ly_do)
        self.danh_sach_don.append(don_moi)
        print(f" Đã tạo đơn xin nghỉ ngày {ngay_nghi}. (Trạng thái: {don_moi.status})")
        return don_moi

    def xem_lich_su_nghi(self):
        print(f" Lịch sử xin nghỉ của {self.hoten}:")
        if not self.danh_sach_don:
            print("  (Chưa có đơn xin nghỉ nào)")
        for don in self.danh_sach_don:
            print(f"  - Ngày: {don.ngay_nghi} | Lý do: {don.ly_do} | Trạng thái: {don.status}")

    def hien_thi(self):
        print(f"Mã nhân viên: {self.manv}")
        super().hien_thi()
        print(f"Phòng ban: {self.phong_ban.ten_phong}")
        print(f"Lương: {self.tinh_luong():,.0f} VNĐ")

class Manager(Employee):

    def __init__(self, hoten: str, tuoi: int, manv: str, phong_ban: Department, luong: float, phu_cap_ql: float):
        super().__init__(hoten, tuoi, manv, phong_ban, luong)
        self.phu_cap_ql = phu_cap_ql

    def tinh_luong(self):
        return super().tinh_luong() + self.phu_cap_ql

  
    def duyet_don(self, don_xin_nghi: LeaveRequest, xac_nhan: bool):
        if don_xin_nghi.status != "Chờ duyệt":
            print(f" Đơn của {don_xin_nghi.manv} đã được xử lý trước đó!")
            return

        if xac_nhan:
            don_xin_nghi.status = "Đã duyệt"
            print(f" Quản lý {self.hoten} ĐÃ DUYỆT đơn ngày {don_xin_nghi.ngay_nghi} của NV {don_xin_nghi.manv}")
        else:
            don_xin_nghi.status = "Bị từ chối"
            print(f" Quản lý {self.hoten} TỪ CHỐI đơn ngày {don_xin_nghi.ngay_nghi} của NV {don_xin_nghi.manv}")

if __name__ == "__main__":
   
    pb2 = Department("PB02")
    pb7 = Department("PB07")
    pb_gs = Department("Phòng giám sát")
    pb_ql = Department("Phòng Ban Quản Lý")

    nv1 = Employee("Nguyễn Văn Linh", 45, "NV01", pb2, 5000000)
    nv2 = Employee("Bui Van Lam", 23, "NV02", pb7, 3500000)
    nv3 = Employee("ABC", 26, "NV03", pb_gs, 7000000)
    ql1 = Manager("Nguyen Cong Đạt", 50, "QL01", pb_ql, 15000000, 2000000)

    he_thong_nhan_vien = {nv1.manv: nv1, nv2.manv: nv2, nv3.manv: nv3, ql1.manv: ql1}
    he_thong_don_nghi = []  # Nơi chứa các đơn đẩy lên để Quản lý duyệt

    while True:
        print("\n" + "="*30)
        print("1. Hiển thị toàn bộ nhân viên")
        print("2. Xem danh sách theo phòng ban")
        print("3. Nhân viên: Xin nghỉ")
        print("4. Nhân viên: Xem trạng thái đơn")
        print("5. Quản lý: Duyệt đơn xin nghỉ")
        print("0. Thoát")
        print("="*30)

        chon = input("Nhập lựa chọn: ").strip()

        if chon == "1":
            for nv in he_thong_nhan_vien.values():
                print("-" * 25)
                nv.hien_thi()

        elif chon == "2":
            pb2.hien_thi_thanh_vien()
            pb7.hien_thi_thanh_vien()
            pb_gs.hien_thi_thanh_vien()
            pb_ql.hien_thi_thanh_vien()

        elif chon == "3":
            ma = input("Nhập mã nhân viên của bạn: ").upper()
            if ma in he_thong_nhan_vien:
                ngay = input("Nhập ngày nghỉ (DD/MM): ")
                lydo = input("Lý do: ")
                don = he_thong_nhan_vien[ma].xin_nghi(ngay, lydo)
                he_thong_don_nghi.append(don)
            else:
                print(" Không tìm thấy mã nhân viên!")

        elif chon == "4":
            ma = input("Nhập mã nhân viên: ").upper()
            if ma in he_thong_nhan_vien:
                he_thong_nhan_vien[ma].xem_lich_su_nghi()
            else:
                print(" Không tìm thấy mã nhân viên!")

        elif chon == "5":
            don_cho = [d for d in he_thong_don_nghi if d.status == "Chờ duyệt"]
            if not don_cho:
                print(" Không có đơn nào cần duyệt!")
                continue
            
            print("\n DANH SÁCH ĐƠN CHỜ DUYỆT:")
            for i, d in enumerate(don_cho):
                print(f"[{i}] NV: {d.manv} | Ngày: {d.ngay_nghi} | Lý do: {d.ly_do}")
            
            try:
                stt = int(input("Chọn số ID đơn muốn xử lý: "))
                if 0 <= stt < len(don_cho):
                    action = input("Duyệt đơn này? (y: Có / n: Từ chối): ").lower()
                    if action == 'y':
                        ql1.duyet_don(don_cho[stt], True)
                    elif action == 'n':
                        ql1.duyet_don(don_cho[stt], False)
                else:
                    print(" ID đơn không hợp lệ!")
            except ValueError:
                print(" Vui lòng nhập số!")

        elif chon == "0":
            print("Thoát chương trình. Tạm biệt!")
            break
        else:
            print(" Lựa chọn sai, vui lòng nhập lại!")