def nhap_tuoi():
    while True:
        try:
            age=int(input("Vui long nhap tuoi:"))
            if age <0:
                print("Tuoi khong hop le. Nhap so duong")
            else:
                return age
        except ValueError:
            print("Loi: Vui long nhap so nguyen")
def hien_thi_tuoi(age):
    print(f"Ban {age} tuoi")
def chuong_trinh_chinh():
    age=nhap_tuoi()
    hien_thi_tuoi(age)
chuong_trinh_chinh()