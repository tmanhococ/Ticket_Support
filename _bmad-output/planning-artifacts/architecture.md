---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - d:/MLOps/Ticket_Support/_bmad-output/planning-artifacts/product-brief.md
  - d:/MLOps/Ticket_Support/_bmad-output/planning-artifacts/prd.md
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
workflowType: 'architecture'
project_name: 'Ticket_Support'
user_name: 'TienManh'
date: '2026-05-12'
---

# Tài liệu Quyết định Kiến trúc (Architecture Decision Document)

_Tài liệu này được tạo ra dựa trên các yêu cầu sản phẩm và context dự án hiện tại._

## 1. Mục tiêu Kiến trúc (Architectural Goals)
Hệ thống Ticket Triage MLOps hướng đến một kiến trúc thực dụng ("Pragmatic Architecture"), tập trung vào tính ổn định, dễ vận hành cho 1 kỹ sư (1-person execution) và làm nổi bật vòng đời MLOps hơn là sự phức tạp của model AI.
- **Tính tự động hóa cao**: Từ CI/CD, đóng gói (Docker) đến giám sát, phát hiện Drift.
- **An toàn khi xảy ra sự cố**: Có cơ chế Fallback ở mức code và Rollback ở mức hạ tầng.
- **Không Over-engineering**: Tránh sử dụng K8s, Kafka, Airflow; thay vào đó là Docker-compose, FastAPI, S3, PostgreSQL.

## 2. Các Quyết định Công nghệ Cốt lõi (Core Technology Decisions)

### 2.1 Backend & API (Intake & Inference)
- **Công nghệ**: FastAPI
- **Lý do**: Hiệu năng cao (async support), tự động sinh OpenAPI docs, validate dữ liệu đầu vào chuẩn xác qua Pydantic (Data Contract).

### 2.2 Cơ sở Dữ liệu (Database)
- **Công nghệ**: PostgreSQL (chạy qua Docker)
- **Lý do**: Bền bỉ, ổn định cho môi trường Production (thay vì SQLite ban đầu). Hỗ trợ tốt JSONB và phù hợp để query dữ liệu trên Dashboard.

### 2.3 Storage (Lưu trữ Dữ liệu Tĩnh & Model)
- **Công nghệ**: AWS S3
- **Lý do**: Tách biệt trạng thái (stateless) cho API. Lưu raw data, Model Artifacts (`.pkl`/`.onnx`) và các báo cáo HTML của Evidently một cách rẻ, bền vững.

### 2.4 Quản lý Vòng đời Model (Model Tracking & Registry)
- **Công nghệ**: MLflow (Server containerized)
- **Lý do**: Tiêu chuẩn công nghiệp cho tracking thí nghiệm (experiments), quản lý model version và dễ dàng rollback bằng cách đổi tag (vd: `Production` -> `Staging`).

### 2.5 Giao diện Giám sát (Dashboard & UI)
- **Công nghệ**: Streamlit
- **Lý do**: Nhanh chóng tạo UI cho dữ liệu bằng Python, tiết kiệm thời gian phát triển frontend. Hiển thị tốt biểu đồ và nhúng (embed) báo cáo HTML của Evidently.

### 2.6 Đóng gói & Triển khai (Containerization & Deployment)
- **Công nghệ**: Docker, Docker-compose, GitHub Actions CI/CD, AWS EC2 (2 instances: Staging & Production).
- **Lý do**: Đảm bảo môi trường nhất quán từ Local -> Staging -> Production. CI/CD qua GitHub Actions (build image, push GHCR, SSH deploy) hoàn toàn tự động (Zero-touch deployment).

## 3. Các Thành phần Hệ thống & Luồng Dữ liệu (System Components & Data Flow)

- **Stream Simulator (Local)**: Script Python đóng gói Docker chạy trên máy cá nhân, tạo request liên tục (có Drift mode) gửi lên EC2 API.
- **FastAPI Service (EC2)**: 
  - Nhận HTTP POST request từ Simulator.
  - Validate payload bằng Pydantic.
  - Kéo model từ MLflow/S3 (hoặc lấy từ cache).
  - Gọi Inference, lấy kết quả phân loại (high/medium/low).
  - Lưu trạng thái (ID, predicted_label, time) vào PostgreSQL. Lưu raw data vào S3.
- **Drift Monitor (EC2 - Cron)**: Script chạy định kỳ bằng Cron, đọc data từ DB (hoặc S3), dùng EvidentlyAI tính toán drift so với reference data, xuất báo cáo `.html` lên S3.
- **Streamlit Dashboard (EC2)**: Truy vấn PostgreSQL để render biểu đồ phân phối ticket và nhúng báo cáo S3 Evidently.

## 4. Quyết định về An toàn & Phục hồi (Safety & Recovery Patterns)

- **Graceful Degradation / Code-level Fallback**: 
  FastAPI route phải được bọc trong `try-except`. Nếu model bị lỗi hoặc time-out, API sẽ trả về nhãn `manual_review` hoặc chạy rule-based (vd: nếu chứa từ 'urgent' thì trả 'high') thay vì trả HTTP 500.
- **Model Rollback (MLflow)**: 
  Nếu model hiện tại bị Data Drift quá nặng, đổi tag model ổn định trước đó trong MLflow thành `Production`, rồi gọi `/reload-model` webhook trên FastAPI để hot-reload mà không downtime.
- **Infrastructure Rollback (GitHub Actions)**: 
  Nếu bản deploy gây sập (Container chết), kích hoạt lại (re-run) GitHub Action Job deploy của commit trước đó trên nhánh `main`. Docker sẽ tự pull image cũ.

## 5. Cấu trúc Thư mục Đề xuất (Proposed Directory Structure)

```text
Ticket_Support/
├── .github/workflows/          # CI/CD pipelines (test, build, deploy)
├── src/                        # Thư mục mã nguồn chính
│   ├── api/                        # FastAPI service
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── schemas.py              # Pydantic data contracts
│   │   └── services/               # Model inference logic
│   ├── dashboard/                  # Streamlit app
│   │   └── app.py
│   ├── simulator/                  # Stream simulator script
│   │   └── run_simulator.py
│   └── drift_monitor/              # EvidentlyAI script
│       └── run_drift.py
├── tests/                      # Unit/Integration tests
├── docker-compose.yml          # Triển khai các container
└── requirements.txt
```

## 6. Xác nhận Khả năng Triển khai (Validation & Implementation Readiness)
Kiến trúc này đã hoàn toàn khớp với mục tiêu PRD và "Project Context":
- **Không dư thừa công cụ** (Đúng triết lý 1-người vận hành).
- **Phủ kín vòng đời MLOps** (Inference, CI/CD, Shadow Deploy, Data Drift, Fallback).
- **Cô lập môi trường** rõ ràng (Local, Staging EC2, Production EC2).
