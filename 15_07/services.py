from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError, DataError
from sqlalchemy import or_
from datetime import datetime, date
from typing import Optional
import re
from .Database import database, Department, Employee, User
from .config import config  
from .logger import logger
from .schemas import DepartmentCreate, EmployeeCreate,DepartmentUpdate
from .auth import hash_password, verify_password, Role
from .exceptions import (
    DuplicateKeyError,
    ForeignKeyReferenceError,
    InvalidDataTypeError,
    DatabaseIntegrityError,
    DatabaseConnectionError,
)
from fastapi import HTTPException

class DepartmentService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: DepartmentCreate):
        # 1. Kiểm tra tên phòng ban không được để trống
        if not data.name or data.name.strip() == "":
            logger.warning("Tạo phòng ban thất bại: tên trống")
            raise ValueError(config.get_message("empty_name"))

        # 2. Kiểm tra phòng ban đã tồn tại chưa
        existing_dept = self.db.query(Department).filter(
            Department.name == data.name
        ).first()
        
        if existing_dept:
            logger.warning(f"Tạo phòng ban thất bại: '{data.name}' đã tồn tại")
            raise ValueError(config.get_message("department_exists"))

        new_dept = Department(**data.model_dump())
        self.db.add(new_dept)

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"IntegrityError khi tạo phòng ban '{data.name}': {e}")
            raise DuplicateKeyError("Phòng ban đã tồn tại (vi phạm ràng buộc UNIQUE)") from e
        except OperationalError as e:
            self.db.rollback()
            logger.error(f"OperationalError khi tạo phòng ban '{data.name}': {e}")
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e
        except DataError as e:
            self.db.rollback()
            logger.error(f"DataError khi tạo phòng ban '{data.name}': {e}")
            raise InvalidDataTypeError("Dữ liệu không hợp lệ khi ghi phòng ban") from e

        self.db.refresh(new_dept)
        logger.info(f"Đã tạo phòng ban '{new_dept.name}' (ID: {new_dept.id})")
        return new_dept
    def update_department(self, department_id: int, data: DepartmentUpdate):
        # 1. Tìm phòng ban trong database
        department = self.db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Không tìm thấy phòng ban")

        # 2. Cập nhật thông tin (nếu người dùng có gửi tên mới lên)
        if data.name:
            department.name = data.name

        # 3. Lưu vào database
        self.db.commit()
        self.db.refresh(department)
        return department

    def delete_department(self, department_id: int):
        # 1. Tìm phòng ban
        department = self.db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Không tìm thấy phòng ban")

        self.db.delete(department)
        self.db.commit()
        return {"detail": "Đã xóa phòng ban thành công"}

    def get_all(
        self,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ):
        """Lấy danh sách phòng ban có tìm kiếm (theo tên/mô tả) + phân trang"""
        try:
            query = self.db.query(Department)

            if search:
                like_pattern = f"%{search.strip()}%"
                query = query.filter(
                    or_(
                        Department.name.ilike(like_pattern),
                        Department.description.ilike(like_pattern),
                    )
                )

            total = query.count()
            items = (
                query.order_by(Department.id)
                .offset(skip)
                .limit(limit)
                .all()
            )

            logger.debug(
                f"Truy vấn phòng ban: search='{search}', skip={skip}, "
                f"limit={limit} -> {len(items)}/{total} kết quả"
            )
            return items, total

        except OperationalError as e:
            logger.error(f"OperationalError khi lấy danh sách phòng ban: {e}")
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_employee_data(self, data: EmployeeCreate, is_update: bool = False):
     
        if not data.fullname or data.fullname.strip() == "":
            raise ValueError(config.get_message("empty_name"))
        
       
        if not data.position or data.position.strip() == "":
            raise ValueError("Chức vụ (position) không được để trống!")
        
        
        if data.department_id:
            dept_exists = self.db.query(Department).filter(
                Department.id == data.department_id
            ).first()
            if not dept_exists:
                raise ValueError(config.get_message("department_not_found"))
        
        if data.email:
            existing_email = self.db.query(Employee).filter(
                Employee.email == data.email
            ).first()
            
         
            if not is_update and existing_email:
                raise ValueError(config.get_message("email_exists"))
            
            # Nếu là update, kiểm tra email mới không được của người khác
            if is_update and existing_email:
           
                pass
        
     
        if data.phone:
            clean_phone = data.phone.strip()
            if clean_phone and len(clean_phone) < config.MIN_PHONE_LENGTH:
                raise ValueError(config.get_message("phone_invalid"))
            
            if clean_phone:
                existing_phone = self.db.query(Employee).filter(
                    Employee.phone == clean_phone
                ).first()
                if not is_update and existing_phone:
                    raise ValueError("Số điện thoại này đã được sử dụng bởi một nhân viên khác!")
        
        
        if data.salary is not None and data.salary <= 0:
            raise ValueError(config.get_message("salary_invalid"))
        
        if data.hire_date:
            hire_date_val = data.hire_date
            
            if isinstance(hire_date_val, str):
                try:
                    hire_date_val = datetime.strptime(hire_date_val, config.DATE_FORMAT).date()
                except ValueError:
                    raise ValueError(f"Định dạng ngày tuyển dụng phải là YYYY-MM-DD (ví dụ: 2026-01-15)")
            
            today = date.today()
            if hire_date_val > today:
                raise ValueError("Ngày tuyển dụng không thể trong tương lai!")
        
        return True

    def create(self, data: EmployeeCreate):
        
        self._validate_employee_data(data, is_update=False)
        
        # Nếu validation pass, mới tạo object và commit
        new_emp = Employee(**data.model_dump())
        self.db.add(new_emp)

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"IntegrityError khi tạo nhân viên '{data.fullname}': {e}")
            raise DuplicateKeyError("Email hoặc số điện thoại đã tồn tại") from e
        except OperationalError as e:
            self.db.rollback()
            logger.error(f"OperationalError khi tạo nhân viên '{data.fullname}': {e}")
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e
        except DataError as e:
            self.db.rollback()
            logger.error(f"DataError khi tạo nhân viên '{data.fullname}': {e}")
            raise InvalidDataTypeError("Dữ liệu không hợp lệ khi ghi nhân viên") from e

        self.db.refresh(new_emp)
        logger.info(f"Đã tạo nhân viên '{new_emp.fullname}' (ID: {new_emp.id})")
        return new_emp

    def get_all(
        self,
        search: Optional[str] = None,
        department_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        min_salary: Optional[float] = None,
        max_salary: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ):
      
        try:
            query = self.db.query(Employee)

            if search:
                like_pattern = f"%{search.strip()}%"
                query = query.filter(
                    or_(
                        Employee.fullname.ilike(like_pattern),
                        Employee.email.ilike(like_pattern),
                        Employee.phone.ilike(like_pattern),
                        Employee.position.ilike(like_pattern),
                    )
                )

            if department_id is not None:
                query = query.filter(Employee.department_id == department_id)

            if is_active is not None:
                query = query.filter(Employee.is_active == is_active)

            if min_salary is not None:
                query = query.filter(Employee.salary >= min_salary)

            if max_salary is not None:
                query = query.filter(Employee.salary <= max_salary)

            total = query.count()
            items = (
                query.order_by(Employee.id)
                .offset(skip)
                .limit(limit)
                .all()
            )

            logger.debug(
                f"Truy vấn nhân viên: search='{search}', department_id={department_id}, "
                f"is_active={is_active}, min_salary={min_salary}, max_salary={max_salary}, "
                f"skip={skip}, limit={limit} -> {len(items)}/{total} kết quả"
            )
            return items, total

        except OperationalError as e:
            logger.error(f"OperationalError khi lấy danh sách nhân viên: {e}")
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e

    def get_by_id(self, emp_id: int):
        try:
            return self.db.query(Employee).filter(Employee.id == emp_id).first()
        except OperationalError as e:
            logger.error(f"OperationalError khi lấy nhân viên ID={emp_id}: {e}")
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e

    def export_to_csv(self):
        employees = self.db.query(Employee).all()
        if not employees:
            raise ValueError(config.get_message("no_data"))
        return employees

    def delete(self, emp_id: int):
        employee = self.db.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            logger.warning(f"Xóa nhân viên thất bại: không tìm thấy ID={emp_id}")
            raise ValueError(config.get_message("employee_not_found"))

        self.db.delete(employee)

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"IntegrityError khi xóa nhân viên ID={emp_id}: {e}")
            raise ForeignKeyReferenceError(
                "Không thể xóa nhân viên vì đang được tham chiếu ở nơi khác"
            ) from e
        except OperationalError as e:
            self.db.rollback()
            logger.error(f"OperationalError khi xóa nhân viên ID={emp_id}: {e}")
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e

        logger.info(f"Đã xóa nhân viên '{employee.fullname}' (ID: {emp_id})")
        return employee

    def update(self, emp_id: int, data: EmployeeCreate):
      
        employee = self.db.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            raise ValueError(config.get_message("employee_not_found"))
        
        #  VALIDATE TRƯỚC - nếu có lỗi, không commit vào DB
        self._validate_employee_data(data, is_update=True)
        
        # Kiểm tra email mới không bị trùng với người khác
        if data.email and data.email != employee.email:
            existing_email = self.db.query(Employee).filter(
                Employee.email == data.email,
                Employee.id != emp_id  # Loại trừ chính nhân viên này
            ).first()
            if existing_email:
                raise ValueError(config.get_message("email_exists"))
        
        #  Kiểm tra phone mới không bị trùng với người khác
        if data.phone and data.phone.strip() and data.phone != employee.phone:
            clean_phone = data.phone.strip()
            existing_phone = self.db.query(Employee).filter(
                Employee.phone == clean_phone,
                Employee.id != emp_id  
            ).first()
            if existing_phone:
                raise ValueError("Số điện thoại này đã được sử dụng bởi một nhân viên khác!")
        
     
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(employee, key, value)

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"IntegrityError khi cập nhật nhân viên ID={emp_id}: {e}")
            raise DuplicateKeyError("Email hoặc số điện thoại đã tồn tại") from e
        except OperationalError as e:
            self.db.rollback()
            logger.error(f"OperationalError khi cập nhật nhân viên ID={emp_id}: {e}")
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e
        except DataError as e:
            self.db.rollback()
            logger.error(f"DataError khi cập nhật nhân viên ID={emp_id}: {e}")
            raise InvalidDataTypeError("Dữ liệu không hợp lệ khi cập nhật nhân viên") from e

        self.db.refresh(employee)
        logger.info(f"Đã cập nhật nhân viên '{employee.fullname}' (ID: {emp_id})")
        return employee
   

class SalaryService:
    
    @staticmethod
    def calculate_pit(taxable_income: float) -> float:
        """Tính thuế TNCN theo biểu lũy tiến từng phần (áp theo ĐỘ RỘNG mỗi bậc)."""
        if taxable_income <= 0:
            return 0.0

        tax = 0.0
        remaining = taxable_income
        for width, rate in config.PIT_BRACKETS:
            if remaining <= 0:
                break
            bracket_amount = remaining if width is None else min(remaining, width)
            tax += bracket_amount * rate
            remaining -= bracket_amount

        return round(tax, 2)

    @classmethod
    def calculate(cls, gross_salary: float, dependents: int = 0) -> dict:
        """
        gross_salary: lương thỏa thuận (Employee.salary)
        dependents:   số người phụ thuộc (mỗi người được giảm trừ thêm)
        """
        if gross_salary is None or gross_salary <= 0:
            raise ValueError("Lương gross phải > 0 để tính lương")
        if dependents < 0:
            raise ValueError("Số người phụ thuộc không được âm")

        insurance_amount = round(gross_salary * config.INSURANCE_RATE, 2)

        personal_deduction = config.PERSONAL_DEDUCTION
        dependent_deduction = dependents * config.DEPENDENT_DEDUCTION

        taxable_income = max(
            0.0,
            gross_salary - insurance_amount - personal_deduction - dependent_deduction,
        )

        tax_amount = cls.calculate_pit(taxable_income)
        net_salary = round(gross_salary - insurance_amount - tax_amount, 2)

        return {
            "gross_salary": gross_salary,
            "insurance_amount": insurance_amount,
            "dependents": dependents,
            "personal_deduction": personal_deduction,
            "dependent_deduction": dependent_deduction,
            "taxable_income": round(taxable_income, 2),
            "tax_amount": tax_amount,
            "net_salary": net_salary,
        }


class UserService:
    """Đăng ký tài khoản + xác thực đăng nhập (Authentication)."""

    def __init__(self, db: Session):
        self.db = db

    def register(
        self,
        username: str,
        password: str,
        role: str = Role.EMPLOYEE,
        employee_id: Optional[int] = None,
    ):
        if not username or not username.strip():
            raise ValueError(config.get_message("empty_name"))
        if not password or len(password) < 6:
            raise ValueError(config.get_message("password_too_short"))

        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            logger.warning(f"Đăng ký thất bại: username '{username}' đã tồn tại")
            raise ValueError(config.get_message("username_exists"))

        if employee_id is not None:
            emp = self.db.query(Employee).filter(Employee.id == employee_id).first()
            if not emp:
                raise ValueError(config.get_message("employee_not_found"))

            linked = self.db.query(User).filter(User.employee_id == employee_id).first()
            if linked:
                raise ValueError("Nhân viên này đã có tài khoản liên kết!")

        new_user = User(
            username=username.strip(),
            hashed_password=hash_password(password),
            role=role,
            employee_id=employee_id,
        )
        self.db.add(new_user)

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"IntegrityError khi tạo tài khoản '{username}': {e}")
            raise DuplicateKeyError("Tên đăng nhập đã tồn tại") from e
        except OperationalError as e:
            self.db.rollback()
            logger.error(f"OperationalError khi tạo tài khoản '{username}': {e}")
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e

        self.db.refresh(new_user)
        logger.info(f"Đã tạo tài khoản '{username}' (role={role})")
        return new_user

    def authenticate(self, username: str, password: str):
        try:
            user = self.db.query(User).filter(User.username == username).first()
        except OperationalError as e:
            logger.error(f"OperationalError khi đăng nhập '{username}': {e}")
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e

        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            logger.warning(f"Đăng nhập thất bại cho username='{username}'")
            return None

        logger.info(f"User '{username}' đăng nhập thành công (role={user.role})")
        return user