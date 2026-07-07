# cú pháp
person={"name":"linh","age":20}
products={1:"Iphone","price":1000}
print(person["name"])
# truy cập bằng key kp index như list
# thay đổi phần tử
#cách 1:
person["age"]=21 
print(person)
#cách 2:
person.update({"age":23})
print(person)
# cách 1 sẽ dùng cho cả thêm phần tử
person["email"]="linh@gmail.com"
print(person)
#xoá
person.pop("email") # xoá theo key
#del person["email"] # xoá key

