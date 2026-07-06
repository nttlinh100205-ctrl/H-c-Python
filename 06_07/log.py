import logging

logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def ham_xu_ly_chinh():
    while True:
        try:
            age_input = input("Vui long nhap tuoi cua ban: ")
            age = int(age_input)

            if age < 0:
                logging.error("Tuoi ko hop le")
                print("Tuoi khong hop le. Vui long nhap so duong.")
            else:
                print(f"Ban {age} tuoi")
                break   

        except ValueError:
            logging.error("Loi nhap lai so")
            print("LOI: Vui long nhap mot so nguyen hop le cho tuoi.")

        except Exception:
            logging.exception("Da xay ra loi trong qua trinh thuc thi:")
            print("Ung dung gap loi, vui long kiem tra file app.log.")
            break

ham_xu_ly_chinh()