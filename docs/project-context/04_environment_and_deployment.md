# Môi trường và Triển khai (Environment & Deployment)

## 1. Các Môi trường (Environments)
- **Local**: Môi trường phát triển trên máy cá nhân. Mọi code phải chạy được thông qua `docker-compose up` để đảm bảo tính đồng nhất.
- **Staging**: Môi trường tiền sản xuất trên máy EC2 riêng rẽ. Dùng để CI/CD tự động test bản build mới, kiểm tra tích hợp với DB, S3 thực tế trước khi lên Production.
- **Production**: Môi trường thực thi cuối cùng trên máy EC2 thứ 2.

## 2. Vai trò chạy Service (What runs where)
Trên AWS EC2 (thông qua Docker-compose):
- Container 1: FastAPI (Backend)
- Container 2: Streamlit (UI)
- Container 3: PostgreSQL (Database)
- Container 4: MLflow Server (Tracking)

Simulator được đóng gói thành một Docker container, ban đầu sẽ chạy trên môi trường Local để đóng vai trò client liên tục bắn request lên hệ thống trên EC2.

## 3. Luân chuyển Artifacts (Artifact Destiny)
- **Source Code**: Nằm trên GitHub.
- **Docker Images**: Sau khi CI pass, image được push lên **GitHub Container Registry (GHCR)**.
- **Machine Learning Models**: Lưu trữ file nhị phân (VD: `.pkl`) trên **AWS S3**.
- **Model Metadata**: Tracking URI trỏ về **MLflow SQLite Backend** hoặc Postgres nội bộ.
- **Data Drift Reports**: Định dạng `.html` xuất ra từ EvidentlyAI được đẩy lên **AWS S3**.

## 4. Mục tiêu Triển khai (Deploy Target)
- 2 servers **AWS EC2** (1 cho Staging, 1 cho Production, tối thiểu t2.micro hoặc t3.small tuỳ cấu hình bộ nhớ).
- OS: Ubuntu.
- Tool yêu cầu: Docker, Docker-compose.
- Triển khai thông qua SSH tự động từ GitHub Actions.

## 5. Cơ chế Rollback / Fallback
### Fallback (Logic Cấp độ Code)
Nếu model tải thất bại, hoặc model ném lỗi do input không xác định (out-of-vocabulary), API phải được bao bọc (try-except) để không bao giờ HTTP 500.
Thay vào đó, API trả về nhãn `predicted_priority: "manual_review"` hoặc sử dụng rule-based fallback (VD: nếu text có chữ "urgent" -> `high`).

### Rollback Model
Nếu model mới (tag `Production`) gặp Data Drift nghiêm trọng hoặc dự đoán sai lệch, Engineer vào MLflow UI đổi tag `Production` cho model cũ, sau đó gọi webhook `/reload-model` của FastAPI để reload mà không cần tắt server.

### Rollback Code/Deployment
Nếu commit mới làm sập ứng dụng (Container healthcheck failed), vào GitHub Actions kích hoạt lại Job Deploy của commit trước đó. Docker-compose sẽ pull image cũ và restart.
