


import getpass

from .Database import database, User
from .auth import hash_password, Role
from .logger import logger

database.create_tables()
def create_admin(username: str, password: str) -> None:
    if len(password) < 6:
        print(" Mật khẩu phải có ít nhất 6 ký tự.")
        return

    db = database.get_session()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"  Tài khoản '{username}' đã tồn tại (role={existing.role}). Bỏ qua.")
            return

        admin = User(
            username=username.strip(),
            hashed_password=hash_password(password),
            role=Role.ADMIN,
            employee_id=None,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        logger.info(f"Đã bootstrap tài khoản Admin '{username}'")
        print(f" Đã tạo tài khoản Admin '{username}' thành công.")
    except Exception as e:
        db.rollback()
        print(f" Lỗi khi tạo Admin: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=== Tạo tài khoản Admin đầu tiên cho HR API ===")
    username = input("Username: ").strip()
    password = getpass.getpass("Password (ẩn khi gõ): ")
    create_admin(username, password)