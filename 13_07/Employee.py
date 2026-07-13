from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from datetime import date
import json
import os
from .Department import router as department_router

app = FastAPI(title="HR Management",tags=["Employee"])

app.include_router(department_router)

DB_FILE = "list_employee.txt"


def read_data():
    if not os.path.exists(DB_FILE):
        return []

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def write_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(
            jsonable_encoder(employees),
            f,
            ensure_ascii=False,
            indent=4
        )


class EmployeeCreate(BaseModel):
    fullname: str
    birth_date: date
    gender: str
    number_phone: int
    email: str
    department_id :int


class Employee(EmployeeCreate):
    id: int

employees = [Employee(**emp) for emp in read_data()]


def find_employee(emp_id: int):
    for emp in employees:
        if emp.id == emp_id:
            return emp
    return None


@app.get("/employee",tags=["Employee"])
def get_employee():
    return employees


@app.post("/employee",tags=["Employee"])
def post_employee(emp: EmployeeCreate):
    new_id = employees[-1].id + 1 if employees else 1

    new_emp = Employee(id=new_id, **emp.model_dump())

    employees.append(new_emp)

    write_data()

    return {
        "message": "Thêm thành công",
        "employee": new_emp
    }


@app.get("/employee/{id}",tags=["Employee"])
def employee_details(id: int):
    emp = find_employee(id)

    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy nhân viên"
        )

    return emp


@app.put("/employee/{id}",tags=["Employee"])
def update_employee(id: int, data: EmployeeCreate):
    emp = find_employee(id)

    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy nhân viên để cập nhật"
        )

    emp.fullname = data.fullname
    emp.birth_date = data.birth_date
    emp.gender = data.gender
    emp.number_phone = data.number_phone
    emp.email = data.email
    emp.department_id = data.department_id

    write_data()

    return {
        "message": "Cập nhật thành công",
        "employee": emp
    }


@app.delete("/employee/{id}",tags=["Employee"])
def delete_employee(id: int):
    emp = find_employee(id)

    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy nhân viên để xóa"
        )

    employees.remove(emp)

    write_data()

    return {
        "message": "Xóa thành công"
    }