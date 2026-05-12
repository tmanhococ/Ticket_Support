# Rủi ro, Giả định và Câu hỏi Mở

Tài liệu này lưu trữ các điểm chưa chắc chắn, các giả định đã đưa ra và rủi ro tiềm ẩn để theo dõi trong suốt quá trình thực thi Sprint.

## 1. Giả định (Assumptions)
- **Về Dữ liệu**: Dữ liệu thật có format bám sát mô tả trong `data_info.md` (bao gồm `subject`, `body`, `queue`, `priority`, `language`, `type`). Nhãn phân loại sẽ chuẩn hoá về `low`, `medium`, `high`.
- **Về Hạ tầng**: Cấu hình 2 server AWS EC2 song song (Staging và Production, loại t2.micro/t3.micro), OS Ubuntu. Ngân sách khả dụng khoảng 20-30$, cần có cảnh báo cho các thao tác tiêu tốn nhiều credit. Tài khoản AWS cấu hình IAM Access Keys để CI/CD kết nối cho nhanh và đơn giản thay vì OIDC.
- **Về User Base**: Hệ thống chỉ phục vụ cho 1 Engineer đóng nhiều vai, không cần xử lý hàng ngàn request đồng thời (Concurrent loads), do đó 1 instance FastAPI + Docker là dư sức đáp ứng.
- **Về Mô hình (Model)**: Bài toán Text Classification bằng các kỹ thuật cơ bản (TF-IDF + Logistic Regression/SVM hoặc LightGBM) là đủ tốt làm baseline, có thể train bằng CPU nhanh chóng.

## 2. Rủi ro (Risks)
- **Rủi ro Cấu hình CI/CD (Brittleness)**: SSH từ GitHub Actions vào EC2 dễ thất bại do cấu hình mạng/Firewall/Key pair. *Mitigation: Chạy thử kết nối SSH Action ngay đầu Sprint 1.*
- **Rủi ro Overengineering**: Developer hoặc AI Agent sa đà vào việc dùng các công cụ thừa thãi (như dựng Kafka, dùng LLM siêu nặng để phân loại ngay từ đầu). *Mitigation: Tuân thủ chặt chẽ Nguồn Sự thật tại `08_agent_workflow_rules.md`.*
- **Rủi ro Mất Mát Dữ liệu**: Dùng PostgreSQL bằng Docker, nếu xóa container mà không mount volume đúng sẽ mất data. *Mitigation: Cấu hình mount volume chuẩn từ thư mục host cho database.*
- **Rủi ro Data Drift Simulator**: Việc sinh ngẫu nhiên có thể không tạo ra sự phân phối ý nghĩa nếu cấu hình weight sai. *Mitigation: Có file test thống kê phân phối sinh ra trước khi chạy thật.*
