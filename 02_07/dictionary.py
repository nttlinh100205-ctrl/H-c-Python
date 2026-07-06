person ={"name":"linh","age":"20"}
product = {"id":1,"name":"Laptop","price":2000}
mixed={"name":"linh","age":20,"is_student":True}
empty = {}
print(person["name"])
person.update({"age":21}) # thay doi thong tin
print(person)
person ["email"] = "linh@gmail.com" # them 
person.pop("age") # xoa theo key
del person ["name"] # xoa key
# Duyệt dictionary
# duyệt key
for key in person:
    print(key)
# duyệt value
for value in person.values():
    print(value)
#duyet ca key - value
for key, value in person.items():
    print(key, value)