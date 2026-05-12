# CI/CD và Release Flow

## 1. Tổng quan CI/CD Pipeline
Pipeline được xây dựng hoàn toàn dựa trên **GitHub Actions**, tối ưu cho sự tự động hóa với sự can thiệp thủ công tối thiểu.

## 2. Continuous Integration (CI)
**Trigger:** Mỗi khi có thao tác `push` lên nhánh `main`, hoặc tạo Pull Request (PR) vào `main`.

**Các bước CI:**
1. **Linting & Formatting**: Chạy `flake8` và `black` để đảm bảo chuẩn code style. Điều này cực kỳ quan trọng để kiểm soát code do AI sinh ra.
2. **Unit Testing**: Chạy `pytest`. Mọi component API, Data Schemas, Model Loading logic đều phải có test.
3. **Build Image**: Build Docker Image cho các service (FastAPI, Streamlit).
4. **Push Registry**: Đẩy image với tag là `commit_hash` và `latest` lên GitHub Container Registry (GHCR).

## 3. Continuous Deployment (CD)
**Trigger:** Tự động chạy sau khi Job CI báo thành công trên nhánh `main`.

**Các bước CD:**
1. **SSH Connection**: Sử dụng GitHub Secrets (IAM Access Keys - phương pháp nhanh và đơn giản) để SSH an toàn vào server AWS EC2 tương ứng (Staging hoặc Production).
2. **Pull New Image**: Chạy `docker pull` để lấy image `latest` từ GHCR về server.
3. **Deploy**: Chạy lệnh `docker-compose up -d` để khởi động lại các container với cấu hình mới. Lệnh này đảm bảo zero-downtime hoặc minimal downtime cho môi trường nhỏ.
4. **Health Check**: (Release Gate) Tự động gọi endpoint `GET /health` của FastAPI. Nếu không nhận được HTTP 200, Job CD sẽ báo lỗi để Engineer nhận biết.

## 4. Promote between Environments
Để thực hiện nâng hạng (Promote) giữa 2 máy EC2 (Staging và Production), ta quản lý dựa trên **Git Tags** và nhánh:
- Push/Merge vào `main` -> Tự động Deploy lên môi trường **Staging**.
- Tạo một GitHub Release / Tag `v1.x.x` -> Tự động Trigger workflow deploy lên môi trường **Production**.

## 5. Release Gates
- **Gate 1**: Tất cả Unit Tests phải PASS.
- **Gate 2**: Build Docker image thành công.
- **Gate 3**: Môi trường mục tiêu trả lời thành công tín hiệu Health Check sau khi deploy.
