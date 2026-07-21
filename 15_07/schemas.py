from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any, List
from datetime import date, datetime
from enum import Enum



class ResponseSuccess(BaseModel):
    """Schema chuẩn cho các API trả về thành công trong main.py"""
    message: str = Field(..., example="Thao tác thành công")
    data: Optional[Any] = None
    code: int = 200

class HealthCheck(BaseModel):
    """Schema cho API kiểm tra trạng thái hệ thống (/health)"""
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



class PaginationMeta(BaseModel):
    """Thông tin phân trang, đính kèm trong các API trả về danh sách"""
    total: int = Field(..., example=42, description="Tổng số bản ghi thỏa điều kiện lọc")
    skip: int = Field(..., example=0, description="Số bản ghi đã bỏ qua")
    limit: int = Field(..., example=10, description="Số bản ghi tối đa mỗi trang")
    total_pages: int = Field(..., example=5, description="Tổng số trang")
    page: int = Field(..., example=1, description="Trang hiện tại (bắt đầu từ 1)")


class DepartmentListResponse(BaseModel):
    """Dữ liệu trả về khi gọi GET /departments (có tìm kiếm/phân trang)"""
    items: List[DepartmentResponse]
    meta: PaginationMeta


class EmployeeListResponse(BaseModel):
    """Dữ liệu trả về khi gọi GET /employees (có tìm kiếm/lọc/phân trang)"""
    items: List[EmployeeResponse]
    meta: PaginationMeta




class RoleEnum(str, Enum):
    admin = "admin"
    employee = "employee"


class UserCreate(BaseModel):
    """Dữ liệu đầu vào khi đăng ký tài khoản (POST /auth/register).
    Lưu ý: API register công khai LUÔN tạo role=employee, không cho tự phong Admin.
    """
    username: str = Field(..., min_length=3, max_length=50, example="nguyenvana")
    password: str = Field(..., min_length=6, example="matkhau123")
    employee_id: Optional[int] = Field(
        None, example=1,
        description="Liên kết tài khoản với 1 nhân viên đã có trong hệ thống (để tự xem lương/thông tin của mình)"
    )


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
    """Kết quả tính lương chi tiết cho 1 nhân viên (chỉ Admin xem được)"""
    employee_id: int
    fullname: str
    gross_salary: float = Field(..., description="Lương gross (thỏa thuận)")
    insurance_amount: float = Field(..., description="Bảo hiểm người lao động đóng (10.5%)")
    dependents: int = Field(..., description="Số người phụ thuộc")
    personal_deduction: float = Field(..., description="Giảm trừ bản thân")
    dependent_deduction: float = Field(..., description="Giảm trừ người phụ thuộc")
    taxable_income: float = Field(..., description="Thu nhập chịu thuế")
    tax_amount: float = Field(..., description="Thuế TNCN phải nộp")
    net_salary: float = Field(..., description="Lương thực nhận (net)")