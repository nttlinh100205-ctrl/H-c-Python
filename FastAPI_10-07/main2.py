from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

app = FastAPI()


DB_FILE = "test.txt"

def read_data():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def write_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class StudentCreate(BaseModel):
    name: str
    age: int

class StudentResponse(BaseModel):
    id: int
    name: str
    age: int



@app.get("/student")
def ds_nv():
    # Đọc dữ liệu từ file txt
    students_list = read_data()
    return {"message": "Thành công", "data": students_list}

@app.post("/student")
def them_nv(student_input: StudentCreate):
    students_list = read_data()
    
    # Tự động tạo ID dựa trên dữ liệu hiện có trong file
    if len(students_list) > 0:
        new_id = students_list[-1]["id"] + 1
    else:
        new_id = 1
        
    new_student = {
        "id": new_id,
        "name": student_input.name,
        "age": student_input.age
    }
    
    students_list.append(new_student)
    write_data(students_list)
    
    return {"message": "Thêm thành công", "data": new_student}

@app.put("/student/{student_id}")
def update_student(student_id: int, student_update: StudentCreate):
    students_list = read_data()
    
  
    for item in students_list:
        if item["id"] == student_id:  
            item["name"] = student_update.name
            item["age"] = student_update.age  
            
            write_data(students_list) 
            return {"message": "Cập nhật thành công", "data": item}
            
    raise HTTPException(status_code=404, detail="Không tìm thấy ID")

@app.delete("/student/{student_id}") 
def delete_student(student_id: int):
    students_list = read_data()
    
    for i, item in enumerate(students_list):
        if item["id"] == student_id:
            students_list.pop(i) 
            write_data(students_list) 
            return {"message": f"Đã xóa học sinh có ID {student_id}"}
            
    raise HTTPException(status_code=404, detail="Không tìm thấy học sinh với ID này")