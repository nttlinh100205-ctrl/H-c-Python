import logging
import sys
from pathlib import Path

class LoggerSingleton:
    """Singleton pattern cho Logger"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        self._logger = logging.getLogger("HR_API")
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()
        
        file_handler = logging.FileHandler(log_dir / f"app.log", encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        for stream in (sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                try:
                    stream.reconfigure(encoding="utf-8", errors="replace")
                except Exception:
                    pass
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
        
        self._logger.info("=" * 70)
        self._logger.info(" HR API khởi động")
        self._logger.info("=" * 70)
    
    def get_logger(self):
        return self._logger
    
    def info(self, message):
        self._logger.info(f" {message}")
    
    def warning(self, message):
        self._logger.warning(f" {message}")
    
    def error(self, message):
        self._logger.error(f" {message}")
    
    def debug(self, message):
        self._logger.debug(f" {message}")

    # ----------------------------------------------------------------------
    # CÁC HÀM GHI LOG CHUYÊN BIỆT CHO BUSINESS LOGIC
    # ----------------------------------------------------------------------
    def log_salary_calculation(self, emp_id: int, year: int, month: int, standard_days: int, 
                               paid_leave: int, unpaid_leave: int, actual_paid: int, actual_gross: float):
        """Log quá trình tính lương"""
        self.info(
            f"[SalaryCalc] emp_id={emp_id}, period={year}-{month:02d}: "
            f"standard_days={standard_days}, paid_leave_days={paid_leave}, "
            f"unpaid_leave_days={unpaid_leave}, actual_paid_days={actual_paid}, "
            f"actual_gross={actual_gross}"
        )

    def log_unknown_leave_type(self, original_value: str, normalized_value: str):
        """Log khi phát hiện loại nghỉ phép không xác định"""
        self.warning(f"Unknown leave_type: '{original_value}' -> normalized to '{normalized_value}'")

    def log_leave_request_normalization(self, original_value: str, normalized_value: str):
        """Log kết quả chuẩn hóa đơn nghỉ phép"""
        self.debug(f"LeaveRequest: normalized '{original_value}' -> '{normalized_value}'")


# Tạo instance duy nhất
logger = LoggerSingleton()