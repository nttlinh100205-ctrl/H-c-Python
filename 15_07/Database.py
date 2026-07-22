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
    name = Column(Unicode(100), nullable=False)
    description = Column(Unicode(255), nullable=True)

    employees = relationship("Employee", back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(Unicode(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=True)  
    phone = Column(String(20), nullable=True)
    position = Column(Unicode(100), nullable=True)
    salary = Column(Float, nullable=True)
    hire_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="employees")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    leave_type = Column(String(50), nullable=False)  # 'có lương' hoặc 'không lương'
    reason = Column(Unicode(255), nullable=True)
    status = Column(String(20), default="pending")  # pending, approved, rejected

    employee = relationship("Employee", backref="leave_requests")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="employee")
    is_active = Column(Boolean, default=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)


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
            SERVER_NAME = r"DESKTOP-CMHT1RR\SQLEXPRESS"               
            DB_NAME = "HR_Database"
            DRIVER_NAME = "ODBC Driver 17 for SQL Server" 
            
            driver_url = DRIVER_NAME.replace(" ", "+")
            
            DATABASE_URL = (
                f"mssql+pyodbc://@{"DESKTOP-CMHT1RR\SQLEXPRESS"}/{"HR_Database"}"
                f"?driver={driver_url}&Trusted_Connection=yes&TrustServerCertificate=yes"
            )
     
            self._engine = create_engine(
                DATABASE_URL,
                echo=config.get("DB_ECHO", False),      
                poolclass=QueuePool,
                pool_size=config.get("DB_POOL_SIZE", 5),
                max_overflow=config.get("DB_MAX_OVERFLOW", 10),
                fast_executemany=True,
            )
            
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            
            logger.info(f"Database connection initialized: Connected to SQL Server ({"DESKTOP-CMHT1RR\SQLEXPRESS"})")
            
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

database = DatabaseSingleton()