---
epic: 1
story: 4
title: Import Historical Data
status: done
---

# Story 1.4: Import Historical Data

## Background
Ban đầu, kiến trúc hệ thống sử dụng **Simulator** (Epic 2) để sinh 100% dữ liệu (cả dữ liệu mồi và dữ liệu streaming) nhằm đảm bảo hệ thống có thể test end-to-end mà không phụ thuộc file bên ngoài. Tuy nhiên, để sát với thực tế, chúng ta cần phân tách rõ rệt:
- **Historical Data**: Dữ liệu lịch sử có sẵn của công ty, được lưu trong `data/original/tickets.csv`. Dữ liệu này phải được nạp (seed) vào Database trước khi hệ thống chạy.
- **Streaming Data**: Dữ liệu sinh ra khi hệ thống đang vận hành, do Simulator đóng giả luồng ticket mới gửi đến API.

## Requirements (User Story)
> **As a** Data Engineer / System Admin  
> **I want** to run a script to import historical tickets from a CSV file into the PostgreSQL database  
> **So that** the ML model and dashboard have real historical data to process before the live stream starts.

## Acceptance Criteria
- [ ] **AC1:** Có một Python script độc lập (VD: `src/api/scripts/seed_data.py`) đọc file `data/original/tickets.csv`.
- [ ] **AC2:** Script sử dụng SQLAlchemy models (`Ticket` từ `src.api.models`) để bulk insert dữ liệu vào bảng `tickets`.
- [ ] **AC3:** Dữ liệu insert phải map đúng với schema (cần tự động sinh `ticket_id` UUID và `received_at` timestamp lùi về quá khứ để phân biệt với data mới).
- [ ] **AC4:** Script có khả năng báo lỗi rõ ràng nếu không tìm thấy file CSV hoặc database chưa sẵn sàng.

## Tasks / Subtasks
- [ ] Task 1: Create Seed Script
  - [ ] 1.1 Tạo thư mục `src/api/scripts/` và file `seed_data.py`.
  - [ ] 1.2 Đọc file CSV bằng pandas, map các cột (subject, body, type, queue, language, priority) với SQLAlchemy `Ticket` model.
- [ ] Task 2: Database Insertion
  - [ ] 2.1 Sử dụng async session (từ `src.api.database`) để insert dữ liệu.
  - [ ] 2.2 Đảm bảo script có thể chạy từ command line dễ dàng (`python -m src.api.scripts.seed_data`).
- [ ] Task 3: Update documentation/plan
  - [ ] 3.1 Ghi chú lại luồng này vào documentation để quá trình setup E2E rõ ràng hơn.

## Dev Notes
- **Lưu ý Timestamp:** Vì là historical data, bạn có thể thiết lập `received_at` lùi dần về quá khứ (ví dụ: trừ đi vài ngày hoặc vài giờ so với thời điểm hiện tại) để chart trên Dashboard không bị tụ lại ở 1 điểm thời gian.
- **Lưu ý UUID:** Tự động gen `uuid4()` cho mỗi record trong script.
- **Fallback:** Script cần an toàn, không insert trùng nếu dữ liệu đã tồn tại (hoặc đơn giản là clear bảng `tickets` trước khi seed nếu chạy ở môi trường test).

## File List (Expected)
- `src/api/scripts/seed_data.py`

## Change Log
- 2026-05-14: Story created.
