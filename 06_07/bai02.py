# chia 2 số a và b dùng try-except bắt lỗi ValueError( nếu nhập chữ) và ZeroDivisionError( nếu chia cho 0)
while True:
    try:
        a_input = input("Vui long nhap so a:")
        b_input = input("Vui long nhap so b:")
        a = float(a_input)
        b = float(b_input)
        result = a/b
        print(f"Ket qua {a} chia {b} la : {result}")
        break
    except ValueError:
        print("LOI: Vui long nhap mot so hop le cho a va b.")
    except ZeroDivisionError:
        print("LOI: Khong the chia cho 0. Vui long nhap so b khac 0.")
