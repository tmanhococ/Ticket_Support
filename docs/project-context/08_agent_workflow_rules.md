# Quy tắc làm việc cho Coding Agent (Agent Workflow Rules)

Tài liệu này chứa các quy tắc BẮT BUỘC mà mọi AI Coding Agent phải tuân thủ khi hỗ trợ viết code, tài liệu hoặc cấu hình cho dự án "Ticket Triage MLOps".

## 1. Source of Truth (Nguồn Sự thật)
- Toàn bộ các file trong thư mục `project-context/` là **Nguồn Sự Thật Tuyệt Đối**.
- AI phải tham chiếu thông tin kiến trúc, data schema, và ràng buộc (constraints) từ thư mục này.
- **KHÔNG ĐƯỢC** tự ý bịa đặt (hallucinate) các data fields, tên bảng, cổng (ports) hay logic không có trong tài liệu.

## 2. Phạm vi Công việc (Scope Rules)
- **Task Siêu Nhỏ**: AI chỉ thực hiện ĐÚNG phạm vi yêu cầu (Micro-task). Nếu được yêu cầu viết `generator.py`, chỉ viết `generator.py`.
- **Không tự ý Refactor**: AI không được tự động sửa code ở các file không liên quan hoặc tự tiện định dạng lại (reformat) dự án trừ khi được yêu cầu rõ ràng.
- **Chống Overengineering**: Nếu có 2 cách giải quyết, LUÔN chọn cách đơn giản nhất, dùng thư viện tiêu chuẩn của Python thay vì cài thêm dependencies nặng nề (ví dụ: dùng `BackgroundTasks` thay vì `Celery`). Mặc dù hệ thống dùng PostgreSQL và Docker từ đầu, cố gắng giữ cấu hình tối giản nhất.

## 3. Quy chuẩn Code (Code Quality & Anti-Drift)
- **Luôn có Unit Tests**: Mọi đoạn logic cốt lõi mới (Pydantic schema, thuật toán sinh dữ liệu, logic xử lý API) đều phải đi kèm file test sử dụng `pytest`.
- **Validation Chặt Chẽ**: Mọi đầu vào API phải sử dụng schema của `Pydantic`.
- **Bắt lỗi (Error Handling)**: Backend không bao giờ được sập (crash) và ném ra HTTP 500 do lỗi dữ liệu. Phải có khối `try-except` và cơ chế fallback (VD: trả về nhãn `manual_review`).
- **Typing & Docstrings**: Bắt buộc sử dụng Type Hints cho Python và viết Docstring ngắn gọn cho các hàm quan trọng.

## 4. Cách sử dụng Context
Khi bắt đầu một phiên làm việc mới:
1. Đọc yêu cầu của User (PO/DevOps).
2. Tự động kiểm tra các file liên quan trong `project-context/` (VD: `02_domain_and_data_contract.md` nếu làm việc với API).
3. Đặt câu hỏi (Open Question) nếu yêu cầu của user mâu thuẫn với `project-context/`.
4. Không bao giờ đưa ra các cấu hình cloud (ví dụ: K8s yaml, Terraform phức tạp) vi phạm nguyên tắc "Minimal Architecture" ở `03_system_architecture.md`.

## 5. Quy tắc Báo cáo Hoàn thành
Sau khi viết code, AI phải:
- Giải thích tóm tắt logic đã thực hiện.
- Liệt kê các lệnh cần chạy để verify (VD: `pytest test_api.py`, `docker-compose build`).
- Cảnh báo nếu thay đổi này có ảnh hưởng tới file khác mà chưa được cập nhật.
