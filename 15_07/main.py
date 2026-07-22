from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
from math import ceil

from .logger import logger
from .config import config
from .Database import database, LeaveRequest

# Khởi tạo bảng nếu chưa có
database.create_tables()

from .schemas import (
    EmployeeCreate, DepartmentCreate, ResponseSuccess, DepartmentUpdate,
    EmployeeResponse, DepartmentResponse, HealthCheck,
    DepartmentListResponse, EmployeeListResponse, PaginationMeta,
    UserCreate, UserResponse, Token, SalaryResponse,
    EmployeeUpdate, EmployeeSelfUpdate,
    LeaveRequestCreate, LeaveRequestResponse, LeaveRequestStatusUpdate,
    LeaveStatusEnum, LeaveTypeEnum
)

from .services import (
    EmployeeService, DepartmentService, SalaryService, UserService, LeaveRequestService
)
from .auth import create_access_token, get_current_user, require_roles, Role
from .utils import ExcelExporter
from .exceptions import (
    DatabaseOperationError, DuplicateKeyError, ForeignKeyReferenceError,
    RequiredFieldError, DatabaseIntegrityError, InvalidDataTypeError,
    DatabaseConnectionError,
)

# --------------------------------------------------------------------------
# KHỞI TẠO CÁC ỨNG DỤNG FASTAPI
# --------------------------------------------------------------------------
app = FastAPI(
    title=config.API_TITLE,
    description="Hệ thống gốc - Quản lý Xác thực",
    version=config.API_VERSION,
    docs_url=None,
    openapi_url=None
)

admin_app = FastAPI(
    title="Admin API",
    description="Trang API dành riêng cho Quản trị viên (Nhân sự)",
    version=config.API_VERSION
)

employee_app = FastAPI(
    title="Employee API",
    description="Trang API dành riêng cho Nhân viên",
    version=config.API_VERSION
)


def build_pagination_meta(total: int, skip: int, limit: int) -> PaginationMeta:
    total_pages = ceil(total / limit) if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1
    return PaginationMeta(
        total=total, skip=skip, limit=limit, total_pages=total_pages, page=current_page
    )


def setup_exception_handlers(target_app: FastAPI):
    @target_app.exception_handler(DuplicateKeyError)
    async def duplicate_key_handler(request: Request, exc: DuplicateKeyError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @target_app.exception_handler(ForeignKeyReferenceError)
    async def foreign_key_handler(request: Request, exc: ForeignKeyReferenceError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @target_app.exception_handler(RequiredFieldError)
    async def required_field_handler(request: Request, exc: RequiredFieldError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @target_app.exception_handler(InvalidDataTypeError)
    async def invalid_data_type_handler(request: Request, exc: InvalidDataTypeError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @target_app.exception_handler(DatabaseConnectionError)
    async def db_connection_handler(request: Request, exc: DatabaseConnectionError):
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @target_app.exception_handler(DatabaseIntegrityError)
    async def db_integrity_handler(request: Request, exc: DatabaseIntegrityError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @target_app.exception_handler(DatabaseOperationError)
    async def db_operation_fallback_handler(request: Request, exc: DatabaseOperationError):
        return JSONResponse(
            status_code=500,
            content={"detail": config.get_message("server_error", error=str(exc))}
        )

setup_exception_handlers(app)
setup_exception_handlers(admin_app)
setup_exception_handlers(employee_app)


# --------------------------------------------------------------------------
# 1. SYSTEM & AUTHENTICATION (APP GỐC)
# --------------------------------------------------------------------------
@app.get("/", tags=["System"])
def root():
    return {"name": config.API_TITLE, "version": config.API_VERSION, "status": "running"}

@app.get("/health", response_model=HealthCheck, tags=["System"], summary="Kiểm tra trạng thái API")
def health_check():
    return {"status": "ok", "timestamp": str(datetime.now()), "database": "connected"}

def process_login(form_data: OAuth2PasswordRequestForm, db: Session):
    service = UserService(db)
    user = service.authenticate(form_data.username, form_data.password) 
    if not user:
        raise HTTPException(status_code=401, detail=config.get_message("invalid_credentials"))

    token = create_access_token(data={"sub": user.username, "role": user.role, "employee_id": user.employee_id})
    return Token(access_token=token, token_type="bearer", role=user.role, expires_in_minutes=config.JWT_EXPIRE_MINUTES)

@app.post("/auth/login", response_model=Token, tags=["Auth"], summary="Đăng nhập hệ thống")
def login_root(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    return process_login(form_data, db)


# --------------------------------------------------------------------------
# 2. ADMIN APP (QUẢN TRỊ VIÊN)
# --------------------------------------------------------------------------
@admin_app.post("/users", response_model=ResponseSuccess,dependencies=[Depends(require_roles(Role.ADMIN))], tags=["Accounts"], summary="Tạo tài khoản mới cho nhân viên")
def create_user(data: UserCreate, db: Session = Depends(database.get_db)):
    try:
        service = UserService(db)
        result = service.register(username=data.username, password=data.password, role=Role.EMPLOYEE, employee_id=data.employee_id)
        return ResponseSuccess(message="Đăng ký tài khoản thành công!", data=UserResponse.model_validate(result), code=201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@admin_app.post("/departments", response_model=ResponseSuccess, dependencies=[Depends(require_roles(Role.ADMIN))],tags=["Departments"], summary="Tạo phòng ban mới")
def create_department(data: DepartmentCreate, db: Session = Depends(database.get_db)):
    try:
        service = DepartmentService(db)
        result = service.create(data)
        return ResponseSuccess(message=config.get_message("create_department_success"), data=DepartmentResponse.model_validate(result), code=201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@admin_app.get("/departments", response_model=DepartmentListResponse, tags=["Departments"], summary="Lấy danh sách phòng ban")
def list_departments(
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(database.get_db),
    current_user = Depends(require_roles(Role.ADMIN))
):
    service = DepartmentService(db)
    items, total = service.get_all(search=search, skip=skip, limit=limit)
    return DepartmentListResponse(items=[DepartmentResponse.model_validate(item) for item in items], meta=build_pagination_meta(total, skip, limit))

@admin_app.put("/departments/{department_id}", tags=["Departments"],dependencies=[Depends(require_roles(Role.ADMIN))], summary="Sửa thông tin phòng ban")
def update_department(department_id: int, data: DepartmentUpdate, db: Session = Depends(database.get_db)):
    service = DepartmentService(db)
    return service.update_department(department_id, data)

@admin_app.delete("/departments/{department_id}", dependencies=[Depends(require_roles(Role.ADMIN))], tags=["Departments"], summary="Xóa phòng ban")
def delete_department(department_id: int, db: Session = Depends(database.get_db)):
    service = DepartmentService(db)
    return service.delete_department(department_id)

@admin_app.post("/employees", response_model=ResponseSuccess,dependencies=[Depends(require_roles(Role.ADMIN))], tags=["Employees"], summary="Tạo nhân viên mới")
def create_employee(data: EmployeeCreate, db: Session = Depends(database.get_db)):
    try:
        service = EmployeeService(db)
        result = service.create(data)
        return ResponseSuccess(message=config.get_message("create_employee_success", name=data.fullname), data=EmployeeResponse.model_validate(result), code=201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@admin_app.get("/employees", response_model=EmployeeListResponse, tags=["Employees"], summary="Lấy danh sách nhân viên")
def list_employees(
    search: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    min_salary: Optional[float] = Query(None, ge=0),
    max_salary: Optional[float] = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(database.get_db),
    current_user = Depends(require_roles(Role.ADMIN))
):
    service = EmployeeService(db)
    items, total = service.get_all(search=search, department_id=department_id, is_active=is_active, min_salary=min_salary, max_salary=max_salary, skip=skip, limit=limit)
    return EmployeeListResponse(items=[EmployeeResponse.model_validate(item) for item in items], meta=build_pagination_meta(total, skip, limit))

@admin_app.get("/employees/export-csv", tags=["Employees"], dependencies=[Depends(require_roles(Role.ADMIN))], summary="Xuất danh sách nhân viên ra Excel (.xlsx)")
def export_csv(db: Session = Depends(database.get_db)):
    try:
        service = EmployeeService(db)
        employees = service.export_to_csv()
        excel_data = ExcelExporter.export_employees(employees)
        excel_filename = config.CSV_FILENAME.rsplit(".", 1)[0] + ".xlsx"
        return StreamingResponse(excel_data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename={excel_filename}"})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@admin_app.get("/employees/{emp_id}", response_model=EmployeeResponse,dependencies=[Depends(require_roles(Role.ADMIN))], tags=["Employees"], summary="Xem chi tiết nhân viên")
def get_employee(emp_id: int, db: Session = Depends(database.get_db)):
    service = EmployeeService(db)
    emp = service.get_by_id(emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail=config.get_message("employee_not_found"))
    return EmployeeResponse.model_validate(emp)

@admin_app.put("/employees/{emp_id}", response_model=ResponseSuccess, dependencies=[Depends(require_roles(Role.ADMIN))], tags=["Employees"], summary="Cập nhật toàn bộ nhân viên")
def update_employee(emp_id: int, data: EmployeeCreate, db: Session = Depends(database.get_db)):
    try:
        service = EmployeeService(db)
        result = service.update(emp_id, data)
        return ResponseSuccess(message=config.get_message("update_employee_success", name=data.fullname), data=EmployeeResponse.model_validate(result))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@admin_app.patch("/employees/{emp_id}", response_model=ResponseSuccess,dependencies=[Depends(require_roles(Role.ADMIN))], tags=["Employees"], summary="Sửa một phần nhân viên")
def patch_employee(emp_id: int, data: EmployeeUpdate, db: Session = Depends(database.get_db)):
    try:
        service = EmployeeService(db)
        result = service.update_partial(emp_id, data)
        return ResponseSuccess(message=config.get_message("update_employee_success", name=result.fullname), data=EmployeeResponse.model_validate(result))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@admin_app.delete("/employees/{emp_id}", response_model=ResponseSuccess, tags=["Employees"], summary="Xóa nhân viên")
def delete_employee(emp_id: int, db: Session = Depends(database.get_db), current_user = Depends(require_roles(Role.ADMIN))):
    try:
        service = EmployeeService(db)
        result = service.delete(emp_id) 
        return ResponseSuccess(message=config.get_message("delete_employee_success", name=result.fullname, id=emp_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --------------------------------------------------------------------------
# ADMIN: TÍNH LƯƠNG NHÂN VIÊN THEO THÁNG 
# --------------------------------------------------------------------------
@admin_app.get("/employees/{emp_id}/salary", dependencies=[Depends(require_roles(Role.ADMIN))],response_model=SalaryResponse, tags=["Employees"], summary="Tính lương nhân viên theo tháng (Tự động tính công & phép đã duyệt)")
def get_employee_salary(
    emp_id: int,
    year: int = Query(..., description="Năm tính lương, ví dụ: 2026"),
    month: int = Query(..., ge=1, le=12, description="Tháng tính lương (1-12)"),
    db: Session = Depends(database.get_db),
   
):
    try:
        service = EmployeeService(db)
        emp = service.get_by_id(emp_id)
        
        if not emp:
            raise ValueError(config.get_message("employee_not_found"))
        if not emp.salary or emp.salary <= 0:
            raise ValueError("Nhân viên chưa có mức lương hợp lệ!")

        # 1. Tính số ngày công chuẩn của tháng đó
        standard_work_days = SalaryService.get_standard_work_days(year, month)

        # 2. Xác định ngày bắt đầu và kết thúc của tháng tính lương
        start_month, end_month, _ = SalaryService.get_month_range(year, month)

        # 3. Truy vấn các đơn xin nghỉ đã được duyệt và có giao với tháng hiện tại
        approved_leaves = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == emp_id,
            LeaveRequest.status.ilike("approved"),  
            LeaveRequest.start_date <= end_month,
            LeaveRequest.end_date >= start_month
        ).all()

        logger.info(start_month)
        paid_leave_days, unpaid_leave_days = SalaryService.calculate_leave_days_in_month(
            approved_leaves=approved_leaves, 
            year=year, 
            month=month
        )
        logger.info(f"Tháng {month}/{year}: Nghỉ có lương={paid_leave_days} ngày, Không lương={unpaid_leave_days} ngày")

        breakdown = SalaryService.calculate(
            gross_salary=emp.salary,
            standard_work_days=standard_work_days,
            unpaid_leave_days=unpaid_leave_days,
            paid_leave_days=paid_leave_days,
            emp_id=emp_id,
            year=year,
            month=month
        )

        return SalaryResponse(
            ma_nhan_vien=emp.id,
            ho_ten=emp.fullname,
            nam=year,
            thang=month,
            **breakdown
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=config.get_message("server_error", error=str(e)))
    
# --- ADMIN: QUẢN LÝ ĐƠN XIN NGHÍ PHÉP ---
@admin_app.get("/leave-requests", response_model=ResponseSuccess, dependencies=[Depends(require_roles(Role.ADMIN))],tags=["Quản lý nghỉ phép"], summary="Admin xem tất cả đơn xin nghỉ")
def get_all_leave_requests(
    status: Optional[LeaveStatusEnum] = Query(None, description="Lọc trạng thái: pending, approved, rejected"),
    db: Session = Depends(database.get_db),
    
):
    service = LeaveRequestService(db)
    status_value = status.value if status else None
    requests = service.get_all(status=status_value)
    data = [LeaveRequestResponse.model_validate(r) for r in requests]
    return ResponseSuccess(message="Lấy danh sách đơn nghỉ phép thành công!", data=data)

@admin_app.patch("/leave-requests/{request_id}/status", response_model=ResponseSuccess, tags=["Quản lý nghỉ phép"], summary="Admin duyệt hoặc từ chối đơn nghỉ phép")
def update_leave_request_status(
    request_id: int,
    data: LeaveRequestStatusUpdate,
    db: Session = Depends(database.get_db),
    current_user = Depends(require_roles(Role.ADMIN))
):
    try:
        service = LeaveRequestService(db)
        result = service.update_status(request_id, data.status.value)
        return ResponseSuccess(
            message=f"Đã cập nhật trạng thái đơn thành {data.status.value}!", 
            data=LeaveRequestResponse.model_validate(result)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --------------------------------------------------------------------------
# 3. EMPLOYEE APP (DÀNH CHO NHÂN VIÊN)
# --------------------------------------------------------------------------
@employee_app.get("/me", response_model=EmployeeResponse, tags=["Thông tin cá nhân"], summary="Xem thông tin cá nhân")
def get_my_profile(db: Session = Depends(database.get_db), current_user = Depends(get_current_user)):
    if current_user.employee_id is None:
        raise HTTPException(status_code=404, detail="Tài khoản chưa liên kết với hồ sơ nhân viên!")
    service = EmployeeService(db)
    emp = service.get_by_id(current_user.employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail=config.get_message("employee_not_found"))
    return EmployeeResponse.model_validate(emp)

@employee_app.patch("/me", response_model=ResponseSuccess, tags=["Thông tin cá nhân"], summary="Tự sửa thông tin cá nhân")
def update_my_profile(data: EmployeeSelfUpdate, db: Session = Depends(database.get_db), current_user = Depends(get_current_user)):
    if current_user.employee_id is None:
        raise HTTPException(status_code=404, detail="Tài khoản chưa liên kết với hồ sơ nhân viên!")
    try:
        service = EmployeeService(db)
        result = service.update_self(current_user.employee_id, data)
        return ResponseSuccess(message=config.get_message("update_employee_success", name=result.fullname), data=EmployeeResponse.model_validate(result))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- EMPLOYEE: XIN NGHỈ PHÉP ---
@employee_app.post("/leave-requests", response_model=ResponseSuccess, tags=["Xin nghỉ phép"], summary="Nhân viên gửi đơn xin nghỉ")
def create_leave_request(data: LeaveRequestCreate, db: Session = Depends(database.get_db), current_user = Depends(get_current_user)):
    if current_user.employee_id is None:
        raise HTTPException(status_code=400, detail="Tài khoản chưa được liên kết với hồ sơ nhân viên!")
    try:
        service = LeaveRequestService(db)
        result = service.create_request(current_user.employee_id, data)
        return ResponseSuccess(
            message="Gửi đơn xin nghỉ thành công, vui lòng chờ Admin duyệt!", 
            data=LeaveRequestResponse.model_validate(result), 
            code=201
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@employee_app.get("/leave-requests", response_model=ResponseSuccess, tags=["Xin nghỉ phép"], summary="Xem danh sách đơn xin nghỉ của bản thân")
def get_my_leave_requests(db: Session = Depends(database.get_db), current_user = Depends(get_current_user)):
    if current_user.employee_id is None:
        raise HTTPException(status_code=400, detail="Tài khoản chưa được liên kết với hồ sơ nhân viên!")
    
    service = LeaveRequestService(db)
    requests = service.get_by_employee(current_user.employee_id)
    data = [LeaveRequestResponse.model_validate(r) for r in requests]
    return ResponseSuccess(message="Lấy danh sách đơn nghỉ thành công!", data=data)



app.mount("/admin", admin_app)
app.mount("/employee", employee_app)

@app.on_event("startup")
async def startup():
    logger.info("Application startup")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shutdown")