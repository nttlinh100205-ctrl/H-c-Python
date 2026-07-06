# giai va bien luan pt bac 2
import math
a = float(input("Nhap a:"))
b = float(input("Nhap b:"))
c = float(input("Nhap c:"))
delta = b*2 -4*a*c
if delta<0:
    print("Phuong trinh vo nghiem")
elif delta == 0:
    print("Phuong trinh co nghiem kep=", -b/(2*a))
else:
    x1=(-b + math.sqrt(delta))/(2*a)
    x2=(-b - math.sqrt(delta))/(2*a)    
    print("Phuong trinh co 2 nghiem phan biet: x1=",x1," va x2=",x2)