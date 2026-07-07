# cú pháp
fruits=["táo","cam","chuối"]
numbers=[1,2,3,4,5]
mixed=[1,"lan",True]
empty=[] # list rỗng
# truy cập phần tử
print(fruits[0])
print(fruits[-1]) #chuối
# thay đổi phần tủ
numbers[1]=10
print(numbers)
# thêm xoá phần tử
#thêm vào cuối
fruits.append("dưa hấu")
# thêm vị trí cố định
fruits.insert(1,"nho")
print(fruits)
# xoá theo giá trị
numbers.remove(1)
print(numbers)
# xoá theo index
fruits.pop(3)
print(fruits)
