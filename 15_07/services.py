from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError, DataError
from sqlalchemy import or_
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import calendar
from fastapi import HTTPException

from .Database import Department, Employee, User, LeaveRequest
from .config import config  
from .logger import logger
from .schemas import (
    DepartmentCreate, EmployeeCreate, DepartmentUpdate, EmployeeUpdate, 
    EmployeeSelfUpdate, LeaveRequestCreate, LeaveStatusEnum, LeaveTypeEnum
)
from .auth import hash_password, verify_password, Role
from .exceptions import (
    DuplicateKeyError,
    ForeignKeyReferenceError,
    InvalidDataTypeError,
    DatabaseIntegrityError,
    DatabaseConnectionError,
)


class SalaryService:
    @staticmethod
    def get_month_range(year: int, month: int) -> tuple[date, date, int]:
        num_days = calendar.monthrange(year, month)[1]
        start_month = date(year, month, 1)
        end_month = date(year, month, num_days)
        return start_month, end_month, num_days

    @staticmethod
    def get_standard_work_days(year: int, month: int) -> int:
        _, _, num_days = SalaryService.get_month_range(year, month)
        standard_days = sum(
            1 for day in range(1, num_days + 1)
            if date(year, month, day).weekday() < 5  
        )
        return standard_days

    @staticmethod
    def calculate_pit(taxable_income: float) -> float:
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
    def calculate(
        cls, 
        gross_salary: float, 
        standard_work_days: int, 
        unpaid_leave_days: int = 0,
        paid_leave_days: int = 0,
        emp_id: int = None,
        year: int = None,
        month: int = None
    ) -> Dict[str, Any]:
        
        if gross_salary is None or gross_salary <= 0:
            raise ValueError("Lương gross phải > 0 để tính lương")
        if standard_work_days <= 0:
            raise ValueError("Số ngày công chuẩn phải > 0")

        # Số ngày tính lương = ngày công chuẩn - số ngày nghỉ không lương
        actual_paid_days = max(0, standard_work_days - unpaid_leave_days)
        actual_gross = round((gross_salary / standard_work_days) * actual_paid_days, 2)

        if emp_id is not None and year is not None and month is not None:
            logger.log_salary_calculation(
                emp_id=emp_id, 
                year=year, 
                month=month, 
                standard_days=standard_work_days, 
                paid_leave=paid_leave_days, 
                unpaid_leave=unpaid_leave_days, 
                actual_paid=actual_paid_days, 
                actual_gross=actual_gross
            )

        # Tiền đóng bảo hiểm (10.5%)
        insurance_amount = round(actual_gross * config.INSURANCE_RATE, 2)
        
        # Thu nhập chịu thuế = Gross thực tế - Tiền bảo hiểm (Không trừ giảm trừ người phụ thuộc/bản thân)
        taxable_income = max(0.0, actual_gross - insurance_amount)

        # Thuế TNCN & Lương Net
        tax_amount = cls.calculate_pit(taxable_income)
        net_salary = round(actual_gross - insurance_amount - tax_amount, 2)

        return {
            "luong_gross_thoa_thuan": gross_salary,
            "so_ngay_cong_chuan": standard_work_days,
            "so_ngay_tinh_luong_thuc_te": actual_paid_days,
            "so_ngay_nghi_co_luong": paid_leave_days,
            "so_ngay_nghi_khong_luong": unpaid_leave_days,
            "luong_gross_thuc_te": actual_gross,
            "tien_bao_hiem_trich_nop": insurance_amount,
            "thu_nhap_chiu_thue": round(taxable_income, 2),
            "thue_tncn_phai_nop": tax_amount,
            "luong_net_thuc_nhan": net_salary,
        }

    @staticmethod
    def calculate_leave_days_in_month(approved_leaves: List[LeaveRequest], year: int, month: int) -> tuple[int, int]:
        paid_leave_days = 0
        unpaid_leave_days = 0
        start_month, end_month, _ = SalaryService.get_month_range(year, month)

        for req in approved_leaves:
            end_date = req.end_date or req.start_date
            
            # 2. Tìm khoảng thời gian giao nhau giữa kỳ nghỉ và tháng đang xét
            calc_start = max(req.start_date, start_month)
            calc_end = min(end_date, end_month)

            # Nếu calc_start > calc_end nghĩa là kỳ nghỉ không rơi vào tháng này
            if calc_start > calc_end:
                continue

            # 3. Đếm số ngày đi làm thực tế (T2 - T6) trong khoảng thời gian đã cắt gọn
            leave_days_count = sum(
                1 for i in range((calc_end - calc_start).days + 1)
                if (calc_start + timedelta(days=i)).weekday() < 5
            )
            
            leave_type_clean = str(req.leave_type).strip().lower()
           
            if leave_type_clean in [ "unpaid", LeaveTypeEnum.UNPAID.value.lower()]:
                unpaid_leave_days += leave_days_count
            elif leave_type_clean in [ "paid", LeaveTypeEnum.PAID.value.lower()]:
                paid_leave_days += leave_days_count
                
        return paid_leave_days, unpaid_leave_days


class LeaveRequestService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def normalize_leave_type(leave_type_value: str) -> str:
        if not leave_type_value:
            return ""
        
        normalized = leave_type_value.strip().lower()
        
        if "có lương" in normalized or "paid" in normalized:
            normalized = LeaveTypeEnum.PAID.value.lower()
        elif "không lương" in normalized or "unpaid" in normalized:
            normalized = LeaveTypeEnum.UNPAID.value.lower()
            
        logger.log_unknown_leave_type(original_value=leave_type_value, normalized_value=normalized)
        return normalized

    def create_request(self, employee_id: int, data: LeaveRequestCreate) -> LeaveRequest:
        if data.start_date > data.end_date:
            raise ValueError("Ngày bắt đầu không được lớn hơn ngày kết thúc!")
        
        leave_type_normalized = self.normalize_leave_type(data.leave_type.value)
        
        logger.log_leave_request_normalization(original_value=data.leave_type.value, normalized_value=leave_type_normalized)
        
        new_request = LeaveRequest(
            employee_id=employee_id,
            start_date=data.start_date,
            end_date=data.end_date,
            leave_type=leave_type_normalized,  
            reason=data.reason,
            status=LeaveStatusEnum.PENDING.value
        )
        self.db.add(new_request)
        self.db.commit()
        self.db.refresh(new_request)
        return new_request

    def get_by_employee(self, employee_id: int) -> List[LeaveRequest]:
        return self.db.query(LeaveRequest)\
            .filter(LeaveRequest.employee_id == employee_id)\
            .order_by(LeaveRequest.id.desc()).all()

    def get_all(self, status: Optional[str] = None) -> List[LeaveRequest]:
        query = self.db.query(LeaveRequest)
        if status:
            query = query.filter(LeaveRequest.status == status)
        return query.order_by(LeaveRequest.id.desc()).all()

    def update_status(self, request_id: int, status: str) -> LeaveRequest:
        leave_request = self.db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
        if not leave_request:
            raise ValueError("Không tìm thấy đơn xin nghỉ phép!")
        
        leave_request.status = status
        self.db.commit()
        self.db.refresh(leave_request)
        return leave_request


class DepartmentService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: DepartmentCreate):
        if not data.name or data.name.strip() == "":
            raise ValueError(config.get_message("empty_name"))

        existing_dept = self.db.query(Department).filter(Department.name == data.name).first()
        if existing_dept:
            raise ValueError(config.get_message("department_exists"))

        new_dept = Department(**data.model_dump())
        self.db.add(new_dept)

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise DuplicateKeyError("Phòng ban đã tồn tại (vi phạm ràng buộc UNIQUE)") from e
        except OperationalError as e:
            self.db.rollback()
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e

        self.db.refresh(new_dept)
        return new_dept

    def update_department(self, department_id: int, data: DepartmentUpdate):
        department = self.db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Không tìm thấy phòng ban")

        if data.name:
            department.name = data.name

        self.db.commit()
        self.db.refresh(department)
        return department

    def delete_department(self, department_id: int):
        department = self.db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Không tìm thấy phòng ban")

        self.db.delete(department)
        self.db.commit()
        return {"detail": "Đã xóa phòng ban thành công"}

    def get_all(self, search: Optional[str] = None, skip: int = 0, limit: int = 100):
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
            items = query.order_by(Department.id).offset(skip).limit(limit).all()
            return items, total

        except OperationalError as e:
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_employee_data(self, data: EmployeeCreate, is_update: bool = False):
        if data.fullname and not data.fullname.strip():
            raise ValueError(config.get_message("empty_name"))
        
        if data.email and "@" not in data.email:
            raise ValueError("Email không hợp lệ!")
        
        if data.phone and len(data.phone.strip()) < config.MIN_PHONE_LENGTH:
            raise ValueError(config.get_message("phone_invalid"))
        
        if data.salary and data.salary <= 0:
            raise ValueError(config.get_message("salary_invalid"))
        
        if data.hire_date:
            hire_date_val = data.hire_date
            if isinstance(hire_date_val, str):
                try:
                    hire_date_val = datetime.strptime(hire_date_val, config.DATE_FORMAT).date()
                except ValueError:
                    raise ValueError("Định dạng ngày tuyển dụng phải là YYYY-MM-DD")
            if hire_date_val > date.today():
                raise ValueError("Ngày tuyển dụng không thể trong tương lai!")
        
        return True

    def create(self, data: EmployeeCreate):
        self._validate_employee_data(data, is_update=False)
        new_emp = Employee(**data.model_dump())
        self.db.add(new_emp)

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise DuplicateKeyError("Email hoặc số điện thoại đã tồn tại") from e

        self.db.refresh(new_emp)
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
            items = query.order_by(Employee.id).offset(skip).limit(limit).all()
            return items, total

        except OperationalError as e:
            raise DatabaseConnectionError("Không thể kết nối tới cơ sở dữ liệu") from e

    def get_by_id(self, emp_id: int):
        return self.db.query(Employee).filter(Employee.id == emp_id).first()

    def export_to_csv(self):
        employees = self.db.query(Employee).all()
        if not employees:
            raise ValueError(config.get_message("no_data"))
        return employees

    def delete(self, emp_id: int):
        employee = self.db.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            raise ValueError(config.get_message("employee_not_found"))

        self.db.delete(employee)
        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise ForeignKeyReferenceError("Không thể xóa nhân viên vì đang được tham chiếu ở nơi khác") from e

        return employee

    def update(self, emp_id: int, data: EmployeeCreate):
        employee = self.db.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            raise ValueError(config.get_message("employee_not_found"))
        
        self._validate_employee_data(data, is_update=True)
        
        if data.email and data.email != employee.email:
            existing_email = self.db.query(Employee).filter(Employee.email == data.email, Employee.id != emp_id).first()
            if existing_email:
                raise ValueError(config.get_message("email_exists"))
        
        if data.phone and data.phone.strip() and data.phone != employee.phone:
            clean_phone = data.phone.strip()
            existing_phone = self.db.query(Employee).filter(Employee.phone == clean_phone, Employee.id != emp_id).first()
            if existing_phone:
                raise ValueError("Số điện thoại này đã được sử dụng bởi một nhân viên khác!")
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(employee, key, value)

        self.db.commit()
        self.db.refresh(employee)
        return employee

    def update_partial(self, emp_id: int, data: EmployeeUpdate):
        employee = self.db.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            raise ValueError(config.get_message("employee_not_found"))

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("Không có dữ liệu nào được gửi lên để cập nhật!")

        if "fullname" in update_data:
            if not update_data["fullname"] or not update_data["fullname"].strip():
                raise ValueError(config.get_message("empty_name"))
            update_data["fullname"] = update_data["fullname"].strip()

        if "department_id" in update_data and update_data["department_id"] is not None:
            dept_exists = self.db.query(Department).filter(Department.id == update_data["department_id"]).first()
            if not dept_exists:
                raise ValueError(config.get_message("department_not_found"))

        if "email" in update_data and update_data["email"]:
            existing_email = self.db.query(Employee).filter(Employee.email == update_data["email"], Employee.id != emp_id).first()
            if existing_email:
                raise ValueError(config.get_message("email_exists"))

        if "phone" in update_data and update_data["phone"]:
            clean_phone = update_data["phone"].strip()
            if len(clean_phone) < config.MIN_PHONE_LENGTH:
                raise ValueError(config.get_message("phone_invalid"))
            existing_phone = self.db.query(Employee).filter(Employee.phone == clean_phone, Employee.id != emp_id).first()
            if existing_phone:
                raise ValueError("Số điện thoại này đã được sử dụng bởi một nhân viên khác!")
            update_data["phone"] = clean_phone

        for key, value in update_data.items():
            setattr(employee, key, value)

        self.db.commit()
        self.db.refresh(employee)
        return employee

    def update_self(self, emp_id: int, data: EmployeeSelfUpdate):
        allowed_fields = data.model_dump(exclude_unset=True)
        return self.update_partial(emp_id, EmployeeUpdate(**allowed_fields))


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, username: str, password: str, role: str = Role.EMPLOYEE, employee_id: Optional[int] = None):
        if not username or not username.strip():
            raise ValueError(config.get_message("empty_name"))
        if not password or len(password) < 6:
            raise ValueError(config.get_message("password_too_short"))

        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
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
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate(self, username: str, password: str):
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            return None
        return user