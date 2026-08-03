import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

class ExcelExporter:
    
    @staticmethod
    def export_employees(employees):
        """
        Hàm xuất danh sách nhân viên ra Excel (Giữ nguyên logic cũ)
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Danh sach nhan vien"

        # 1. Tạo Header
        headers = ["Mã NV", "Họ Tên", "Email", "Số điện thoại", "Phòng ban", "Lương cơ bản", "Trạng thái"]
        ws.append(headers)

        # In đậm và căn giữa Header
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        # 2. Đổ dữ liệu nhân viên vào
        for emp in employees:
            ws.append([
                emp.id,
                emp.fullname,
                emp.email,
                emp.phone,
                emp.department.name if emp.department else "N/A",
                emp.salary,
                "Đang làm việc" if emp.is_active else "Đã nghỉ việc"
            ])

        # 3. Tự động căn chỉnh độ rộng cột cho đẹp
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter 
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            ws.column_dimensions[column].width = max_length + 2

        # 4. Lưu ra BytesIO để trả về qua StreamingResponse
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @staticmethod
    def export_payroll(records, year: int, month: int):
        """
        Hàm mới: Xuất bảng lương hàng tháng ra Excel
        """
        wb = Workbook()
        ws = wb.active
        ws.title = f"Bang_Luong_T{month}_{year}"

        # 1. Tạo Header
        headers = [
            "Mã NV", "Họ Tên", "Năm", "Tháng", 
            "Lương Cơ Bản", "Ngày Công Chuẩn", 
            "Nghỉ Có Lương", "Nghỉ Không Lương", "Thực Nhận"
        ]
        ws.append(headers)

        # In đậm và căn giữa Header
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        # 2. Đổ dữ liệu lương vào
        for r in records:
            ws.append([
                r.employee_id,
                r.employee.fullname if r.employee else "N/A",  # Gọi relationship để lấy tên
                r.year,
                r.month,
                r.gross_salary,
                r.standard_work_days,
                r.paid_leave_days,
                r.unpaid_leave_days,
                r.net_salary
            ])

        # 3. Tự động căn chỉnh độ rộng cột
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter 
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            ws.column_dimensions[column].width = max_length + 2

        # 4. Lưu ra BytesIO
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output