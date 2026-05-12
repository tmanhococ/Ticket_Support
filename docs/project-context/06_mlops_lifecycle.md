# Vòng đời MLOps (MLOps Lifecycle)

Mô phỏng vòng đời toàn diện của một hệ thống Machine Learning trong dự án.

## 1. Ingest (Tiếp nhận dữ liệu)
- Dữ liệu chảy từ `Stream Simulator` vào hệ thống qua HTTP POST tới Intake API.
- FastAPI sử dụng Pydantic để validate tính toàn vẹn (Schema Validation).

## 2. Process (Xử lý dữ liệu)
- Xử lý văn bản thô (clean text, lowercase, remove stop words).
- Lưu trữ 2 phiên bản: Raw (chưa xử lý - vào S3) và Processed (vào Database) để phục vụ việc audit và training lại.

## 3. Train (Huấn luyện)
- Dữ liệu được trích xuất từ DB.
- Chạy script huấn luyện baseline model (VD: TF-IDF + Logistic Regression hoặc LightGBM).
- Không yêu cầu SOTA, thời gian train phải nhanh, chạy được trên CPU.

## 4. Evaluate (Đánh giá)
- Chạy trên tập test/validation hold-out.
- Thu thập các metrics: Accuracy, Precision, Recall, F1-score.
- Nếu metrics vượt ngưỡng cơ sở (Baseline threshold), model được coi là đạt yêu cầu.

## 5. Register & Version (Lưu trữ và Lập phiên bản)
- Log metrics, parameters, và lưu artifacts model trực tiếp vào **MLflow**.
- Gắn thẻ (Tag) cho các version: `Staging` hoặc `Production`.

## 6. Deploy (Triển khai)
- **Shadow Deploy**: Lần đầu model được deploy ngầm. Nó nhận traffic, thực hiện suy luận và lưu kết quả vào DB nhưng trả về kết quả rỗng hoặc kết quả của model rule-based cho người dùng cuối.
- **Active Deploy**: FastAPI pull model mang tag `Production` từ MLflow để làm model chính thức thức suy luận.

## 7. Monitor (Giám sát)
- **System Metrics**: FastAPI log latency, request count, HTTP 500 errors.
- **Outcome Monitoring**: Theo dõi tỷ lệ class phân bổ (`low`, `medium`, `high`).
- **Data Drift**: Sử dụng `EvidentlyAI` chạy định kỳ so sánh tập dữ liệu nhận được trong 24h qua với tập Reference (Tập Training). Sinh HTML Report lưu ở S3.

## 8. Retrain Trigger (Kích hoạt huấn luyện lại)
- Khi báo cáo từ EvidentlyAI cảnh báo Data Drift nghiêm trọng (VD: ngôn ngữ ticket bị trôi dạt mạnh sang tiếng Đức), gửi alert (log/UI) để Engineer quyết định trigger vòng lặp huấn luyện lại (Retrain) bằng dữ liệu mới.

## 9. Rollback
- Khi model mới hoạt động kém (phát hiện qua Monitor), thay đổi tag trên MLflow về version cũ và trigger API `/reload-model` của backend. Hệ thống ngay lập tức quay lại trạng thái ổn định.
