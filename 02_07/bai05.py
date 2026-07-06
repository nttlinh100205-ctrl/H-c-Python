# in bang cuu chuong
n =int(input("Nhap n:"))
if 1<= n <=9:
    print(" Bang cuu chuong",n)
    for i in range(1,11):
        print(f"{n} x {i}={n * i}")
else:
    print("Nhap tu 1 den 9")