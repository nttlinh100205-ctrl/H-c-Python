

class DatabaseOperationError(Exception):
    """Base exception cho mọi lỗi liên quan tới thao tác database.
    Mọi custom exception khác trong file này nên kế thừa từ đây,
    để main.py có một 'lưới an toàn' (fallback handler) bắt được hết."""

    def __init__(self, message: str = "Lỗi thao tác cơ sở dữ liệu"):
        self.message = message
        super().__init__(self.message)


class DuplicateKeyError(DatabaseOperationError):
    """Raise khi dữ liệu bị trùng khóa (vd: email, tên phòng ban đã tồn tại)."""

    def __init__(self, message: str = "Dữ liệu đã tồn tại, không thể tạo trùng"):
        super().__init__(message)


class ForeignKeyReferenceError(DatabaseOperationError):
    """Raise khi khóa ngoại tham chiếu tới bản ghi không tồn tại
    (vd: department_id không có trong bảng departments)."""

    def __init__(self, message: str = "Khóa ngoại tham chiếu không hợp lệ"):
        super().__init__(message)


class RequiredFieldError(DatabaseOperationError):
    """Raise khi thiếu trường bắt buộc (vi phạm NOT NULL ở tầng DB)."""

    def __init__(self, message: str = "Thiếu trường dữ liệu bắt buộc"):
        super().__init__(message)


class InvalidDataTypeError(DatabaseOperationError):
    """Raise khi dữ liệu sai kiểu (vd: truyền chữ vào cột số, ngày sai định dạng ở tầng DB)."""

    def __init__(self, message: str = "Kiểu dữ liệu không hợp lệ"):
        super().__init__(message)


class DatabaseIntegrityError(DatabaseOperationError):
   

    def __init__(self, message: str = "Vi phạm ràng buộc toàn vẹn dữ liệu"):
        super().__init__(message)


class DatabaseConnectionError(DatabaseOperationError):
  

    def __init__(self, message: str = "Không thể kết nối tới cơ sở dữ liệu"):
        super().__init__(message)