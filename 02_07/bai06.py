# tro choi doan so
import random
so_ngau_nhien = random.randint(1,100)
while True:
    try:  
        so_nhap =int(input("Nhap so doan:"))
    except ValueError:
        print("Vui long nhap mot so nguyen!")
        continue
    if so_nhap < so_ngau_nhien:
        print("So ngau nhien lon hon")
    elif so_nhap > so_ngau_nhien:
        print("So ngau nhien nho hon")
    else:
        print("Chuc mưng doan dung so ngau nhien la:",so_ngau_nhien)
        break
