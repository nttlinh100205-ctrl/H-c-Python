from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any, List
from datetime import date, datetime
from enum import Enum


class ResponseSuccess(BaseModel):
    message: str = Field(..., example="Thao tác thành công")
    data: Optional[Any] = None
    code: int = 200

class HealthCheck(BaseModel):
    status: str
    timestamp: str
    database: str


class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=100, example="Phòng Kỹ thuật")
    description: Optional[str] = Field(None, max_length=255, example="Chịu trách nhiệm phát triển phần mềm")

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        from_attributes = True

class DepartmentUpdate(BaseModel): 
    name: Optional[str] = Field(None, max_length=100, example="Tên phòng ban mới")
    description: Optional[str] = Field(None, max_length=255, example="Mô tả sửa đổi")


class EmployeeBase(BaseModel):
    fullname: str = Field(..., max_length=150, example="Nguyễn Văn A")
    email: Optional[EmailStr] = Field(None, example="nguyenvana@gmail.com")
    phone: Optional[str] = Field(None, max_length=20, example="0987654321")
    position: Optional[str] = Field(None, max_length=100, example="Lập trình viên Backend")
    salary: Optional[float] = Field(None, example=15000000.0)
    hire_date: Optional[date] = Field(None, example="2026-07-16")
    is_active: Optional[bool] = Field(True, example=True)
    department_id: Optional[int] = Field(None, example=1)

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int
    department: Optional[DepartmentResponse] = None 

    class Config:
        from_attributes = True

class EmployeeUpdate(BaseModel):
    fullname: Optional[str] = Field(None, max_length=150, example="Nguyễn Văn A")
    email: Optional[EmailStr] = Field(None, example="nguyenvana@gmail.com")
    phone: Optional[str] = Field(None, max_length=20, example="0987654321")
    position: Optional[str] = Field(None, max_length=100, example="Lập trình viên Backend")
    department_id: Optional[int] = Field(None, example=1)

class EmployeeSelfUpdate(BaseModel):
    fullname: Optional[str] = Field(None, max_length=150, example="Nguyễn Văn A")
    email: Optional[EmailStr] = Field(None, example="nguyenvana@gmail.com")
    phone: Optional[str] = Field(None, max_length=20, example="0987654321")


class PaginationMeta(BaseModel):
    total: int = Field(..., example=42)
    skip: int = Field(..., example=0)
    limit: int = Field(..., example=10)
    total_pages: int = Field(..., example=5)
    page: int = Field(..., example=1)

class DepartmentListResponse(BaseModel):
    items: List[DepartmentResponse]
    meta: PaginationMeta

class EmployeeListResponse(BaseModel):
    items: List[EmployeeResponse]
    meta: PaginationMeta


class RoleEnum(str, Enum):
    admin = "admin"
    employee = "employee"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="nguyenvana")
    password: str = Field(..., min_length=6, example="matkhau123")
    employee_id: Optional[int] = Field(None, example=1)

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    employee_id: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str = Field(..., example="nguyenvana")
    password: str = Field(..., example="matkhau123")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    expires_in_minutes: int


class SalaryResponse(BaseModel):
    ma_nhan_vien: int = Field(..., description="Mã nhân viên")
    ho_ten: str = Field(..., description="Họ và tên nhân viên")
    nam: int = Field(..., description="Năm tính lương")
    thang: int = Field(..., description="Tháng tính lương")
    luong_gross_thoa_thuan: float = Field(..., description="Lương gross thỏa thuận")
    so_ngay_cong_chuan: int = Field(..., description="Số ngày công chuẩn trong tháng")
    so_ngay_tinh_luong_thuc_te: int = Field(..., description="Số ngày tính lương thực tế")
    so_ngay_nghi_co_luong: int = Field(..., description="Số ngày nghỉ có lương đã duyệt")
    so_ngay_nghi_khong_luong: int = Field(..., description="Số ngày nghỉ không lương đã duyệt")
    luong_gross_thuc_te: float = Field(..., description="Lương gross tính theo công thực tế")
    tien_bao_hiem_trich_nop: float = Field(..., description="Tiền bảo hiểm đóng (10.5%)")
    thu_nhap_chiu_thue: float = Field(..., description="Thu nhập chịu thuế")
    thue_tncn_phai_nop: float = Field(..., description="Thuế TNCN phải nộp")
    luong_net_thuc_nhan: float = Field(..., description="Lương thực nhận (net)")


class LeaveTypeEnum(str, Enum):
    PAID = "paid"
    UNPAID = "unpaid"

class LeaveStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class LeaveRequestCreate(BaseModel):
    start_date: date = Field(..., description="Ngày bắt đầu nghỉ")
    end_date: date = Field(..., description="Ngày kết thúc nghỉ")
    leave_type: LeaveTypeEnum = Field(..., description="Loại nghỉ (có lương / không lương)")
    reason: Optional[str] = Field(None, max_length=255, description="Lý do nghỉ")

class LeaveRequestStatusUpdate(BaseModel):
    status: LeaveStatusEnum

class LeaveRequestResponse(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    leave_type: str
    reason: Optional[str]
    status: str

    class Config:
        from_attributes = True