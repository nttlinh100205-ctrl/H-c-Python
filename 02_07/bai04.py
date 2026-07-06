# tinh tong tu 1 den n 
n = int(input("Nhap n:"))
sum = 0
for i in range(1,n+1,):
    if i %2 ==0:
       sum += i # sum= sum+i
print("Tong tu 1 den n =", sum)