# Báo cáo Nghiên cứu: Đánh giá & Thiết kế Kiến trúc Ticket Triage MLOps

Dựa trên tài liệu ngữ cảnh dự án `ticket_triage_ai_context.md` và các ưu tiên: **practical, minimal, educational, production-thinking, AI-agent friendly**, dưới đây là bản đánh giá kỹ thuật và đề xuất kiến trúc.

## 1. Đánh giá Kiến trúc Hiện tại
**Stack hiện tại:** FastAPI, Docker, GitHub Actions, EC2, S3, Streamlit, Python, Local/Staging/Prod.

Kiến trúc này **RẤT PHÙ HỢP** với mục tiêu của dự án:
- **Học MLOps & Production Thinking:** Phủ kín được vòng đời từ Data -> Training -> Model Storage (S3) -> Deployment (EC2/Docker) -> CI/CD (GH Actions) -> UI (Streamlit). Cung cấp đủ trải nghiệm production nhưng không bị rối rắm bởi các cloud-native tools.
- **Sprint ngắn (2-3 ngày) & 1 Developer:** Đây là stack vàng cho "solo dev". Không cần cấu hình K8s hay Terraform phức tạp.
- **AI Coding Workflow:** Các tool này đều cực kỳ phổ biến, AI agent (như Claude, GPT-4, Gemini) viết code FastAPI, Streamlit, GH Actions rất chuẩn xác và ít sinh ra mã lỗi (hallucinations) do syntax rõ ràng.

## 2. Nhận diện Rủi ro: Phức tạp, Chưa đủ, Dễ fail, Overengineering
- **Chưa đủ (Missing piece):** S3 lưu model và raw files là hợp lý, nhưng bạn **cần một Database có cấu trúc** để lưu trạng thái của ticket (ví dụ: `ticket_id, status, predicted_class, true_class`). S3 không hỗ trợ truy vấn hiệu quả để vẽ dashboard trên Streamlit. (Nên thêm SQLite hoặc Postgres).
- **Dễ fail (Brittleness):** Triển khai trực tiếp lên EC2 bằng SSH qua GH Actions rất dễ lỗi mạng giữa chừng hoặc lỗi phân quyền. Cần chuẩn hóa bằng `docker-compose`.
- **Dễ overengineering:** Cố gắng xây dựng streaming real-time (WebSockets) từ FastAPI sang UI, hoặc tạo hệ thống event-driven phức tạp ngay từ Sprint 1.

## 3. Có nên sử dụng các công cụ mở rộng?

| Công cụ | Đánh giá | Quyết định cho dự án này |
| :--- | :--- | :--- |
| **Airflow** | Overkill. Cấu hình nặng, khó quản lý cho 1 dev. | ❌ **KHÔNG**. Dùng Cron job hoặc Script Python (Github Actions) để trigger train định kỳ. |
| **MLflow** | Phù hợp. Standard của MLOps. Tracking tốt. | ✅ **CÓ**. Cài MLflow backend SQLite + S3 artifact store. AI code rất tốt với thư viện `mlflow`. |
| **Kafka** | Overkill. Tăng độ phức tạp vận hành lên 300%. | ❌ **KHÔNG**. Chỉ dùng HTTP POST API từ simulator tới FastAPI. |
| **Celery/Redis**| Async queue tốt, nhưng Sprint 1 chưa cần. | ⚖️ **CÓ THỂ (Sau này)**. Ban đầu dùng `BackgroundTasks` của FastAPI là đủ. |
| **Postgres** | Rất tốt cho production. | ✅ **CÓ**. Chạy bằng Docker container chung với app. |
| **Feature Store**| Overkill. Text data không cần lưu trữ feature phức tạp. | ❌ **KHÔNG**. Dùng S3 lưu raw + processed text là đủ. |

## 4. Đề xuất Kiến trúc

### A. Minimal Architecture (Sprint 1 - Skeleton)
- **Intake & Inference:** 1 service `FastAPI`.
- **Database:** `SQLite` lưu local.
- **UI:** `Streamlit`.
- **Deployment:** Chạy Docker-compose với 2 container (FastAPI + Streamlit) trên 1 EC2. Dữ liệu mount ra volume.

### B. Recommended Architecture (Mục tiêu cuối)
- **Backend:** `FastAPI` (Inference API + Data Intake).
- **Database:** `PostgreSQL` (Lưu trạng thái tickets + metadata).
- **Storage:** `AWS S3` (Lưu Raw JSON tickets + ML Models Artifacts).
- **Model Tracking:** `MLflow` chạy trên 1 container riêng (hoặc dùng Managed MLflow nếu có).
- **UI:** `Streamlit`.
- **Deployment:** 1 máy EC2 lớn, cài `docker-compose` chứa: FastAPI, Postgres, Streamlit, MLflow. Môi trường Staging và Prod có thể là 2 folder khác nhau (hoặc 2 EC2 nhỏ).

### C. Advanced Optional (Thử thách thêm)
- Tách `Intake API` và `Inference API` thành 2 microservices. Intake lưu data vào DB, sau đó trigger job suy luận bất đồng bộ (Celery + Redis).
- Thêm `Prometheus + Grafana` để monitor system & metrics.

## 5. Đề xuất CI/CD Workflow (Thực tế & Minimal)
Dùng **GitHub Actions** làm xương sống:
1. **CI (Continuous Integration):** Trigger khi tạo PR hoặc push lên `main` / `staging`.
   - Checkout code.
   - Setup Python, run `flake8`/`black` (AI friendly).
   - Run `pytest` (Unit tests cho API và Data schemas).
   - Build Docker Image và Push lên GitHub Container Registry (GHCR).
2. **CD (Continuous Deployment):** Trigger khi CI pass.
   - SSH bằng Github Secrets vào EC2 Staging/Prod.
   - Run `docker pull ghcr.io/...:latest`.
   - Run `docker-compose up -d`.
   - Run `curl http://localhost/health` để verify.

## 6. Đề xuất Monitoring Strategy (Tối thiểu)
- **Data Drift:** Định kỳ hàng ngày (qua cron job), quét data mới trong Postgres/S3, chạy tool `EvidentlyAI` so sánh với data train. Xuất HTML Report lưu vào S3 và render lên Streamlit.
- **Model Monitoring:** Theo dõi phân phối của các class được dự đoán (`low`, `medium`, `high`). Nếu tỷ lệ một class vượt ngưỡng đột biến (VD: 90% vé thành `high`), gửi cảnh báo (Slack webhook / Telegram bot).
- **System Monitoring:** Cấu hình FastAPI logging để ghi nhận độ trễ (latency), số request (throughput), tỷ lệ lỗi (500 errors).

## 7. Đề xuất Model Versioning Strategy
- Mọi model train xong đều được ghi nhận (logged) vào **MLflow**.
- Khi model đạt chất lượng, gắn tag (Promote) thành `Staging`. Sau khi shadow deploy ổn, đổi tag thành `Production`.
- Service FastAPI khi khởi động sẽ gọi MLflow API (hoặc download từ S3 path cố định) phiên bản model đang có tag `Production`.
- **AI-agent friendly tip:** AI dễ code việc đọc config `model_version: "production"` và tự động pull từ MLflow/S3 mà không cần logic code lại đường dẫn mỗi lần có model mới.

## 8. Đề xuất Rollback / Fallback Strategy
- **Fallback (Code/Logic):** Bắt buộc phải có trong FastAPI. Nếu quá trình load model thất bại, hoặc model trả lỗi do input lạ, API trả về nhãn mặc định là `manual_review` hoặc rule-based đơn giản (nếu chứa từ "urgent" -> `high`) để hệ thống ko sập.
- **Rollback Deployment (Docker):** Nếu bản deploy mới gây lỗi hệ thống (healthcheck fail), vào Github Actions chạy lại Job CD của tag/commit trước đó. `docker-compose` sẽ kéo lại image cũ.
- **Rollback Model:** Nếu model mới bị sai lệch (data drift nặng), chỉ cần đổi tag `Production` về version cũ trên giao diện MLflow, sau đó trigger webhook gọi API `/reload-model` của FastAPI để load lại model.

---
> [!IMPORTANT]
> **Nhận xét Tổng thể cho Sprint Planning:**
> Để đạt được điều này theo Sprint, bạn cần chia nhỏ dứt điểm. Không setup DB Postgres hay MLflow ở Sprint 1. Hãy làm Minimal Architecture (SQLite, không MLflow, Dummy Model) ở Sprint 1, sau đó nâng cấp lên Recommended Architecture ở Sprint 2.
