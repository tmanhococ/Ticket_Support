# Tổng quan Dự án (Project Overview)

## 1. Dự án là gì
**Ticket Triage MLOps** là một dự án xây dựng hệ thống phân loại ticket hỗ trợ khách hàng. Hệ thống tự động tiếp nhận ticket dạng text và phân loại mức độ ưu tiên (`low`, `medium`, `high`). Dự án đóng vai trò như một môi trường "thực chiến thu nhỏ" để rèn luyện tư duy MLOps, làm việc theo quy trình Scrum, và phối hợp hiệu quả với AI Coding Agent.

## 2. Mục tiêu Tổng quát
Mô phỏng hoàn chỉnh vòng đời của một dự án Machine Learning trong môi trường Production:
- Xây dựng luồng dữ liệu (Data Pipeline) từ Intake, Validation đến Storage.
- Xây dựng luồng huấn luyện và triển khai mô hình (Training & Deployment Pipeline).
- Thiết lập cơ chế giám sát (Monitoring), phát hiện trôi dạt dữ liệu (Data Drift), và khôi phục an toàn (Rollback/Fallback).
- Áp dụng các nguyên tắc Scrum thực tế vào dự án cá nhân (sprint ngắn 2-3 ngày).
- Rèn luyện kỹ năng giao việc và kiểm soát AI Coding Agent để tránh hiện tượng trôi dạt (hallucination) trong code.

## 3. Phạm vi (Scope)
- **Data Simulator**: Script sinh dữ liệu ticket giả lập theo thời gian thực có hỗ trợ sinh Data Drift.
- **Intake API**: API tiếp nhận dữ liệu (FastAPI) có tính năng validation.
- **CI/CD**: Pipeline tự động test, build và deploy bằng GitHub Actions.
- **Deployment**: Đóng gói bằng Docker & docker-compose, triển khai trên AWS EC2.
- **Model**: Baseline model đơn giản phân loại độ ưu tiên ticket.
- **Monitoring**: Giám sát lỗi hệ thống, phân phối dự đoán, và báo cáo Data Drift bằng EvidentlyAI.
- **Dashboard**: Giao diện UI tối giản bằng Streamlit.

## 4. Những gì KHÔNG làm (Non-goals)
- **Không** theo đuổi state-of-the-art (SOTA) model. Model đơn giản/dummy là đủ ở giai đoạn đầu để tập trung vào MLOps pipeline.
- **Không** sử dụng các công nghệ cloud-native quá phức tạp, cồng kềnh cho 1 người (như Kubernetes, Kafka, Airflow).
- **Không** xây dựng UI/UX phức tạp, chỉ cần dashboard hiển thị thông tin tối thiểu.
- **Không** mở rộng scope ra ngoài những gì đã định nghĩa trong Sprint Map. Kiến trúc cần giữ ở mức tối giản (minimal) và thực dụng (practical).
