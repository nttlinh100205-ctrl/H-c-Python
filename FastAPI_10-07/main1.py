from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

students = []

class Student(BaseModel):
    name: str
    age: int

# Read
@app.get("/students")
def get_students():
    return students

# Create
@app.post("/students")
def create_student(student: Student):
    students.append(student)
    return {"message": "Thêm thành công", "data": student}

# Update
@app.put("/students/{id}")
def update_student(id: int, student: Student):
    students[id] = student
    return {"message": "Cập nhật thành công"}

# Delete
@app.delete("/students/{id}")
def delete_student(id: int):
    students.pop(id)
    return {"message": "Đã xóa"}