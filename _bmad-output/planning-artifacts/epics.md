---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - d:/MLOps/Ticket_Support/_bmad-output/planning-artifacts/prd.md
  - d:/MLOps/Ticket_Support/_bmad-output/planning-artifacts/architecture.md
---

# Ticket_Support - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Ticket_Support, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

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

### NonFunctional Requirements

NFR1: Thời gian phản hồi (Latency) của Intake API < 200ms cho mỗi request.
NFR2: Khả năng chịu tải: Hệ thống có thể xử lý mượt mà khi Simulator đẩy lưu lượng 50 requests/giây.
NFR3: Tỷ lệ tự động hóa CI/CD là 100%. Mọi thao tác deploy đều chạy qua pipeline, không dùng tay.
NFR4: Thời gian thực thi Rollback toàn bộ hệ thống < 5 phút.
NFR5: Môi trường giả lập phải che mờ (masking) các thông tin nhạy cảm PII trước khi train model (nếu có).
NFR6: API endpoints phục vụ external traffic được bảo vệ bằng cơ chế API Key cơ bản.

### Additional Requirements

- **Starter Template**: Không có starter template được cung cấp sẵn, dự án sẽ khởi tạo từ đầu theo hướng Microservices tinh gọn.
- Xây dựng kiến trúc: FastAPI, Streamlit, MLflow, PostgreSQL, Simulator.
- Tích hợp AWS S3 để lưu raw data, Model artifacts, và báo cáo Evidently.
- Thiết lập Docker và Docker-compose cho việc đóng gói tất cả các services.
- Cấu hình GitHub Actions cho CI/CD pipeline để build image, push GHCR và deploy lên EC2 (Staging/Production).
- Graceful Degradation / Code-level Fallback: API cần bọc try-except, trả rule-based hoặc manual_review khi lỗi model.
- Thiết lập cấu trúc thư mục quy chuẩn (`src/api`, `src/dashboard`, `src/simulator`, `src/drift_monitor`, `tests/`).

### UX Design Requirements

*(Không có tài liệu UX chuyên biệt. Dashboard Streamlit sẽ dùng giao diện mặc định, tối giản, hiển thị các biểu đồ)*

### FR Coverage Map

FR1.1: Epic 1 - Thiết lập endpoint POST /tickets/
FR1.2: Epic 1 - Pydantic Validation (HTTP 400)
FR1.3: Epic 2 - Simulator Script & Kịch bản Drift
FR2.1: Epic 6 & 8 - Baseline Model Training & Shadow Inference
FR2.2: Epic 8 - Triển khai Shadow Mode
FR3.1: Epic 4 & 11 - Product placeholder & Dashboard Polish
FR3.2: Epic 11 - Tích hợp EvidentlyAI HTML Report vào Streamlit
FR4.1: Epic 10 - Fail-safe Mechanisms & Rollback script
FR4.2: Epic 7 - Tích hợp MLflow Tracking

## Epic List

### Sprint 1: Foundation, Data, Skeleton Product
**Epic 1: Ticket intake và data contract**
Xây dựng nền tảng API tiếp nhận dữ liệu với FastAPI, đảm bảo dữ liệu đầu vào luôn chuẩn xác (Pydantic validation) và lưu trữ thành công vào DB.
**FRs covered:** FR1.1, FR1.2

**Epic 2: Stream simulator**
Thiết lập bộ giả lập tạo request liên tục như một môi trường thực tế thu nhỏ, bao gồm khả năng tạo Data Drift.
**FRs covered:** FR1.3

**Epic 3: Walking skeleton CI/CD**
Tự động hóa hoàn toàn quy trình kiểm thử và triển khai bằng GitHub Actions và Docker lên EC2.
**FRs covered:** NFR3

**Epic 4: Product placeholder**
Khởi tạo giao diện tương tác ban đầu (Streamlit) để trực quan hóa lượng dữ liệu đổ vào hệ thống.
**FRs covered:** FR3.1 (một phần)

### Sprint 2: Model + Shadow + Versioning
**Epic 5: Setup & Optimize Storage**
Tối ưu PostgreSQL và cấu hình AWS S3 để chuẩn bị lưu trữ lượng lớn model artifacts và báo cáo.
**FRs covered:** (Hạ tầng nền tảng)

**Epic 6: Baseline Model Training**
Xây dựng pipeline huấn luyện mô hình phân loại văn bản cơ bản nhất (baseline).
**FRs covered:** FR2.1 (training)

**Epic 7: MLflow Tracking**
Thiết lập hệ thống Model Registry để theo dõi lịch sử huấn luyện và các phiên bản của mô hình.
**FRs covered:** FR4.2

**Epic 8: Shadow Inference**
Cập nhật API để chạy song song mô hình học máy (Shadow Mode) nhằm đánh giá hiệu năng thực tế mà không ảnh hưởng kết quả cuối cùng.
**FRs covered:** FR2.1, FR2.2

### Sprint 3: Monitoring + Rollback + Polish
**Epic 9: Data Drift Detection**
Xây dựng job giám sát tự động để phát hiện sự thay đổi bất thường của dữ liệu (Drift) bằng EvidentlyAI.
**FRs covered:** (Mở rộng cho giám sát rủi ro)

**Epic 10: Fail-safe Mechanisms**
Bảo vệ hệ thống khỏi sự cố bằng các cơ chế Fallback (Rule-based) ở tầng Code và kịch bản Rollback model nhanh chóng.
**FRs covered:** FR4.1, NFR4

**Epic 11: Dashboard Polish**
Hoàn thiện giao diện điều khiển, tích hợp báo cáo theo dõi Drift để Support Lead và MLOps Engineer có bức tranh toàn cảnh.
**FRs covered:** FR3.1, FR3.2

**Epic 12: Incident Drill (Tùy chọn)**
Diễn tập sự cố bằng cách cố tình tạo Drift từ Simulator để kiểm tra khả năng phản ứng và phục hồi của toàn bộ hệ thống.
**FRs covered:** (Thử nghiệm độ tin cậy)

<!-- Bắt đầu phần Stories cho từng Epic -->

## Epic 1: Ticket intake và data contract

Xây dựng nền tảng API tiếp nhận dữ liệu với FastAPI, đảm bảo dữ liệu đầu vào luôn chuẩn xác (Pydantic validation) và lưu trữ thành công vào DB.

### Story 1.1: Setup FastAPI Project Structure & DB Connection

As a MLOps Engineer,
I want to initialize the FastAPI project and connect to the database,
So that I have a foundation to build the ticket intake API.

**Acceptance Criteria:**
**Given** an empty repository
**When** I run the server startup command
**Then** the FastAPI server starts on port 8000
**And** a `/health` endpoint returns 200 OK and DB connection status

### Story 1.2: Define Ticket Pydantic Schema

As a MLOps Engineer,
I want to define a strict data contract for incoming tickets,
So that invalid data is rejected before hitting the database.

**Acceptance Criteria:**
**Given** the FastAPI application
**When** a client sends a POST request with an invalid payload
**Then** the API returns HTTP 400 Bad Request with validation errors
**And** valid payloads pass validation successfully

### Story 1.3: Create Intake Endpoint & DB Save

As a MLOps Engineer,
I want an endpoint to receive and save tickets,
So that the system can continuously ingest simulated traffic.

**Acceptance Criteria:**
**Given** a running FastAPI server
**When** a valid POST `/tickets/` request is received
**Then** the ticket is saved to the database with a timestamp
**And** the API returns HTTP 201 Created

## Epic 2: Stream simulator

Thiết lập bộ giả lập tạo request liên tục như một môi trường thực tế thu nhỏ, bao gồm khả năng tạo Data Drift.

### Story 2.1: Implement Base Ticket Generator

As a Developer,
I want a script that generates random but realistic support tickets,
So that I have testing data for the system.

**Acceptance Criteria:**
**Given** the simulator script
**When** I run the generator function
**Then** it outputs a JSON object matching the FastAPI Pydantic schema
**And** the text content looks like a support ticket

### Story 2.2: Implement Request Producer & Drift Logic

As a MLOps Engineer,
I want the simulator to continuously send requests and support a drift parameter,
So that I can test the system's resilience and drift detection.

**Acceptance Criteria:**
**Given** the simulator script and running FastAPI server
**When** I start the producer with normal mode
**Then** it sends N requests per second successfully
**And** when started with `drift=True`, it generates tickets with an altered vocabulary distribution

## Epic 3: Walking skeleton CI/CD

Tự động hóa hoàn toàn quy trình kiểm thử và triển khai bằng GitHub Actions và Docker lên EC2.

### Story 3.1: Dockerize Application Services

As a MLOps Engineer,
I want to containerize the FastAPI app using Docker,
So that the deployment environment is consistent with local dev.

**Acceptance Criteria:**
**Given** the FastAPI source code
**When** I run `docker build` and `docker run`
**Then** the API is accessible inside the container
**And** a `Dockerfile` exists in the repository

### Story 3.2: Create CI/CD Pipeline

As a MLOps Engineer,
I want a GitHub Actions workflow to build and deploy the application,
So that code merged to `main` is automatically pushed to Staging/Production.

**Acceptance Criteria:**
**Given** a new commit on the `main` branch
**When** the GitHub Action triggers
**Then** it runs linting and tests (Pytest)
**And** if successful, builds the Docker image and deploys to the EC2 server

## Epic 4: Product placeholder

Khởi tạo giao diện tương tác ban đầu (Streamlit) để trực quan hóa lượng dữ liệu đổ vào hệ thống.

### Story 4.1: Setup Streamlit Application

As a Support Lead,
I want a basic web dashboard,
So that I can access the system through a UI instead of APIs.

**Acceptance Criteria:**
**Given** the Streamlit app
**When** I navigate to the dashboard URL
**Then** I see the application title and a basic layout
**And** it connects successfully to the underlying database

### Story 4.2: Display Ticket List

As a Support Lead,
I want to view the latest incoming tickets on the dashboard,
So that I know the system is receiving data.

**Acceptance Criteria:**
**Given** the dashboard and existing tickets in the DB
**When** I open the Streamlit app
**Then** I see a table or list of the 50 most recent tickets
**And** the list updates automatically or via a refresh button

## Epic 5: Setup & Optimize Storage

Tối ưu PostgreSQL và cấu hình AWS S3 để chuẩn bị lưu trữ lượng lớn model artifacts và báo cáo.

### Story 5.1: Optimize PostgreSQL configuration

As a MLOps Engineer,
I want to optimize PostgreSQL configuration,
So that the database can handle concurrent inserts from the simulator effectively.

**Acceptance Criteria:**
**Given** the FastAPI and Streamlit apps
**When** I configure the database URL to point to a PostgreSQL container with optimized pooling
**Then** both apps read and write to Postgres successfully under high load
**And** connection pooling is used

### Story 5.2: Configure AWS S3 Client

As a MLOps Engineer,
I want a utility to upload and download files from S3,
So that I can store models and reports externally.

**Acceptance Criteria:**
**Given** AWS credentials
**When** the S3 utility is called with a file
**Then** the file is uploaded to the specified S3 bucket
**And** files can be downloaded back to the local filesystem

## Epic 6: Baseline Model Training

Xây dựng pipeline huấn luyện mô hình phân loại văn bản cơ bản nhất (baseline).

### Story 6.1: Develop Training Pipeline

As a Data Scientist,
I want a script to train a text classification model,
So that the system can automatically categorize tickets.

**Acceptance Criteria:**
**Given** a dataset of historical tickets
**When** I run the training script
**Then** a model is trained to classify text into high/medium/low
**And** the model artifact is saved locally

## Epic 7: MLflow Tracking

Thiết lập hệ thống Model Registry để theo dõi lịch sử huấn luyện và các phiên bản của mô hình.

### Story 7.1: Setup MLflow Server

As a MLOps Engineer,
I want a running instance of MLflow,
So that I have a central place to track experiments.

**Acceptance Criteria:**
**Given** the docker-compose file
**When** I start the services
**Then** MLflow UI is accessible on its dedicated port
**And** it uses PostgreSQL as the backend store and S3 as artifact store

### Story 7.2: Integrate MLflow into Training

As a Data Scientist,
I want the training script to log metrics and models to MLflow,
So that I can compare versions and register the best one.

**Acceptance Criteria:**
**Given** the training script and MLflow server
**When** the training completes
**Then** accuracy metrics are logged to MLflow
**And** the model artifact is registered in the MLflow Model Registry

## Epic 8: Shadow Inference

Cập nhật API để chạy song song mô hình học máy (Shadow Mode) nhằm đánh giá hiệu năng thực tế mà không ảnh hưởng kết quả cuối cùng.

### Story 8.1: Load Model in API

As a MLOps Engineer,
I want the FastAPI app to load the registered model from MLflow,
So that it can use it for inference.

**Acceptance Criteria:**
**Given** a registered model in MLflow
**When** the FastAPI server starts
**Then** it downloads and loads the model into memory
**And** an endpoint can use it to predict labels

### Story 8.2: Implement Shadow Deployment Logic

As a MLOps Engineer,
I want the API to run predictions but not alter the external behavior yet,
So that I can test the model safely on production traffic.

**Acceptance Criteria:**
**Given** an incoming ticket
**When** it hits the `/tickets/` endpoint
**Then** the system predicts the label and saves the `predicted_priority` to the DB
**And** the API response to the user remains unchanged (does not expose the prediction)

## Epic 9: Data Drift Detection

Xây dựng job giám sát tự động để phát hiện sự thay đổi bất thường của dữ liệu (Drift) bằng EvidentlyAI.

### Story 9.1: Generate EvidentlyAI Report

As a MLOps Engineer,
I want a script that compares recent tickets against baseline data,
So that I can detect data drift.

**Acceptance Criteria:**
**Given** a reference dataset and current production data in the DB
**When** I run the Evidently script
**Then** it calculates drift metrics
**And** generates an HTML report showing the results

### Story 9.2: Automate and Upload Drift Reports

As a MLOps Engineer,
I want the drift report generation to run automatically and save to S3,
So that the dashboard can always access the latest report.

**Acceptance Criteria:**
**Given** the Evidently script
**When** it runs as a scheduled job (cron)
**Then** the resulting HTML file is uploaded to the S3 bucket with a timestamp

## Epic 10: Fail-safe Mechanisms

Bảo vệ hệ thống khỏi sự cố bằng các cơ chế Fallback (Rule-based) ở tầng Code và kịch bản Rollback model nhanh chóng.

### Story 10.1: Implement Graceful Degradation

As a MLOps Engineer,
I want the API to fallback to rule-based logic if the model fails,
So that the system never returns a 500 error during inference.

**Acceptance Criteria:**
**Given** a broken model or high latency
**When** an inference request is made
**Then** the API catches the exception
**And** assigns a default label (e.g., based on keyword 'urgent') without failing

### Story 10.2: Infrastructure Rollback Script

As a MLOps Engineer,
I want a script or CI action to quickly revert to a previous state,
So that I can recover from a bad deployment in under 5 minutes.

**Acceptance Criteria:**
**Given** a bad deployment
**When** I execute the rollback mechanism
**Then** the previous stable Docker image is pulled and restarted
**And** the system is fully functional again

## Epic 11: Dashboard Polish

Hoàn thiện giao diện điều khiển, tích hợp báo cáo theo dõi Drift để Support Lead và MLOps Engineer có bức tranh toàn cảnh.

### Story 11.1: Real-time Distribution Charts & Trend Monitoring

As a Support Lead,
I want to see visual charts of ticket priorities and their trends over time,
So that I can quickly assess the workload and spot sudden spikes.

**Acceptance Criteria:**
**Given** tickets with predicted priorities in the DB
**When** I view the Streamlit dashboard
**Then** I see a time-series chart (line/area) showing ticket volume over time grouped by priority
**And** I see a pie/bar chart showing the overall ratio of high/medium/low tickets
**And** I can see the recent ticket list to identify the content of any spikes (e.g., payment errors)

### Story 11.2: Embed Drift Report in Dashboard

As a MLOps Engineer,
I want to view the EvidentlyAI report directly within the dashboard,
So that I don't have to download HTML files manually.

**Acceptance Criteria:**
**Given** an uploaded drift report in S3
**When** I navigate to the "Monitoring" tab in Streamlit
**Then** the latest HTML report is fetched and rendered inside the app

### Story 11.3: Model Performance List

As a MLOps Engineer,
I want to see a list of trained models and their performance metrics on the dashboard,
So that I can easily compare models and click to view detailed information.

**Acceptance Criteria:**
**Given** models registered in MLflow
**When** I navigate to the "Models" tab in the dashboard
**Then** I see a list of trained models with metrics
**And** I can click/expand to view detailed parameters and model information

### Story 11.4: Data Simulation Tab

As a QA/MLOps Engineer,
I want a simulation tab in the dashboard to generate data and view predictions,
So that I can test the model's behavior interactively.

**Acceptance Criteria:**
**Given** the Streamlit dashboard
**When** I input simulation parameters and click "Generate & Send"
**Then** data is generated and sent to the API
**And** the dashboard displays the newly generated data along with the model's classification results and summary charts

## Epic 12: Incident Drill (Tùy chọn)

Diễn tập sự cố bằng cách cố tình tạo Drift từ Simulator để kiểm tra khả năng phản ứng và phục hồi của toàn bộ hệ thống.

### Story 12.1: Execute Postmortem Simulation

As a MLOps Engineer,
I want to trigger the drift simulator and observe the system,
So that I can validate the entire observability and fallback pipeline.

**Acceptance Criteria:**
**Given** the running system
**When** the simulator is set to drift mode
**Then** the Evidently cron job eventually detects the drift
**And** I can see the drift alert in the Streamlit dashboard
