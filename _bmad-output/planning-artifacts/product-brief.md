# Product Brief: Ticket Triage MLOps

## 1. Product Vision
Xây dựng một hệ thống phân loại ticket hỗ trợ khách hàng (Ticket Triage) sát với thực tế vận hành doanh nghiệp nhất có thể. Dự án không tập trung vào độ chính xác tuyệt đối của model, mà đóng vai trò như một môi trường "thực chiến thu nhỏ" để rèn luyện tư duy MLOps, làm việc theo quy trình Scrum, và phối hợp hiệu quả với AI Coding Agent, đảm bảo tính thực dụng và chống overengineering.

## 2. Problem Statement
Hầu hết các dự án ML cá nhân hoặc bài tập học thuật chỉ dừng lại ở việc train model trong Jupyter Notebook. Khi bước ra môi trường thực tế, kỹ sư thường lúng túng trước các vấn đề về data stream, deployment, CI/CD, shadow testing, monitoring (data drift), và cơ chế phòng ngừa rủi ro (fallback/rollback). Dự án này giải quyết bài toán thiếu hụt "tư duy production" bằng cách tạo ra một hệ thống end-to-end, buộc người thực hiện phải tư duy như một team thực thụ (PO, SM, DevOps) và quản lý rủi ro trên môi trường mô phỏng.

## 3. User Personas
- **Support Agent**: Người gửi các ticket cần phân loại (thông qua hệ thống giả lập).
- **Support Lead**: Cần một dashboard để theo dõi lượng ticket đổ về và tình trạng của hệ thống.
- **Product Owner (PO)**: Định nghĩa mục tiêu, viết user stories và nghiệm thu kết quả.
- **Scrum Master (SM)**: Tổ chức sprint, gỡ rối (blocker) và đảm bảo tiến độ.
- **DevOps / MLOps Engineer**: Chịu trách nhiệm thiết kế kiến trúc, cấu hình CI/CD, theo dõi hệ thống.
- **AI Coding Agent**: "Lập trình viên AI" hỗ trợ viết code, viết test theo quy tắc chặt chẽ.

## 4. Goals / Non-goals
**Goals:**
- Mô phỏng hoàn chỉnh vòng đời MLOps: từ data intake, validation, training, deploy đến monitoring và rollback.
- Áp dụng các nguyên tắc Scrum thực tế vào một dự án cá nhân (sprint ngắn 2-3 ngày).
- Rèn luyện kỹ năng quản lý và kiểm soát AI Coding Agent để tránh hiện tượng trôi dạt (hallucination/drift) trong code.
- Tư duy production-first: luôn có test, có log, có cơ chế an toàn.

**Non-goals:**
- Không theo đuổi state-of-the-art model (SOTA); model đơn giản/dummy là đủ ở giai đoạn đầu.
- Không sử dụng các công cụ cloud-native quá phức tạp (như Kubernetes, Kafka, Airflow) gây cồng kềnh không cần thiết.
- Không xây dựng UI/UX quá cầu kỳ, chỉ cần Streamlit dashboard tối giản.

## 5. MVP Scope
- Hệ thống tiếp nhận ticket (Intake API) qua FastAPI với validation rõ ràng.
- Bộ mô phỏng dữ liệu (Stream Simulator) có khả năng sinh ticket ngẫu nhiên theo thời gian và giả lập hiện tượng Data Drift.
- Pipeline CI/CD qua GitHub Actions để tự động test và deploy.
- Môi trường triển khai đóng gói bằng Docker & docker-compose trên một EC2 server.
- Giao diện giám sát tối giản (Streamlit).
- Một model baseline phân loại ticket theo 3 mức độ: `low`, `medium`, `high`.

## 6. Sprint Roadmap
- **Sprint 1: Foundation, Data, Skeleton Product**
  - Xây dựng API tiếp nhận ticket (FastAPI) & Data Contracts.
  - Viết Stream Simulator với cấu trúc hỗ trợ Drift.
  - Thiết lập Walking Skeleton CI/CD (GitHub Actions -> Docker -> EC2).
  - Tạo giao diện Streamlit cơ bản hiển thị ticket (dùng SQLite).
- **Sprint 2: Model + Shadow + Versioning**
  - Huấn luyện baseline model & versioning qua MLflow.
  - Tích hợp PostgreSQL thay thế SQLite.
  - Đẩy code shadow deploy model lên môi trường mô phỏng để đánh giá.
- **Sprint 3: Monitoring + Rollback + Polish**
  - Triển khai Data Drift Detection (EvidentlyAI).
  - Cấu hình alerting cơ bản & cơ chế Fallback/Rollback an toàn.
  - Hoàn thiện UI Dashboard và giả lập tình huống sự cố (Incident Postmortem).

## 7. Architecture Summary
- **Backend/Intake**: FastAPI (Inference & Data Intake).
- **Database**: SQLite (Sprint 1) chuyển dần lên PostgreSQL (Sprint 2).
- **Storage**: AWS S3 cho việc lưu trữ raw JSON tickets và Model Artifacts.
- **Model Registry/Tracking**: MLflow (chạy trên container riêng).
- **UI Dashboard**: Streamlit.
- **Containerization**: Docker & docker-compose giúp chuẩn hoá môi trường.

## 8. Deployment Strategy
- Sử dụng **GitHub Actions** làm luồng CI/CD tự động:
  - **CI**: Chạy `flake8`/`black` (linting), `pytest` (unit tests). Build và push Docker image lên GitHub Container Registry (GHCR).
  - **CD**: Tự động SSH vào EC2 staging/production, kéo image mới, chạy `docker-compose up -d` và xác nhận trạng thái qua endpoint `/health`.
- Tách biệt môi trường (Staging/Production) để đảm bảo an toàn trước khi promote model hoặc code mới.

## 9. Monitoring Strategy
- **System Monitoring**: Ghi log FastAPI để theo dõi latency, throughput và tỷ lệ lỗi (HTTP 500).
- **Model/Outcome Monitoring**: Theo dõi tỷ lệ phân phối dự đoán (`low`, `medium`, `high`). Cảnh báo nếu xuất hiện đột biến (VD: > 90% ticket được gán `high`).
- **Data Drift**: Cấu hình cron job chạy mỗi ngày sử dụng EvidentlyAI so sánh phân phối dữ liệu mới và dữ liệu training. Báo cáo HTML được lưu ở S3 và nhúng vào Streamlit.

## 10. Success Metrics
- Dòng dữ liệu từ Simulator chảy suốt hệ thống trơn tru mà không có nghẽn hay lỗi vặt.
- Mọi commit merge vào `main` đều đi qua CI test và tự động deploy thành công lên EC2.
- Shadow deployment xác minh model mới chạy ngầm an toàn trước khi thay thế model cũ.
- Phát hiện được hiện tượng Data Drift thông qua báo cáo hệ thống khi kích hoạt kịch bản Drift trên Simulator.
- Thao tác Rollback nhanh chóng kéo hệ thống hoặc model về trạng thái ổn định khi có lỗi mô phỏng.

## 11. Risks
- **Overengineering**: Quá đà trong việc thêm thắt các công nghệ mới (Kafka, Redis, K8s) phá vỡ tính "thực dụng" và giới hạn 1-person execution.
- **Sự cố CD**: Lỗi SSH hoặc phân quyền khi GH Actions kết nối tới EC2. Cần chuẩn hóa chặt chẽ qua Docker để hạn chế rủi ro môi trường.
- **Thiếu tập trung vào MLOps**: Mất quá nhiều thời gian tinh chỉnh thuật toán NLP thay vì xây dựng luồng vận hành (pipeline).

## 12. Constraints
- Dự án do **một cá nhân** đóng mọi vai trò, thời gian giới hạn (Sprint ngắn 2-3 ngày).
- Mọi công cụ phải "AI-friendly" (mã nguồn dễ đọc, ít "ma thuật", phổ biến như FastAPI, Streamlit, Python script).
- Hệ thống cần giới hạn ở thiết kế có chi phí thấp (1 server EC2, lưu trữ rẻ).

## 13. AI Coding Workflow Rules
- **Task siêu nhỏ (Micro-tasks)**: Luôn giao việc cho AI ở mức độ component cụ thể, kèm input/output rõ ràng.
- **Boundaries**: AI không được tự ý refactor code nằm ngoài phạm vi yêu cầu.
- **Context Management**: Giữ `ticket_triage_ai_context.md` làm Source of Truth để nhắc nhở AI về mục tiêu.
- **Chống Drift (Hallucination)**: 
  - Yêu cầu AI luôn viết kèm Unit Tests tương ứng với logic mới.
  - Ràng buộc tiêu chuẩn (ví dụ Pydantic schema bắt buộc cho validation).
  - Developer luôn review và tự động hóa qua `pytest` sau mỗi output của AI trước khi đi tiếp.
