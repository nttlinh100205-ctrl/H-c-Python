while True:
    try:
        age_input = input("Vui long nhap tuoi cua ban:")
        age = int(age_input)
        if age < 0:
            print("Tuoi khong hop le. Vui long nhap so duong.")
        else:
            print(f"Ban {age} tuoi")
            break
    except ValueError:
         print("LOI: Vui long nhap mot so nguyen hop le cho tuoi.")
