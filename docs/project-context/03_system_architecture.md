# Kiến trúc Hệ thống (System Architecture)

## 1. Kiến trúc Tổng quan (Minimal & Practical)
Hệ thống tuân theo nguyên tắc "Pragmatic Architecture" – đủ chức năng MLOps nhưng không phức tạp hóa bằng công cụ cloud-native cồng kềnh.

**Stack cốt lõi:**
- Backend/Inference: **FastAPI**
- Database: **PostgreSQL** (triển khai bằng Docker ngay từ Sprint 1)
- Frontend/Dashboard: **Streamlit**
- Storage: **AWS S3** (Raw tickets, Model Artifacts, HTML Reports)
- Model Tracking: **MLflow**
- Containerization: **Docker & docker-compose**
- CI/CD: **GitHub Actions**

## 2. Phân vai Môi trường (Roles)
- **Local (Developer Machine)**: Dùng để viết code, chạy unit test, chạy các container cục bộ (`docker-compose up`) để phát triển.
- **GitHub**: Lưu trữ source code, quản lý issue/sprint, thực thi CI/CD pipeline, và đóng vai trò là Container Registry (GHCR).
- **AWS (S3 & EC2)**:
  - **EC2**: 2 server chạy song song, 1 cho môi trường Staging và 1 cho Production. Cài Docker, làm host chạy các service (FastAPI, UI, Database).
  - **S3**: Lưu trữ các dữ liệu tĩnh không phù hợp lưu trên RDBMS (như Raw JSON, model files `.pkl`/`.onnx`, report Evidently).

## 3. Các Components Chính
1. **Stream Simulator**: Docker container chạy local (máy cá nhân) để bắn request lên server EC2. Định kỳ sinh ticket và gọi POST API. Hỗ trợ "Drift Profiles".
2. **FastAPI Service**: Cung cấp cả Intake endpoint (`/tickets`) và Inference logic. Lưu trữ ticket xuống Database.
3. **Database (DB)**: Lưu trạng thái xử lý của ticket (ID, content, predicted_priority, timestamp).
4. **MLflow Service**: Container riêng biệt theo dõi model experiments, versioning và metrics.
5. **Drift Monitor (Cron Job)**: Script chạy định kỳ (VD: mỗi 24h), sử dụng EvidentlyAI so sánh data trong DB với reference data, xuất HTML report lưu vào S3.
6. **Streamlit UI**: Giao diện đọc data trực tiếp từ DB để hiển thị dashboard và nhúng báo cáo từ S3.

## 4. Tương tác Dữ liệu (Component Interactions)
```text
[Stream Simulator] --(POST JSON)--> [FastAPI Intake/Inference]
                                      |--> (Lưu trạng thái) --> [Database]
                                      |--> (Lưu raw data) --> [AWS S3]
                                      |--> (Pull Model) <-- [MLflow / S3]

[Cron Job: Train] --(Đọc Data)--> [Database/S3] --(Log Model)--> [MLflow]
[Cron Job: Drift] --(Đọc Data)--> [Database] --(Lưu Report)--> [AWS S3]

[Streamlit Dashboard] --(Đọc Data)--> [Database]
                      --(Hiển thị)--> [AWS S3 Reports]
```

## 5. Giới hạn & Quyết định Kiến trúc
- ❌ **KHÔNG Kafka/RabbitMQ**: Việc xếp hàng (queueing) được xử lý đồng bộ qua API hoặc `BackgroundTasks` của FastAPI ở mức độ nhỏ.
- ❌ **KHÔNG Airflow/Prefect**: Lập lịch bằng Cron đơn giản trên EC2 hoặc GitHub Actions scheduled workflows.
- ❌ **KHÔNG K8s**: Triển khai hoàn toàn bằng `docker-compose`.
