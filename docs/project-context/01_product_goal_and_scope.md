# Mục tiêu Sản phẩm và Phạm vi (Product Goal & Scope)

## 1. Problem Statement
Hầu hết các dự án ML cá nhân chỉ dừng lại ở Jupyter Notebook. Khi bước ra thực tế, kỹ sư gặp khó khăn với các vấn đề production như: luồng dữ liệu thực (data stream), CI/CD, shadow testing, monitoring (data drift), và cơ chế phòng ngừa rủi ro (fallback/rollback).
**Ticket Triage MLOps** giải quyết bài toán thiếu hụt "tư duy production" này bằng cách tạo ra một hệ thống end-to-end tinh gọn, buộc người thực hiện (và AI Agent) phải tư duy theo hướng vận hành an toàn.

## 2. User Personas
Dù làm cá nhân, dự án mô phỏng các vai trò sau:
- **Support Agent**: Người gửi ticket (được giả lập bởi Stream Simulator).
- **Support Lead**: Người theo dõi lượng ticket và trạng thái qua Dashboard.
- **Product Owner (PO)**: Định nghĩa mục tiêu, viết user stories, nghiệm thu.
- **Scrum Master (SM)**: Tổ chức sprint, gỡ rối (blocker), quản lý tiến độ.
- **DevOps / MLOps Engineer**: Xây dựng kiến trúc, CI/CD, hạ tầng và monitoring.
- **AI Coding Agent**: "Lập trình viên AI" hỗ trợ viết code, test, và tài liệu dưới sự kiểm soát nghiêm ngặt.

## 3. Primary Use Cases
1. **Tiếp nhận & Validate Ticket**: Hệ thống nhận ticket từ Simulator, validate schema và lưu trữ.
2. **Phân loại Tự động**: Model suy luận (inference) phân loại ticket thành `low`, `medium`, `high`.
3. **Giám sát Trôi dạt (Drift Monitoring)**: Hệ thống định kỳ kiểm tra sự thay đổi của dữ liệu đầu vào so với dữ liệu huấn luyện và cảnh báo nếu có sự bất thường.
4. **Triển khai Không gián đoạn (Safe Deployment)**: Triển khai model mới qua cơ chế shadow deploy và dễ dàng rollback nếu có lỗi.

## 4. Success Metrics
- **Luồng dữ liệu**: Dữ liệu từ Simulator chảy suốt hệ thống trơn tru, không nghẽn/lỗi.
- **Tự động hóa**: Mọi commit hợp lệ trên nhánh `main` đều tự động chạy qua CI test và deploy thành công lên EC2.
- **Triển khai an toàn**: Shadow deployment hoạt động đúng, cho phép đánh giá model mới trước khi kích hoạt chính thức.
- **Giám sát hiệu quả**: Hệ thống phát hiện và báo cáo chính xác khi Simulator được cấu hình sinh Data Drift.
- **Khôi phục nhanh**: Thao tác Rollback nhanh chóng kéo hệ thống/model về trạng thái ổn định khi có sự cố.

## 5. Non-goals
- Không giải quyết các bài toán xử lý ngôn ngữ tự nhiên phức tạp (NLP SOTA).
- Không phục vụ hàng triệu requests/giây (scalability testing).
- Không xây dựng tính năng quản trị user, phân quyền (auth/roles).
