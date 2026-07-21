import logging
import sys
from pathlib import Path
from datetime import datetime


class LoggerSingleton:
    """Singleton pattern cho Logger"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        """Đảm bảo chỉ tạo 1 instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """Khởi tạo logger một lần duy nhất"""
        # Tạo folder logs nếu chưa có
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Tạo logger
        self._logger = logging.getLogger("HR_API")
        self._logger.setLevel(logging.DEBUG)
        
        # Clear handlers cũ (nếu có)
        self._logger.handlers.clear()
        
        # File handler - ghi vào file (UTF-8 để lưu tiếng Việt đúng)
        file_handler = logging.FileHandler(
            log_dir / f"app.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # ✅ FIX LỖI TIẾNG VIỆT TRÊN CONSOLE:
        # Trên Windows, console mặc định dùng codepage cp1252/cp850,
        # không hiển thị đúng ký tự Unicode (tiếng Việt có dấu).
        # Ép sys.stdout/sys.stderr sang UTF-8 nếu Python hỗ trợ (>=3.7).
        for stream in (sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                try:
                    stream.reconfigure(encoding="utf-8", errors="replace")
                except Exception:
                    pass
        
        # Console handler - hiển thị console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Thêm handlers
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
        
        self._logger.info("=" * 70)
        self._logger.info(" HR API khởi động")
        self._logger.info("=" * 70)
    
    def get_logger(self):
        """Lấy logger instance"""
        return self._logger
    
    def info(self, message):
        """Log info level"""
        self._logger.info(f" {message}")
    
    def warning(self, message):
        """Log warning level"""
        self._logger.warning(f" {message}")
    
    def error(self, message):
        """Log error level"""
        self._logger.error(f" {message}")
    
    def debug(self, message):
        """Log debug level"""
        self._logger.debug(f" {message}")


# Tạo instance duy nhất
logger = LoggerSingleton()