from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import json
import os

router = APIRouter(
    prefix="/department",
    tags=["Department"]
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "list_department.txt")


def read_data():
    if not os.path.exists(DB_FILE):
        return []

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


departments = read_data()


def write_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(
            departments,
            f,
            ensure_ascii=False,
            indent=4
        )


class DepartmentCreate(BaseModel):
    department_name: str


class Department(DepartmentCreate):
    id: int


def find_department(dep_id: int):
    for dep in departments:
        if dep["id"] == dep_id:
            return dep
    return None


@router.get("")
def get_departments():
    return departments


@router.post("")
def create_department(data: DepartmentCreate):
    new_id = departments[-1]["id"] + 1 if departments else 1

    new_department = {
        "id": new_id,
        "department_name": data.department_name
    }

    departments.append(new_department)
    write_data()

    return {
        "message": "Thêm phòng ban thành công",
        "department": new_department
    }


@router.get("/{id}")
def get_department(id: int):
    dep = find_department(id)

    if not dep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phòng ban"
        )

    return dep


@router.put("/{id}")
def update_department(id: int, data: DepartmentCreate):
    dep = find_department(id)

    if not dep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phòng ban"
        )

    dep["department_name"] = data.department_name

    write_data()

    return {
        "message": "Cập nhật thành công",
        "department": dep
    }


@router.delete("/{id}")
def delete_department(id: int):
    dep = find_department(id)

    if not dep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phòng ban"
        )

    departments.remove(dep)

    write_data()

    return {
        "message": "Xóa phòng ban thành công"
    }