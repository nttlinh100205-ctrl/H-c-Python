# đoán số
import random
random_number = random.randint(1, 50)
luot_doan=5
for i in range(1, luot_doan + 1):
    try:
        num=int(input("Nhập số đoán (1-50): "))
    except ValueError:
        print("Vui lòng nhập một số nguyên!")
        continue
    if num < random_number:
        print("Số ngẫu nhiên lớn hơn")
    elif num > random_number:
        print("Số ngẫu nhiên nhỏ hơn")
    else:
        print("Chúc mừng đoán đúng số ngẫu nhiên là:", random_number)
        break
else:
    print("Hết lượt đoán! Số ngẫu nhiên là:", random_number)