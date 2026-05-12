---
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-02b-vision
  - step-02c-executive-summary
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
  - step-12-complete
releaseMode: phased
inputDocuments:
  - d:/MLOps/Ticket_Support/_bmad-output/planning-artifacts/product-brief.md
  - d:/MLOps/Ticket_Support/_bmad-output/planning-artifacts/research/technical-ticket-triage-architecture-2026-05-12.md
  - d:/MLOps/Ticket_Support/docs/ticket_triage_ai_context.md
  - d:/MLOps/Ticket_Support/docs/data_info.md
  - d:/MLOps/Ticket_Support/docs/project-context/00_project_overview.md
  - d:/MLOps/Ticket_Support/docs/project-context/01_product_goal_and_scope.md
  - d:/MLOps/Ticket_Support/docs/project-context/02_domain_and_data_contract.md
  - d:/MLOps/Ticket_Support/docs/project-context/03_system_architecture.md
  - d:/MLOps/Ticket_Support/docs/project-context/04_environment_and_deployment.md
  - d:/MLOps/Ticket_Support/docs/project-context/05_ci_cd_and_release_flow.md
  - d:/MLOps/Ticket_Support/docs/project-context/06_mlops_lifecycle.md
  - d:/MLOps/Ticket_Support/docs/project-context/07_sprint_map.md
  - d:/MLOps/Ticket_Support/docs/project-context/08_agent_workflow_rules.md
  - d:/MLOps/Ticket_Support/docs/project-context/09_risks_assumptions_open_questions.md
documentCounts:
  briefCount: 1
  researchCount: 1
  brainstormingCount: 0
  projectDocsCount: 12
workflowType: 'prd'
classification:
  projectType: 'API / Backend Pipeline'
  domain: 'MLOps / ITSM'
  complexity: 'Medium'
  projectContext: 'brownfield'
---

# Tài liệu Yêu cầu Sản phẩm (Product Requirements Document) - Ticket_Support

**Tác giả:** TienManh
**Ngày:** 2026-05-12

## Tóm tắt Điều hành (Executive Summary)

Ticket Triage MLOps là một hệ thống phân loại ticket hỗ trợ khách hàng được thiết kế như một "sa bàn thực chiến" (production-ready sandbox) dành cho kỹ sư Machine Learning. Dự án giải quyết bài toán thiếu hụt tư duy vận hành thực tế bằng cách mô phỏng trọn vẹn vòng đời MLOps—từ Intake API, Data Validation, CI/CD, Shadow Deployment đến Monitoring và Fallback. Mục tiêu cốt lõi không phải là xây dựng một mô hình State-of-the-Art (SOTA), mà là thiết lập một đường ống (pipeline) ổn định, tự động hóa toàn phần, có khả năng đối phó với các rủi ro vận hành trong môi trường thực tế.

### Điều làm nên sự khác biệt (What Makes This Special)

- **Trọng tâm vào Vận hành & Giám sát**: Ưu tiên việc phát hiện Data Drift (qua EvidentlyAI) và thiết lập cơ chế Rollback/Fallback an toàn, thay vì chỉ tập trung tối ưu thuật toán ML.
- **Thực thi tinh gọn (1-Person Execution)**: Tối ưu kiến trúc bằng cách sử dụng các công cụ thực dụng (FastAPI, Streamlit, Docker, GitHub Actions, EC2) và kiên quyết từ chối over-engineering (không Kubernetes, không Kafka).
- **Hợp tác an toàn với AI**: Tích hợp hệ thống quy tắc làm việc nghiêm ngặt với AI Coding Agent (chia nhỏ task, giới hạn phạm vi, bắt buộc có Unit Test) nhằm kiểm soát triệt để rủi ro code hallucination.

## Phân loại Dự án (Project Classification)

- **Loại dự án (Project Type):** API / Backend Pipeline
- **Lĩnh vực (Domain):** MLOps / ITSM
- **Độ phức tạp (Complexity):** Medium
- **Bối cảnh (Project Context):** Brownfield

## Tiêu chí Thành công (Success Criteria)

### Thành công của Người dùng (User Success)
- **Kỹ sư MLOps (Người học/Người triển khai)**: Nắm vững và tự tin làm chủ toàn bộ vòng đời ML trên môi trường Production thu nhỏ mà không bị lạc lối trong lý thuyết.
- **AI Coding Agent**: Hoàn thành các micro-tasks được giao một cách chính xác, pass 100% Unit Tests và không gây ra hiện tượng phá vỡ logic cũ (hallucination/drift code).

### Thành công về Mặt Dự án (Project Success)
- Vận hành thành công dự án cá nhân theo kỷ luật Scrum (sprint ngắn 2-3 ngày).
- Rèn luyện tư duy "Production-first", ưu tiên hệ thống giám sát và khôi phục sự cố trước khi ưu tiên độ phức tạp của model.

### Thành công Kỹ thuật (Technical Success)
- Stream Simulator bơm dữ liệu trơn tru vào hệ thống mà không có hiện tượng tắc nghẽn.
- Mọi thay đổi code merge vào nhánh `main` đều tự động vượt qua CI Pipeline (Linting, Tests) và Deploy thành công lên EC2.
- Cơ chế Fallback/Rollback hoạt động trơn tru, khôi phục hệ thống an toàn khi có lỗi xảy ra.
- Hệ thống phát hiện và cảnh báo Data Drift tự động thông qua EvidentlyAI.

### Kết quả Đo lường Cụ thể (Measurable Outcomes)
- Tỷ lệ CI/CD Pipeline chạy thành công đạt > 95% sau giai đoạn đầu.
- Thời gian Rollback hệ thống về trạng thái ổn định cũ mất dưới 5 phút.
- Unit Test coverage (với sự hỗ trợ của AI Agent) đạt tối thiểu 80%.

## Phạm vi Sản phẩm (Product Scope)

### MVP - Minimum Viable Product (Giai đoạn Sprint 1)
- API tiếp nhận và kiểm tra dữ liệu bằng FastAPI.
- Script giả lập luồng dữ liệu ticket theo thời gian (Stream Simulator).
- CI/CD cơ bản (GitHub Actions -> Docker -> EC2).
- Dashboard Streamlit đơn giản với PostgreSQL.
- Model phân loại cơ bản (baseline) với 3 mức độ: `low`, `medium`, `high`.

### Các Tính năng Tăng trưởng (Growth / Sprint 2 & 3)
- Nâng cấp database lên PostgreSQL.
- Quản lý version model bằng MLflow.
- Triển khai ngầm (Shadow Deployment) để kiểm định mô hình mới trên môi trường thực.
- Thiết lập giám sát Data Drift và Alerting (EvidentlyAI).

### Tầm nhìn (Vision)
- Xây dựng kho source code này thành một "Template MLOps chuẩn mực" để dễ dàng tái sử dụng (clone & run) cho mọi dự án AI quy mô vừa và nhỏ trong tương lai.

## Bản đồ Hành trình Người dùng (User Journeys)

### 1. Hành trình Triển khai Mô hình Mới (MLOps Engineer - Happy Path)
**Nhân vật:** Alex (Kỹ sư MLOps)
**Mở đầu:** Alex vừa huấn luyện xong một phiên bản model phân loại mới. Anh commit và push code lên nhánh `main`. Dù tự tin nhưng anh vẫn có chút hồi hộp.
**Diễn biến:** Hệ thống GitHub Actions tự động kích hoạt. Các bước kiểm tra code (linting, pytest) chạy mượt mà. Docker image được build và tự động deploy lên server EC2. Thay vì thay thế ngay model cũ, hệ thống đưa model mới vào chạy ở chế độ *Shadow Deployment* (nhận traffic thực tế nhưng chỉ dự đoán ngầm, không trả kết quả cho end-user).
**Cao trào:** Alex mở bảng điều khiển theo dõi MLflow và nhận thấy model mới hoạt động cực kỳ chính xác trên dữ liệu thực tế, không hề làm tăng độ trễ (latency) của hệ thống.
**Kết thúc:** Alex quyết định "promote" model mới thành bản chính thức. Anh nhận ra tư duy MLOps đã giúp việc đưa mô hình ra thực tế trở nên an toàn và nhàn nhã hơn rất nhiều.

### 2. Hành trình Đối mặt và Khôi phục Sự cố (MLOps Engineer - Edge Case / Recovery)
**Nhân vật:** Alex (Kỹ sư MLOps)
**Mở đầu:** Đang trong giờ làm việc, Alex bất ngờ nhận được cảnh báo từ EvidentlyAI báo hiệu có sự thay đổi bất thường (Data Drift) - tỷ lệ ticket bị phân loại là `high` tăng vọt một cách vô lý.
**Diễn biến:** Anh truy cập Streamlit dashboard để xem báo cáo HTML chi tiết. Alex phát hiện ra cấu trúc ngôn ngữ của khách hàng thay đổi đột ngột (ví dụ xuất hiện một từ khóa lỗi mới), khiến model hiện tại phân loại sai hoàn toàn. Đồng thời API có dấu hiệu quá tải.
**Cao trào:** Không mất thời gian hoảng loạn, Alex sử dụng cơ chế Rollback để ngay lập tức khôi phục toàn bộ hệ thống và model về phiên bản ổn định của ngày hôm trước. Quá trình này diễn ra chưa tới 3 phút.
**Kết thúc:** Hệ thống trở lại trạng thái an toàn. Alex thở phào nhẹ nhõm, tiến hành cô lập dữ liệu lỗi để phân tích và chuẩn bị train lại model. Cảm giác làm chủ hệ thống giúp anh giải quyết sự cố tự tin như một chuyên gia.

### 3. Hành trình Giám sát Khối lượng Công việc (Support Lead - Operations)
**Nhân vật:** Sarah (Trưởng nhóm CSKH)
**Mở đầu:** Đầu ca làm việc, Sarah cần nắm bắt tình hình để phân bổ nhân sự.
**Diễn biến:** Cô truy cập vào URL của Streamlit Dashboard. Giao diện ngay lập tức hiển thị trực quan lưu lượng ticket đang đổ về theo thời gian thực, phân chia rõ ràng theo các nhãn `high`, `medium`, `low`.
**Cao trào:** Nhờ màu sắc cảnh báo, cô nhanh chóng nhận thấy một "điểm nóng" (spike) với hàng loạt ticket `high` liên quan đến lỗi thanh toán. 
**Kết thúc:** Sarah lập tức huy động nhóm ưu tiên xử lý cụm ticket này. Nhờ công cụ hiển thị trực quan, cô chủ động điều phối công việc thay vì phải mò mẫm lọc ticket thủ công.

### 4. Hành trình Tiêu thụ API (Stream Simulator - Automated Actor)
**Mô tả:** Đây là một Script Python đóng vai trò "khách hàng" gọi liên tục vào hệ thống để tạo môi trường thực hành cho Alex.
**Hành trình:** Script khởi động, liên tục sinh ra các payload JSON chứa ticket giả lập. Ở điều kiện bình thường, nó đẩy traffic đều đặn. Khi được cấu hình, nó sẽ cố tình "bơm" các dữ liệu nhiễu, từ vựng lạ (để tạo Data Drift) hoặc tạo lưu lượng đột biến để kiểm tra sức chịu tải và khả năng cảnh báo của toàn bộ hệ thống.

### Tóm tắt Yêu cầu từ Hành trình (Journey Requirements Summary)
- **Từ Hành trình 1 (Deploy)**: Cần thiết lập GitHub Actions CI/CD pipeline chuẩn mực, tự tự động build Docker và có tính năng Shadow Deployment để test model an toàn.
- **Từ Hành trình 2 (Rollback)**: Bắt buộc tích hợp EvidentlyAI để phát hiện Drift, và phải có kịch bản Rollback (script tự động hoặc 1-click) luôn sẵn sàng trên server.
- **Từ Hành trình 3 (Dashboard)**: Xây dựng Streamlit app đọc dữ liệu từ Database PostgreSQL realtime, hiển thị biểu đồ phân phối ticket rõ ràng.
- **Từ Hành trình 4 (Simulator)**: Script giả lập (Simulator) phải linh hoạt, cho phép truyền tham số để tạo các kịch bản traffic khác nhau (bình thường, nhiễu, quá tải).

## Yêu cầu Nghiệp vụ Đặc thù (Domain-Specific Requirements)

### Tuân thủ & Pháp lý (Compliance & Regulatory)
- **Bảo mật dữ liệu (Data Privacy)**: Mặc dù là sa bàn thực chiến, nhưng do tính chất mô phỏng dữ liệu hỗ trợ khách hàng (ticket), hệ thống cần ý thức về việc xử lý thông tin nhạy cảm (PII). Quá trình Intake nên có bước làm sạch hoặc làm ẩn dữ liệu trước khi train model.
- **Khả năng Truy vết (Auditability)**: Mọi dự đoán của hệ thống phải được ghi log kèm theo chính xác phiên bản model (Model Version) đã đưa ra quyết định đó, sử dụng MLflow.

### Ràng buộc Kỹ thuật (Technical Constraints)
- **Quản trị Sự trôi dạt (Drift Management)**: Dữ liệu ngôn ngữ luôn thay đổi. Hệ thống bắt buộc phải duy trì một job kiểm tra Data Drift định kỳ (hoặc realtime) bằng EvidentlyAI.
- **Cô lập Môi trường (Isolation)**: Tính năng Shadow Deployment yêu cầu traffic thật được đẩy vào model mới để test, nhưng kết quả dự đoán ngầm này phải được cô lập hoàn toàn, không được ghi đè vào database production.
- **Triển khai Không chạm (Zero-touch Deployment)**: Quá trình từ commit đến deploy phải hoàn toàn tự động qua CI/CD để tránh lỗi do thao tác thủ công của con người (human error).

### Yêu cầu Tích hợp (Integration Requirements)
- **CI/CD & Source Control**: Tích hợp sâu và liền mạch với GitHub Actions.
- **Môi trường**: Mọi service (FastAPI, Streamlit, MLflow) phải được đóng gói Docker để đảm bảo tính nhất quán tuyệt đối giữa môi trường Dev và Production (AWS EC2).

### Giảm thiểu Rủi ro (Risk Mitigations)
- **Suy giảm Hiệu năng Đột ngột**: Áp dụng cơ chế Fallback/Rollback tự động (hoặc 1-click) để nhanh chóng đưa hệ thống về phiên bản an toàn gần nhất khi phát hiện lỗi hoặc drift.
- **Over-engineering**: Kiểm soát rủi ro phình to dự án bằng cách thiết lập ranh giới cứng: Không sử dụng Kubernetes, Kafka hay các công cụ vượt quá giới hạn vận hành của 1 cá nhân.

## Yêu cầu Đặc thù Loại Dự án (Project-Type Specific Requirements)

### Tổng quan Kiến trúc API & Backend
Dự án được xây dựng theo kiến trúc Microservices tinh gọn (phù hợp cho 1-person execution). Giao tiếp chính thông qua RESTful API.

### Cấu trúc Thành phần (Technical Architecture Considerations)
- **Intake API**: Xây dựng bằng FastAPI. Bắt buộc có Pydantic schema để validate dữ liệu đầu vào (Data Contracts).
- **Model Training & Versioning**: Tích hợp MLflow server (chạy container) để quản lý metadata và model artifacts.
- **Data Storage**: Sử dụng PostgreSQL ngay từ đầu để thiết lập luồng dữ liệu vững chắc. File raw ticket và model lưu tại S3 (hoặc local storage gắn volume).
- **Dashboard**: Streamlit app trực quan, query dữ liệu trực tiếp từ DB.

### Triển khai (Implementation Considerations)
- Sử dụng Docker-compose để orchestrate toàn bộ stack (FastAPI, Streamlit, MLflow) trên cùng 1 server EC2.
- Source code được quản lý trên GitHub, sử dụng GitHub Actions CI/CD để tự động build image, push lên GHCR và SSH deploy lên EC2.

## Phân định Phạm vi và Giai đoạn (Project Scoping & Phased Development)

### Chiến lược MVP
**Cách tiếp cận:** Xây dựng một "Walking Skeleton" - luồng dữ liệu end-to-end hoạt động được nhưng chưa có logic phức tạp.
**Nguồn lực:** 1 Kỹ sư MLOps (với sự hỗ trợ của AI Agent).

### Giai đoạn 1: MVP (Sprint 1 - Foundation & Skeleton)
**Journeys cốt lõi:** Hành trình số 3 (Dashboard) và số 4 (Simulator).
**Tính năng bắt buộc (Must-Have):**
- FastAPI endpoints (POST `/tickets/`, GET `/health`).
- Script Stream Simulator tạo dữ liệu giả lập.
- Setup GitHub Actions CI/CD pipeline và Dockerize.
- Streamlit dashboard kết nối PostgreSQL.
- Model baseline phân loại 3 mức độ (`high`, `medium`, `low`).

### Giai đoạn 2: Tăng trưởng (Sprint 2 - Model & Shadow)
- Tối ưu truy vấn PostgreSQL (nếu cần).
- Tích hợp MLflow Tracking.
- Cấu hình Shadow Deployment cho model mới.

### Giai đoạn 3: Giám sát & An toàn (Sprint 3 - Monitoring & Rollback)
- Tích hợp EvidentlyAI giám sát Data Drift.
- Xây dựng kịch bản Fallback/Rollback tự động hoặc 1-click.
- Incident Postmortem (Diễn tập sự cố).

### Chiến lược Giảm thiểu Rủi ro
**Rủi ro kỹ thuật:** Thiết lập sai CI/CD gây downtime. *Cách giải quyết:* Cô lập môi trường Staging/Production, triển khai hoàn toàn bằng Docker.
**Rủi ro tài nguyên:** Dự án bị phình to (Over-engineering). *Cách giải quyết:* Tuân thủ nghiêm ngặt nguyên tắc 1-người vận hành, chỉ dùng công cụ "AI-friendly".

## Yêu cầu Chức năng (Functional Requirements)

### 1. Data Intake & Simulator
- **FR1.1**: Hệ thống cung cấp endpoint `POST /tickets/` nhận JSON payload gồm `ticket_id`, `text`, `timestamp`.
- **FR1.2**: Trả về HTTP 400 nếu payload vi phạm Data Contract (sai format, thiếu trường).
- **FR1.3**: Simulator có khả năng gửi request liên tục và hỗ trợ tham số để sinh Data Drift (thay đổi phân phối ngôn ngữ).

### 2. Model Inference
- **FR2.1**: Hệ thống chạy model dự đoán trả về nhãn `high`, `medium`, `low`.
- **FR2.2**: Cung cấp chế độ Shadow Mode - nhận traffic, gọi model mới để lưu dự đoán vào DB nhưng trả về kết quả của model chính cho user.

### 3. Streamlit Dashboard
- **FR3.1**: Hiển thị tổng số ticket và phân phối theo nhãn (Realtime chart).
- **FR3.2**: Hiển thị/Nhúng báo cáo HTML của EvidentlyAI (Data Drift report).

### 4. MLOps & Rollback
- **FR4.1**: Có script Rollback cho phép lùi version Docker container hoặc lùi Model version về bản ổn định gần nhất.
- **FR4.2**: MLflow UI có thể truy cập được để xem lịch sử training và quản lý Model Registry.

## Yêu cầu Phi Chức năng (Non-Functional Requirements)

### Hiệu năng (Performance)
- **NFR1**: Thời gian phản hồi (Latency) của Intake API < 200ms cho mỗi request.
- **NFR2**: Khả năng chịu tải: Hệ thống có thể xử lý mượt mà khi Simulator đẩy lưu lượng 50 requests/giây.

### Khả năng Vận hành (Operability)
- **NFR3**: Tỷ lệ tự động hóa CI/CD là 100%. Mọi thao tác deploy đều chạy qua pipeline, không dùng tay (No human intervention in deployment).
- **NFR4**: Thời gian thực thi Rollback toàn bộ hệ thống < 5 phút.

### Bảo mật (Security)
- **NFR5**: Môi trường giả lập phải che mờ (masking) các thông tin nhạy cảm PII trước khi train model (nếu có).
- **NFR6**: API endpoints phục vụ external traffic được bảo vệ bằng cơ chế API Key cơ bản.
