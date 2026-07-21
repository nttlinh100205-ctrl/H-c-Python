from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from math import ceil
from .logger import logger
from .config import config
from .Database import database  
database.create_tables()

from .schemas import (
    EmployeeCreate, DepartmentCreate, ResponseSuccess, DepartmentUpdate,
    EmployeeResponse, DepartmentResponse, HealthCheck,
    DepartmentListResponse, EmployeeListResponse, PaginationMeta,
    UserCreate, UserResponse, LoginRequest, Token, SalaryResponse
)
from .services import EmployeeService, DepartmentService, SalaryService, UserService
from .auth import create_access_token, get_current_user, require_roles, Role
from .utils import ExcelExporter, CSVExporter, DateFormatter, ResponseFormatter
from .exceptions import (
    DatabaseOperationError,
    DuplicateKeyError,
    ForeignKeyReferenceError,
    RequiredFieldError,
    DatabaseIntegrityError,
    InvalidDataTypeError,
    DatabaseConnectionError,
)
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION,
    docs_url=config.API_DOCS_URL,
    openapi_url=config.API_OPENAPI_URL
)


def build_pagination_meta(total: int, skip: int, limit: int) -> PaginationMeta:
    """Tạo object PaginationMeta dùng chung cho các API danh sách"""
    total_pages = ceil(total / limit) if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1
    return PaginationMeta(
        total=total,
        skip=skip,
        limit=limit,
        total_pages=total_pages,
        page=current_page,
    )


@app.post(
    "/auth/register",
    response_model=ResponseSuccess,
    tags=["Auth"],
    summary="Đăng ký tài khoản mới (mặc định role=employee)"
)
def register(
    data: UserCreate,
    db: Session = Depends(database.get_db)
):
    
    logger.info(f"[API] POST /auth/register username='{data.username}'")
    try:
        service = UserService(db)
        result = service.register(
            username=data.username,
            password=data.password,
            role=Role.EMPLOYEE,
            employee_id=data.employee_id,
        )
        return ResponseSuccess(
            message="Đăng ký tài khoản thành công!",
            data=UserResponse.model_validate(result),
            code=201
        )

    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except DatabaseOperationError:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=config.get_message("server_error", error=str(e))
        )


@app.post(
    "/auth/login",
    response_model=Token,
    tags=["Auth"],
    summary="Đăng nhập, lấy JWT access token"
)
def login(
   
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    
    logger.info(f"[API] POST /auth/login username='{form_data.username}'")
    try:
        service = UserService(db)
        user = service.authenticate(form_data.username, form_data.password) 
    except DatabaseOperationError:
        raise

    if not user:
        raise HTTPException(
            status_code=401,
            detail=config.get_message("invalid_credentials")
        )

    token = create_access_token(
        data={"sub": user.username, "role": user.role, "employee_id": user.employee_id}
    )
    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        expires_in_minutes=config.JWT_EXPIRE_MINUTES,
    )


@app.exception_handler(DuplicateKeyError)
async def duplicate_key_handler(request: Request, exc: DuplicateKeyError):
    logger.error(f"[API-409] {request.method} {request.url.path} -> {exc}")
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ForeignKeyReferenceError)
async def foreign_key_handler(request: Request, exc: ForeignKeyReferenceError):
    logger.error(f"[API-400] {request.method} {request.url.path} -> {exc}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(RequiredFieldError)
async def required_field_handler(request: Request, exc: RequiredFieldError):
    logger.error(f"[API-400] {request.method} {request.url.path} -> {exc}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(InvalidDataTypeError)
async def invalid_data_type_handler(request: Request, exc: InvalidDataTypeError):
    logger.error(f"[API-400] {request.method} {request.url.path} -> {exc}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(DatabaseConnectionError)
async def db_connection_handler(request: Request, exc: DatabaseConnectionError):
    logger.error(f"[API-503] {request.method} {request.url.path} -> {exc}")
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(DatabaseIntegrityError)
async def db_integrity_handler(request: Request, exc: DatabaseIntegrityError):
    logger.error(f"[API-409] {request.method} {request.url.path} -> {exc}")
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(DatabaseOperationError)
async def db_operation_fallback_handler(request: Request, exc: DatabaseOperationError):
   
    logger.error(f"[API-500] {request.method} {request.url.path} -> {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": config.get_message("server_error", error=str(exc))}
    )


@app.post(
    "/departments",
    response_model=ResponseSuccess,
    tags=["Departments"],
    summary="Tạo phòng ban mới"
)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(database.get_db),
    current_user = Depends(require_roles(Role.ADMIN))
):
    logger.info(f"[API] POST /departments name='{data.name}' by admin='{current_user.username}'")
    try:
        service = DepartmentService(db)
        result = service.create(data)
        
        dept_data = DepartmentResponse.model_validate(result)
        
        return ResponseSuccess(
            message=config.get_message("create_department_success"),
            data=dept_data, 
            code=201
        )
    
    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    

    except DatabaseOperationError:
        raise
    
    except Exception as e:
        db.rollback()
        logger.error(f"Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=config.get_message("server_error", error=str(e))
        )


@app.get(
    "/departments",
    response_model=DepartmentListResponse,
    tags=["Departments"],
    summary="Lấy danh sách phòng ban (tìm kiếm + phân trang)"
)
def list_departments(
    search: Optional[str] = Query(None, description="Tìm theo tên hoặc mô tả phòng ban"),
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
    db: Session = Depends(database.get_db),
    current_user = Depends(require_roles(Role.ADMIN))
):
    """Lấy danh sách phòng ban, hỗ trợ tìm kiếm theo tên/mô tả và phân trang. (Chỉ Admin)"""
    logger.info(f"[API] GET /departments search='{search}' skip={skip} limit={limit} by admin='{current_user.username}'")
    try:
        service = DepartmentService(db)
        items, total = service.get_all(search=search, skip=skip, limit=limit)

        return DepartmentListResponse(
            items=[DepartmentResponse.model_validate(item) for item in items],
            meta=build_pagination_meta(total, skip, limit)
        )
    
    except DatabaseOperationError:
        raise
    
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=config.get_message("server_error", error=str(e))
        )

@app.put("/departments/{department_id}", tags=["Departments"], summary="Sửa thông tin phòng ban")
def update_department(
    department_id: int, 
    data: DepartmentUpdate, 
    db: Session = Depends(database.get_db),
    current_admin = Depends(require_roles(Role.ADMIN))# Yêu cầu quyền Admin
):
    service = DepartmentService(db) # Gọi nhà bếp
    return service.update_department(department_id, data)


@app.delete("/departments/{department_id}", tags=["Departments"], summary="Xóa phòng ban")
def delete_department(
    department_id: int,
    db: Session = Depends(database.get_db),
    current_admin = Depends(require_roles(Role.ADMIN))# Yêu cầu quyền Admin
):
    service = DepartmentService(db) # Gọi nhà bếp
    return service.delete_department(department_id)

@app.post(
    "/employees",
    response_model=ResponseSuccess,
    tags=["Employees"],
    summary="Tạo nhân viên mới"
)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(database.get_db),
    current_user = Depends(require_roles(Role.ADMIN))
):
    logger.info(f"[API] POST /employees fullname='{data.fullname}' by admin='{current_user.username}'")
    try:
        service = EmployeeService(db)
        result = service.create(data)
        
        emp_data = EmployeeResponse.model_validate(result)
        return ResponseSuccess(
            message=config.get_message(
                "create_employee_success",
                name=data.fullname
            ),
            data=emp_data,
            code=201
        )
    
    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    except DatabaseOperationError:
        raise
    
    except Exception as e:
        db.rollback()
        logger.error(f"Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=config.get_message("server_error", error=str(e))
        )


@app.put(
    "/employees/{emp_id}",
    response_model=ResponseSuccess,
    tags=["Employees"],
    summary="Cập nhật thông tin nhân viên"
)
def update_employee(
    emp_id: int,
    data: EmployeeCreate,
    db: Session = Depends(database.get_db),
    current_user = Depends(require_roles(Role.ADMIN))
):
    """Cập nhật thông tin nhân viên (Chỉ Admin)"""
    logger.info(f"[API] PUT /employees/{emp_id} fullname='{data.fullname}' by admin='{current_user.username}'")
    try:
        service = EmployeeService(db)
        result = service.update(emp_id, data)
        
        emp_data = EmployeeResponse.model_validate(result)
        return ResponseSuccess(
            message=config.get_message(
                "update_employee_success",
                name=data.fullname
            ),
            data=emp_data,
            code=200
        )
    
    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    except DatabaseOperationError:
        raise
    
    except Exception as e:
        db.rollback()
        logger.error(f"Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=config.get_message("server_error", error=str(e))
        )


@app.delete(
    "/employees/{emp_id}",
    response_model=ResponseSuccess,
    tags=["Employees"],
    summary="Xóa nhân viên"
)
def delete_employee(
    emp_id: int,
    db: Session = Depends(database.get_db),
    current_user = Depends(require_roles(Role.ADMIN))
):
    """Xóa nhân viên theo ID (Chỉ Admin)"""
    logger.info(f"[API] DELETE /employees/{emp_id} by admin='{current_user.username}'")
    try:
        service = EmployeeService(db)
        result = service.delete(emp_id) 
        
        return ResponseSuccess(
            message=config.get_message(
                "delete_employee_success",
                name=result.fullname, 
                id=emp_id
            ),
            code=200
        )
    
    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=404, detail=str(e))
    
    except DatabaseOperationError:
        raise
    
    except Exception as e:
        db.rollback()
        logger.error(f"Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=config.get_message("server_error", error=str(e))
        )

@app.get(
    "/employees",
    response_model=EmployeeListResponse,
    tags=["Employees"],
    summary="Lấy danh sách nhân viên (tìm kiếm + lọc + phân trang)"
)
def list_employees(
    search: Optional[str] = Query(None, description="Tìm theo tên/email/SĐT/chức vụ"),
    department_id: Optional[int] = Query(None, description="Lọc theo phòng ban"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái làm việc"),
    min_salary: Optional[float] = Query(None, ge=0, description="Lương tối thiểu"),
    max_salary: Optional[float] = Query(None, ge=0, description="Lương tối đa"),
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
    db: Session = Depends(database.get_db),
    current_user = Depends(require_roles(Role.ADMIN))
):
    """Lấy danh sách nhân viên, hỗ trợ tìm kiếm, lọc theo phòng ban/trạng thái/khoảng lương, và phân trang. (Chỉ Admin)"""
    logger.info(
        f"[API] GET /employees search='{search}' department_id={department_id} "
        f"is_active={is_active} min_salary={min_salary} max_salary={max_salary} "
        f"skip={skip} limit={limit} by admin='{current_user.username}'"
    )
    try:
        service = EmployeeService(db)
        items, total = service.get_all(
            search=search,
            department_id=department_id,
            is_active=is_active,
            min_salary=min_salary,
            max_salary=max_salary,
            skip=skip,
            limit=limit,
        )

        return EmployeeListResponse(
            items=[EmployeeResponse.model_validate(item) for item in items],
            meta=build_pagination_meta(total, skip, limit)
        )
    
    except DatabaseOperationError:
        raise
    
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=config.get_message("server_error", error=str(e))
        )

@app.get(
    "/employees/export-csv",
    tags=["Employees"],
    summary="Xuất danh sách nhân viên ra Excel (.xlsx)"
)
def export_csv(
    db: Session = Depends(database.get_db),
    current_user = Depends(require_roles(Role.ADMIN))
):
   
    try:
        service = EmployeeService(db)
        employees = service.export_to_csv()
        
        excel_data = ExcelExporter.export_employees(employees)
        
        logger.info(
            config.get_message(
                "export_csv_success",
                count=len(employees)
            )
        )
        
        excel_filename = config.CSV_FILENAME.rsplit(".", 1)[0] + ".xlsx"
        
        return StreamingResponse(
            excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition":
                f"attachment; filename={excel_filename}"
            }
        )
    
    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=404, detail=str(e))
    
    except DatabaseOperationError:
        raise
    
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=config.get_message("server_error", error=str(e))
        )

@app.get(
    "/employees/{emp_id}",
    response_model=EmployeeResponse,
    tags=["Employees"],
    summary="Lấy thông tin chi tiết nhân viên"
)
def get_employee(
    emp_id: int,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
 
    logger.info(f"[API] GET /employees/{emp_id} by user='{current_user.username}' role={current_user.role}")

    if current_user.role != Role.ADMIN and current_user.employee_id != emp_id:
        logger.warning(
            f"[403] User '{current_user.username}' (employee_id={current_user.employee_id}) "
            f"cố xem thông tin nhân viên khác (ID={emp_id})"
        )
        raise HTTPException(
            status_code=403,
            detail="Bạn chỉ được xem thông tin của chính mình"
        )

    try:
        service = EmployeeService(db)
        emp = service.get_by_id(emp_id)
        
        if not emp:
            raise ValueError(config.get_message("employee_not_found"))
     
        return EmployeeResponse.model_validate(emp)
    
    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=404, detail=str(e))
    
    except DatabaseOperationError:
        raise
    
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=config.get_message("server_error", error=str(e))
        )


@app.get(
    "/employees/{emp_id}/salary",
    response_model=SalaryResponse,
    tags=["Employees"],
    summary="Tính lương nhân viên (chỉ Admin)"
)
def get_employee_salary(
    emp_id: int,
    dependents: int = Query(0, ge=0, description="Số người phụ thuộc để giảm trừ gia cảnh"),
    db: Session = Depends(database.get_db),
    current_user = Depends(require_roles(Role.ADMIN))
):
    logger.info(
        f"[API] GET /employees/{emp_id}/salary dependents={dependents} "
        f"by admin='{current_user.username}'"
    )
    try:
        service = EmployeeService(db)
        emp = service.get_by_id(emp_id)

        if not emp:
            raise ValueError(config.get_message("employee_not_found"))

        if not emp.salary or emp.salary <= 0:
            raise ValueError("Nhân viên chưa có mức lương hợp lệ để tính")

        breakdown = SalaryService.calculate(emp.salary, dependents=dependents)

        return SalaryResponse(
            employee_id=emp.id,
            fullname=emp.fullname,
            **breakdown,
        )

    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except DatabaseOperationError:
        raise

    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=config.get_message("server_error", error=str(e))
        )


@app.get(
    "/health",
    response_model=HealthCheck,
    tags=["System"],
    summary="Kiểm tra trạng thái API"
)
def health_check():
    """Kiểm tra trạng thái API"""
    logger.debug("Health check")
    return {
        "status": "ok",
        "timestamp": DateFormatter.get_current_datetime(),
        "database": "connected"
    }


@app.on_event("startup")
async def startup():
    """Chạy khi ứng dụng khởi động"""
    logger.info("Application startup")
  
@app.on_event("shutdown")
async def shutdown():
    """Chạy khi ứng dụng tắt"""
    logger.info("Application shutdown")
 

@app.get("/", tags=["System"])
def root():
    """API info"""
    return {
        "name": config.API_TITLE,
        "version": config.API_VERSION,
        "docs": "/docs",
        "status": "running"
    }