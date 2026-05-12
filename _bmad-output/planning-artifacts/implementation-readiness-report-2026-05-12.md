---
stepsCompleted: ['step-01-document-discovery', 'step-02-prd-analysis', 'step-03-epic-coverage-validation', 'step-04-ux-alignment', 'step-05-epic-quality-review', 'step-06-final-assessment']
inputDocuments:
  - d:/MLOps/Ticket_Support/_bmad-output/planning-artifacts/prd.md
  - d:/MLOps/Ticket_Support/_bmad-output/planning-artifacts/architecture.md
  - d:/MLOps/Ticket_Support/_bmad-output/planning-artifacts/epics.md
workflowType: 'implementation-readiness'
project_name: 'Ticket_Support'
user_name: 'TienManh'
date: '2026-05-12'
---

# Implementation Readiness Assessment Report

**Date:** 2026-05-12
**Project:** Ticket_Support

## PRD Analysis

### Functional Requirements

FR1.1: Hệ thống cung cấp endpoint `POST /tickets/` nhận JSON payload gồm `ticket_id`, `text`, `timestamp`.
FR1.2: Trả về HTTP 400 nếu payload vi phạm Data Contract (sai format, thiếu trường).
FR1.3: Simulator có khả năng gửi request liên tục và hỗ trợ tham số để sinh Data Drift (thay đổi phân phối ngôn ngữ).
FR2.1: Hệ thống chạy model dự đoán trả về nhãn `high`, `medium`, `low`.
FR2.2: Cung cấp chế độ Shadow Mode - nhận traffic, gọi model mới để lưu dự đoán vào DB nhưng trả về kết quả của model chính cho user.
FR3.1: Hiển thị tổng số ticket và phân phối theo nhãn (Realtime chart).
FR3.2: Hiển thị/Nhúng báo cáo HTML của EvidentlyAI (Data Drift report).
FR4.1: Có script Rollback cho phép lùi version Docker container hoặc lùi Model version về bản ổn định gần nhất.
FR4.2: MLflow UI có thể truy cập được để xem lịch sử training và quản lý Model Registry.

Total FRs: 9

### Non-Functional Requirements

NFR1: Thời gian phản hồi (Latency) của Intake API < 200ms cho mỗi request.
NFR2: Khả năng chịu tải: Hệ thống có thể xử lý mượt mà khi Simulator đẩy lưu lượng 50 requests/giây.
NFR3: Tỷ lệ tự động hóa CI/CD là 100%. Mọi thao tác deploy đều chạy qua pipeline, không dùng tay.
NFR4: Thời gian thực thi Rollback toàn bộ hệ thống < 5 phút.
NFR5: Môi trường giả lập phải che mờ (masking) các thông tin nhạy cảm PII trước khi train model (nếu có).
NFR6: API endpoints phục vụ external traffic được bảo vệ bằng cơ chế API Key cơ bản.

Total NFRs: 6

### Additional Requirements

- **Compliance**: Yêu cầu về Bảo mật dữ liệu (Data Privacy) với thao tác masking dữ liệu PII và khả năng truy vết (Auditability) mọi dự đoán thông qua Model Version (bằng MLflow).
- **Constraints**: Không Over-engineering (Không K8s, Kafka, Airflow). Phải sử dụng Docker-compose, FastAPI, PostgreSQL, AWS S3, Streamlit, MLflow.
- **Safety**: Phải có Graceful Degradation / Code-level Fallback (try-except để không sập server, trả kết quả manual_review khi model lỗi).

### PRD Completeness Assessment

Tài liệu PRD được viết rất chi tiết, có phân chia rõ ràng giữa các yêu cầu chức năng, phi chức năng, và đặc tả cấu trúc dữ liệu. Hệ thống mục tiêu và triết lý (Pragmatic/1-person execution) được xác định sắc bén, dễ dàng đối chiếu với các Epic và Story.

## Epic Coverage Validation

### Coverage Matrix

| FR Number | PRD Requirement | Epic Coverage | Status |
| --------- | --------------- | -------------- | --------- |
| FR1.1 | Hệ thống cung cấp endpoint POST /tickets/ nhận JSON payload... | Epic 1 | ✓ Covered |
| FR1.2 | Trả về HTTP 400 nếu payload vi phạm Data Contract... | Epic 1 | ✓ Covered |
| FR1.3 | Simulator có khả năng gửi request liên tục và hỗ trợ tham số để sinh Data Drift... | Epic 2 | ✓ Covered |
| FR2.1 | Hệ thống chạy model dự đoán trả về nhãn high, medium, low... | Epic 6 & Epic 8 | ✓ Covered |
| FR2.2 | Cung cấp chế độ Shadow Mode... | Epic 8 | ✓ Covered |
| FR3.1 | Hiển thị tổng số ticket và phân phối theo nhãn... | Epic 4 & Epic 11 | ✓ Covered |
| FR3.2 | Hiển thị/Nhúng báo cáo HTML của EvidentlyAI... | Epic 11 | ✓ Covered |
| FR4.1 | Có script Rollback cho phép lùi version Docker container... | Epic 10 | ✓ Covered |
| FR4.2 | MLflow UI có thể truy cập được để xem lịch sử training... | Epic 7 | ✓ Covered |

### Missing Requirements

Không có FR nào bị bỏ sót. Tất cả các yêu cầu chức năng (FR) trong PRD đều đã được bao phủ bởi các Epic tương ứng.

### Coverage Statistics

- Total PRD FRs: 9
- FRs covered in epics: 9
- Coverage percentage: 100%

## UX Alignment Assessment

### UX Document Status

Not Found (Không có tài liệu UX chuyên biệt).

### Alignment Issues

Không có sự mâu thuẫn. Các Epic đã ghi nhận rõ: "Không có tài liệu UX chuyên biệt. Dashboard Streamlit sẽ dùng giao diện mặc định, tối giản, hiển thị các biểu đồ".

### Warnings

Không có cảnh báo nghiêm trọng. Việc thiếu thiết kế UX là hoàn toàn nhất quán với định hướng "Pragmatic Architecture" (1-person MLOps execution) của dự án, vốn chỉ yêu cầu một giao diện cơ bản bằng Streamlit để trực quan hoá biểu đồ và báo cáo.

## Epic Quality Review

Quá trình đánh giá chất lượng Epic dựa trên best practices (giá trị cho user, tính độc lập, story độc lập).

### 🔴 Critical Violations
- **Epic 5: Setup & Optimize Storage (Optimize PostgreSQL, Configure S3)**: Đây là một "Technical Milestone" (Mốc kỹ thuật) không mang lại giá trị trực tiếp cho End-user hoặc Persona chính trong bối cảnh sử dụng phần mềm. Việc tối ưu DB và setup S3 thuần túy là công việc hạ tầng.
  - *Recommendation*: Nên lồng ghép Story 5.1 (PostgreSQL) vào Epic 1 (áp dụng PostgreSQL ngay từ đầu để đảm bảo hiệu năng). Story 5.2 (S3) nên được chuyển vào Epic 6 hoặc Epic 7 vì đó là nơi S3 thực sự bắt đầu mang lại giá trị lưu trữ model và artifact.

### 🟠 Major Issues
- **Epic 3: Walking skeleton CI/CD**: Tương tự Epic 5, đây là một Epic nặng về hạ tầng kỹ thuật. Tuy nhiên, đối với lĩnh vực MLOps, CI/CD chính là giá trị cốt lõi mà Kỹ sư (MLOps Engineer persona) nhận được. Vì thế nó được coi là hợp lệ trong bối cảnh này, nhưng cần lưu ý ACs phải xoay quanh "Code merge vào main được tự động test và deploy".

### 🟡 Minor Concerns
- **Story Sizing**: Đa số các Story đã được thiết kế khá độc lập với Acceptance Criteria rõ ràng. Không phát hiện forward-dependency (Story 1 phụ thuộc vào Story 2). 
- **Database/Entity Timing**: Story 1.1 khởi tạo kết nối DB, Story 1.3 bắt đầu lưu dữ liệu. Thời điểm khởi tạo bảng/schema đang được phân bổ hợp lý, không có sự dư thừa "tạo toàn bộ DB từ đầu".
- **Starter Template**: Epic 1 Story 1 bắt đầu từ một project rỗng (setup FastAPI từ đầu) khớp với yêu cầu Architecture (Greenfield MLOps).

## Summary and Recommendations

### Overall Readiness Status

**READY** (Sẵn sàng triển khai, với một số điều chỉnh nhỏ nếu muốn tối ưu).

### Critical Issues Requiring Immediate Action

Không có lỗi nghiêm trọng (blocker) cản trở quá trình triển khai. PRD, Kiến trúc và Epic có sự đồng bộ tuyệt đối về tư duy (1-person MLOps) và yêu cầu chức năng (100% FR Coverage). Vấn đề duy nhất nằm ở cách tổ chức Epic 5 hơi thiên về Technical Milestone, nhưng điều này hoàn toàn có thể chấp nhận trong một dự án nặng tính hệ thống như thế này.

### Recommended Next Steps

1. **Gộp Epic 5**: Gộp Story 5.1 (PostgreSQL) vào Epic 1 ngay từ đầu. Chuyển Story 5.2 (S3) sang Epic 7 (MLflow Tracking) vì MLflow cần S3 làm artifact store.
2. **Khởi tạo Codebase**: Bắt đầu triển khai Epic 1 theo cấu trúc thư mục quy chuẩn đã định (với `./src/`).
3. **Cập nhật UX (nếu có)**: Trong quá trình làm Epic 4 và 11 (Streamlit Dashboard), nếu phát sinh yêu cầu thiết kế cụ thể hơn, có thể bổ sung Mockup sau.

### Final Note

Đợt kiểm tra này phát hiện 1 lỗi cấu trúc Epic ở mức độ Critical (Epic 5 thiếu User Value trực tiếp) và 1 lỗi Major (Epic 3 thuần kỹ thuật). Tuy nhiên, với 100% độ bao phủ yêu cầu chức năng, dự án đã đủ chín muồi để bước vào giai đoạn Implementation (Thực thi code). Bạn có thể điều chỉnh Epic 5 hoặc tiếp tục giữ nguyên nếu thấy thuận tiện cho luồng làm việc cá nhân.
