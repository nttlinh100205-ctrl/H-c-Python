try:
    f=open("test.py","r")
except FileNotFoundError:
    print("File khong ton tai")
else:
    print("Doc file thành công")
    content=f.read()
    print("Noi dung file :")
    print(content)
    f.close()
finally:
    print("Ket thuc")