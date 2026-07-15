from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = {}
SECRET_KEY = "bjnk-vjbk-hj"
ALGORITHM = "HS256"

class User(BaseModel):
    username: str
    password: str


def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    Hàm để xác minh JWT token từ Header Authorization
    Cách dùng: Authorization: Bearer <TOKEN>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header bị thiếu")
  
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authorization header không hợp lệ. Định dạng: Bearer <token>")
    
    token = parts[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
        return {"username": username}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")


@app.post("/register")
def register(user: User):
    """Đăng ký tài khoản mới"""
    if user.username in db:
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại")
    
    hashed_pwd = pwd_context.hash(user.password)
    db[user.username] = {
        "username": user.username,
        "password": hashed_pwd
    }
    return {"message": "Đăng kí thành công"}

@app.post("/login")
def login(user: User):
    
    if user.username not in db:
        raise HTTPException(status_code=401, detail="Tên đăng nhập or mật khẩu ko chính xác")
    
    db_user = db[user.username]
    is_verified = pwd_context.verify(user.password, db_user["password"])
    
    if not is_verified:
        raise HTTPException(status_code=401, detail="Tên đăng nhập or mật khẩu ko chính xác")
    
    # Tạo JWT token
    time_end = datetime.utcnow() + timedelta(minutes=30)
    payload = {
        "sub": user.username,
        "exp": time_end
    }
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "message": "Đăng nhập thành công",
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/")
def root():
    return {"message": "Chào mừng đến API"}

@app.get("/profile")
def get_profile(token_data: dict = Depends(verify_token)):
    """
    Lấy thông tin profile
    
    Cách dùng:
    Authorization: Bearer <JWT_TOKEN>
    """
    username = token_data["username"]
    return {
        "message": "Thành công",
        "username": username,
        "user_info": db[username]
    }

@app.get("/protected-data")
def get_protected_data(token_data: dict = Depends(verify_token)):

    return {
        "message": "Dữ liệu bảo vệ",
        "username": token_data["username"],
        "data": "Đây là dữ liệu chỉ user đã login mới thấy"
    }

@app.get("/me")
def get_me(token_data: dict = Depends(verify_token)):
    """
    Lấy thông tin user hiện tại
    
    Cách dùng:
    Authorization: Bearer <JWT_TOKEN>
    """
    username = token_data["username"]
    user = db[username]
    return {
        "username": user["username"],
        # Không trả password
    }

@app.put("/update-profile")
def update_profile(token_data: dict = Depends(verify_token), new_info: dict = None):

    username = token_data["username"]
    if new_info:
        db[username].update(new_info)
    return {
        "message": "Cập nhật thành công",
        "user_info": db[username]
    }

