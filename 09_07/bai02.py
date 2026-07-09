password = input("Nhap pass:")
loi = []
if len(password) < 8:
    loi.append("Mat khau phai co it nhat 8 ky tu"   )
if not any(char.islower() for char in password):
    loi.append("Mat khau phai co it nhat 1 chu thuong")
if not any(char.isupper() for char in password):
    loi.append("Mat khau phai co it nhat 1 chu hoa")
if loi:
    for error in loi:
        print(error)
else:
    print("Mat khau hop le")
