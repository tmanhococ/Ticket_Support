# Lộ trình Sprint (Sprint Map)

Dự án áp dụng Scrum với các vòng lặp cực ngắn (2-3 ngày/sprint), tập trung giải quyết dứt điểm các thành phần nhỏ, tuân thủ nguyên lý Walking Skeleton (có end-to-end càng sớm càng tốt).

## Sprint 1: Foundation, Data, Skeleton Product
**Sprint Goal:** Xây dựng nền móng cơ sở hạ tầng, đảm bảo hệ thống có thể tiếp nhận dữ liệu liên tục, lưu trữ được và luồng CI/CD cơ bản hoạt động. Chưa có mô hình ML.

**Epics & Deliverables:**
- **Epic 1: Ticket intake và data contract**: Xây dựng FastAPI `POST /tickets`, Pydantic validation, lưu dữ liệu vào PostgreSQL.
- **Epic 2: Stream simulator**: Script `generator.py` và `producer.py` sinh ticket giả lập (hỗ trợ cấu trúc Drift Profile).
- **Epic 3: Walking skeleton CI/CD**: Thiết lập GitHub Actions lint, test, build Docker image, và deploy lên 1 EC2 server.
- **Epic 4: Product placeholder**: Dựng UI Streamlit tối giản kết nối PostgreSQL để hiển thị danh sách ticket.

**Dependency:** Cần setup AWS EC2 và GitHub Secrets trước khi đóng Sprint 1.

---

## Sprint 2: Model + Shadow + Versioning
**Sprint Goal:** Đưa Machine Learning vào hệ thống một cách có kiểm soát, áp dụng MLflow và chiến lược Shadow Deployment.

**Epics & Deliverables:**
- **Epic 5: Setup & Optimize Storage**: Tối ưu hoá connection pool của PostgreSQL, thiết lập cấu trúc lưu trữ S3 chuẩn phục vụ model artifact.
- **Epic 6: Baseline Model Training**: Viết pipeline train text classification đơn giản.
- **Epic 7: MLflow Tracking**: Tích hợp MLflow server lưu trữ model artifact và parameters.
- **Epic 8: Shadow Inference**: Cập nhật FastAPI load model từ MLflow, dự đoán ngầm và lưu `predicted_priority` vào DB.

**Dependency:** Hệ thống CI/CD ở Sprint 1 phải ổn định mới có thể cập nhật kiến trúc (thêm DB, thêm MLflow container) mượt mà.

---

## Sprint 3: Monitoring + Rollback + Polish
**Sprint Goal:** Hoàn thiện tư duy Production với cơ chế giám sát rủi ro (Observability) và an toàn hệ thống (Fallback/Rollback).

**Epics & Deliverables:**
- **Epic 9: Data Drift Detection**: Viết cron job dùng EvidentlyAI phân tích data trong Postgres so sánh với baseline, đẩy report lên S3.
- **Epic 10: Fail-safe Mechanisms**: Viết logic Fallback trong FastAPI, cơ cấu Rollback model qua API.
- **Epic 11: Dashboard Polish**: Tích hợp HTML report của EvidentlyAI vào Streamlit Dashboard, hoàn thiện giao diện cho Support Lead.
- **Epic 12: Incident Drill (Tùy chọn)**: Kích hoạt Drift trên Simulator và ghi nhận phản ứng hệ thống (Postmortem giả lập).

**Dependency:** Cần S3 Bucket được cấp quyền để upload reports. Model phải chạy trơn tru ở Sprint 2.
