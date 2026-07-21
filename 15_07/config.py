class ConfigSingleton:
    
    _instance = None
    
    def __new__(cls):
        """Đảm bảo chỉ tạo 1 instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_config()
        return cls._instance
    
    def _initialize_config(self):
        """Khởi tạo config một lần duy nhất"""
        
        
        self.API_TITLE = "HR API"
        self.API_DESCRIPTION = "API Quản lý Nhân sự"
        self.API_VERSION = "1.0.0"
        self.API_DOCS_URL = "/docs"
        self.API_OPENAPI_URL = "/openapi.json"
        
        
        self.VALID_GENDERS = ['Nam', 'Nữ', 'Khác']
        self.MIN_AGE = 18
        self.MIN_PHONE_LENGTH = 10
        self.SALARY_DECIMAL_PLACES = 2
        
       
        self.DATE_FORMAT = '%Y-%m-%d'
        self.DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
        
        self.DB_ECHO = True  # Set to True để debug SQL queries
        self.DB_POOL_SIZE = 5
        self.DB_MAX_OVERFLOW = 10
        
        
        self.CSV_FILENAME = "danh_sach_nhan_vien.csv"
        self.CSV_ENCODING = 'utf-8-sig'  # Có BOM cho Excel

        # 🔐 JWT / Authentication
        # ⚠️ SECRET_KEY nên đọc từ biến môi trường khi deploy thật,
        # không hardcode trong source code.
        import os
        self.JWT_SECRET_KEY = os.environ.get(
            "JWT_SECRET_KEY", "hr-api-dev-secret-key-doi-khi-deploy-that"
        )
        self.JWT_ALGORITHM = "HS256"
        self.JWT_EXPIRE_MINUTES = 60  # thời hạn access token: 60 phút

        # 💰 Cấu hình tính lương (theo quy định VN, đơn giản hóa)
        self.INSURANCE_RATE = 0.105  # 10.5% = BHXH 8% + BHYT 1.5% + BHTN 1%
        self.PERSONAL_DEDUCTION = 11_000_000   # giảm trừ bản thân / tháng
        self.DEPENDENT_DEDUCTION = 4_400_000   # giảm trừ mỗi người phụ thuộc / tháng

        # Biểu thuế TNCN lũy tiến từng phần (áp dụng theo ĐỘ RỘNG từng bậc,
        # không phải mốc lũy kế): (độ_rộng_bậc, thuế_suất). width=None -> không giới hạn
        self.PIT_BRACKETS = [
            (5_000_000, 0.05),
            (5_000_000, 0.10),
            (8_000_000, 0.15),
            (14_000_000, 0.20),
            (20_000_000, 0.25),
            (28_000_000, 0.30),
            (None, 0.35),
        ]
        
        # 🔒 Validation Messages
        self.MESSAGES = {
            # Thành công
            "create_department_success": "Tạo phòng ban thành công!",
            "create_employee_success": "Thêm nhân viên '{name}' thành công!",
            "update_employee_success": "Cập nhật nhân viên '{name}' thành công!",
            "delete_employee_success": "Xóa nhân viên '{name}' (ID: {id}) thành công!",
            "export_csv_success": "Xuất CSV thành công: {count} nhân viên",
            
            # Lỗi validate
            "empty_name": "Tên không được để trống!",
            "department_exists": "Phòng ban đã tồn tại!",
            "department_not_found": "Phòng ban không tồn tại!",
            "email_exists": "Email đã được sử dụng!",
            "phone_invalid": f"Số điện thoại phải có ít nhất {10} ký tự!",
            "gender_invalid": f"Giới tính không hợp lệ! Chọn: Nam, Nữ, Khác",
            "salary_invalid": "Lương phải > 0",
            "birthday_format": "Định dạng ngày sinh phải là YYYY-MM-DD (ví dụ: 2000-01-15)",
            "birthday_future": "Ngày sinh không thể trong tương lai!",
            "age_invalid": f"Nhân viên phải ít nhất {18} tuổi!",
            
            # Not found
            "employee_not_found": "Không tìm thấy nhân viên!",
            "no_data": "Không có dữ liệu!",

            # Auth
            "username_exists": "Tên đăng nhập đã tồn tại!",
            "invalid_credentials": "Tên đăng nhập hoặc mật khẩu không đúng!",
            "user_not_found": "Không tìm thấy tài khoản!",
            "permission_denied": "Bạn không có quyền thực hiện thao tác này!",
            "password_too_short": "Mật khẩu phải có ít nhất 6 ký tự!",

            # Server error
            "server_error": "Lỗi server: {error}",
        }
    
    def get(self, key, default=None):
        """Lấy config value"""
        return getattr(self, key, default)
    
    def get_message(self, key, **kwargs):
        """Lấy message và format nếu cần"""
        message = self.MESSAGES.get(key, key)
        if kwargs:
            return message.format(**kwargs)
        return message


# Tạo instance duy nhất
config = ConfigSingleton()