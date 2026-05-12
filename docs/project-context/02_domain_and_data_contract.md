# Domain và Data Contract

## 1. Domain: Ticket Triage
Hệ thống tiếp nhận các yêu cầu hỗ trợ (ticket) từ khách hàng dưới dạng văn bản và phân loại chúng vào các mức độ ưu tiên (Priority) để đội ngũ hỗ trợ xử lý hiệu quả.

## 2. Ticket Schema
Dữ liệu đầu vào bắt buộc tuân theo Schema sau (dựa trên phân tích từ `data_info.md`):

| Field | Type | Description |
| :--- | :--- | :--- |
| `ticket_id` | UUID | Định danh duy nhất của ticket. |
| `timestamp` | ISO8601 | Thời gian ticket được gửi vào hệ thống. |
| `subject` | String | Tiêu đề của email/ticket. |
| `body` | String | Nội dung chi tiết của email/ticket. |
| `language` | String | Ngôn ngữ (VD: `en`, `de`, `es`). |
| `queue` | String | Phòng ban (VD: `Technical Support`, `Customer Service`). |
| `type` | String | Loại ticket (VD: `Incident`, `Request`, `Problem`, `Change`). |

## 3. Input/Output Contract (Inference API)
- **Input**: JSON Object chứa tối thiểu `ticket_id`, `subject`, `body`, `timestamp`.
- **Output**: JSON Object chứa:
  - `ticket_id`: UUID ban đầu.
  - `predicted_priority`: `low`, `medium`, hoặc `high`.
  - `confidence_score`: Float (0.0 - 1.0).
  - `model_version`: String phiên bản model đang dùng.

## 4. Data Flow
1. **Simulator**: Sinh JSON ticket và gửi `POST` tới Intake API.
2. **Intake API (FastAPI)**: Validate payload -> Lưu raw data xuống Storage (Local File/S3) -> Lưu metadata vào Database (SQLite/Postgres).
3. **Training**: Script/Cron job đọc raw data, xử lý text, huấn luyện model -> Đẩy artifact lên S3 & log metadata lên MLflow.
4. **Inference**: FastAPI pull model từ MLflow/S3 để thực hiện phân loại trực tiếp khi có request (hoặc chạy shadow mode).
5. **Evaluation/Monitoring**: Cron job lấy dữ liệu thực tế từ Database so sánh với dữ liệu gốc để tính Data Drift bằng EvidentlyAI.
6. **Dashboard**: Streamlit đọc từ Database để hiển thị ticket và đọc file HTML từ báo cáo Drift.

## 5. Data Assumptions (Dựa trên `data_info.md`)
- Mức độ ưu tiên thực tế (Ground Truth) có 3 mức: `low` (1), `medium` (2), `high`/`critical` (3). Model sẽ chuẩn hóa output về `low`, `medium`, `high`.
- Dữ liệu text có chứa cả tiếng Anh và tiếng Đức (`en`, `de`).

## 6. Validation Rules
- `ticket_id` phải là UUID hợp lệ.
- `subject` và `body` không được để trống (empty). Nếu thiếu, API trả về HTTP 422.
- `timestamp` phải theo định dạng chuẩn ISO8601.

## 7. Drift Considerations
Stream Simulator được cấu hình để hỗ trợ mô phỏng Data Drift thông qua các Profiles:
- **Feature Drift**: Tăng đột biến tỷ lệ ticket `critical` hoặc `Incident`.
- **Concept Drift / Language Drift**: Thay đổi phân phối ngôn ngữ (VD: Tăng vọt lượng ticket tiếng `de` hoặc `es`).
Hệ thống Monitoring cần bắt được những thay đổi phân phối này.
