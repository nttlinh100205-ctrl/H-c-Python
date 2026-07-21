from sqlalchemy import create_engine, Column, Integer, String, Unicode, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from sqlalchemy.pool import QueuePool
from .logger import logger
from .config import config
from .exceptions import DatabaseConnectionError

Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    # ✅ Dùng Unicode (map -> NVARCHAR trên SQL Server) để lưu tiếng Việt có dấu đúng
    name = Column(Unicode(100), nullable=False)
    description = Column(Unicode(255), nullable=True)

    # Mối quan hệ: Một phòng ban có nhiều nhân viên
    employees = relationship("Employee", back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    # ✅ Các trường có thể chứa tiếng Việt -> Unicode (NVARCHAR)
    fullname = Column(Unicode(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=True)  # Email luôn ASCII, giữ String
    phone = Column(String(20), nullable=True)  # Phone luôn số, giữ String
    position = Column(Unicode(100), nullable=True)  # ✅ Chức vụ có thể là tiếng Việt
    salary = Column(Float, nullable=True)
    hire_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Khóa ngoại liên kết với bảng departments
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    # Mối quan hệ ngược lại
    department = relationship("Department", back_populates="employees")


class User(Base):
 
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)


class DatabaseSingleton:
    _instance = None
    _engine = None
    _SessionLocal = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_database()
        return cls._instance
    
    def _initialize_database(self):
        try:
            # Thông tin kết nối
            SERVER_NAME = r"DESKTOP-CMHT1RR\SQLEXPRESS"               
            DB_NAME = "HR_Database"
            DRIVER_NAME = "ODBC Driver 17 for SQL Server" 
            
            driver_url = DRIVER_NAME.replace(" ", "+")
            
            # ✅ ĐÃ BỎ "&charset=utf8" - param này KHÔNG hợp lệ với mssql+pyodbc
            # (đó là cú pháp dành cho MySQL). Với NVARCHAR + ODBC Driver 17,
            # Unicode được xử lý tự động, không cần khai báo charset thủ công.
            DATABASE_URL = (
                f"mssql+pyodbc://@{SERVER_NAME}/{DB_NAME}"
                f"?driver={driver_url}&Trusted_Connection=yes&TrustServerCertificate=yes"
            )
     
            self._engine = create_engine(
                DATABASE_URL,
                echo=config.get("DB_ECHO", False),      
                poolclass=QueuePool,
                pool_size=config.get("DB_POOL_SIZE", 5),
                max_overflow=config.get("DB_MAX_OVERFLOW", 10),
                # ✅ fast_executemany giúp pyodbc gửi dữ liệu Unicode ổn định hơn
                fast_executemany=True,
            )
            
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            
            logger.info(f"Database connection initialized: Connected to SQL Server ({SERVER_NAME})")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise DatabaseConnectionError(
                f"Không thể kết nối tới SQL Server: {str(e)}"
            ) from e
    
    def get_engine(self):
        return self._engine
    
    def get_session_local(self):
        return self._SessionLocal
    
    def get_session(self) -> Session:
        return self._SessionLocal()
    
    def get_db(self):
        db = self.get_session()
        try:
            yield db
        finally:
            db.close()
    
    def create_tables(self):
        try:
            Base.metadata.create_all(bind=self._engine)
            logger.info("All tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise DatabaseConnectionError(
                f"Không thể tạo bảng trong cơ sở dữ liệu: {str(e)}"
            ) from e
    
    def drop_tables(self):
        try:
            Base.metadata.drop_all(bind=self._engine)
            logger.warning("All tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop tables: {str(e)}")
            raise

# Tạo instance duy nhất
database = DatabaseSingleton()