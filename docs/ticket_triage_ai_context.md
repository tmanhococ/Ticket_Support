# Bối cảnh dự án: Ticket Triage + Scrum Sprints + MLOps + Coding Agent

## 1) Mục tiêu của tài liệu này
Tài liệu này được viết để một AI có thể đọc nhanh và hiểu đúng toàn bộ ngữ cảnh dự án trước khi hỗ trợ thiết kế kiến trúc, viết code, tạo tài liệu, lập kế hoạch sprint, hoặc đề xuất workflow.

Dự án là một mô phỏng thực chiến theo tư duy doanh nghiệp, nhưng được thu gọn để một cá nhân có thể triển khai trong thời gian ngắn bằng cách kết hợp:
- Scrum theo sprint ngắn
- MLOps cho vòng đời dữ liệu, model, deploy và monitor
- Coding agent để sinh code có kiểm soát
- Tư duy production & operation, không chỉ làm demo model

---

## 2) Tên bài toán
**Ticket Triage**

Đây là hệ thống nhận ticket hỗ trợ khách hàng, sau đó phân loại mức độ ưu tiên như:
- `low`
- `medium`
- `high`

Mục tiêu là mô phỏng một hệ thống ML có tính sản phẩm thật, có data pipeline, training pipeline, deploy pipeline, monitoring, drift detection, rollback, dashboard, và quy trình làm việc gần với team doanh nghiệp.

---

## 3) Mục tiêu học tập của dự án
Dự án này không nhằm tạo model tốt nhất, mà nhằm hiểu đúng tư duy sản xuất phần mềm và vận hành ML trong môi trường production.

Người thực hiện muốn học và mô phỏng các năng lực sau:
- Tư duy PO: define problem, product goal, user story, backlog, acceptance criteria
- Tư duy SM: sprint planning, execution, review, retro, manage team/process
- Tư duy DevOps/MLOps: CI/CD, deploy, monitoring, observability, rollback, versioning
- Tư duy coding agent: cách giao việc rõ ràng cho AI, giảm drift, kiểm soát context, review code
- Tư duy production: an toàn, có kiểm thử, có log, có drill sự cố, có khả năng quay lui

---

## 4) Bối cảnh thực hiện
Người thực hiện là một cá nhân, nhưng muốn mô phỏng như một team doanh nghiệp có đủ vai trò:
- **PO**: xác định mục tiêu sản phẩm, phạm vi sprint, backlog, acceptance criteria
- **SM**: tổ chức sprint, breakdown task, theo dõi tiến độ, gỡ blocker, review process
- **DevOps/Engineer**: triển khai hạ tầng, CI/CD, testing, deploy, monitoring
- **Reviewer / QA**: kiểm tra chất lượng đầu ra
- **Coding agent**: hỗ trợ sinh code, sinh test, sinh docs theo prompt có ràng buộc

Người thực hiện sẽ là người review cuối cùng và quyết định deploy.

---

## 5) Mục tiêu sản phẩm ở mức cao
Sản phẩm cần mô phỏng được một flow thực tế:
1. Ticket được sinh ra liên tục hoặc gửi vào hệ thống
2. Hệ thống validate dữ liệu đầu vào
3. Hệ thống lưu raw data để tái tạo flow
4. Hệ thống train baseline model
5. Hệ thống deploy inference service
6. Hệ thống chạy shadow deploy hoặc ghost deploy để kiểm tra model mới
7. Hệ thống ghi logs và monitor data drift/model behavior
8. Hệ thống có cơ chế rollback/fallback an toàn
9. Hệ thống có dashboard tối thiểu để nhìn thấy trạng thái sản phẩm
10. Hệ thống có CI/CD để tự động kiểm thử và deploy

---

## 6) Định hướng kiến trúc thực dụng
Dự án không cần enterprise cloud quá phức tạp. Ưu tiên kiến trúc thực dụng, dễ làm, dễ hiểu, nhưng vẫn phản ánh production thinking.

Định hướng ban đầu được chốt theo kiểu:
- GitHub Actions cho CI/CD
- EC2 cho compute/deploy
- S3 cho lưu dữ liệu / artifact / backup nếu cần
- FastAPI cho backend inference / intake API
- Streamlit hoặc UI Python đơn giản cho dashboard
- Docker để đóng gói app
- Logging file / CloudWatch tùy khả năng triển khai

Mục tiêu là học được vòng đời thực tế, không phải ép dùng quá nhiều dịch vụ cloud chỉ để “trông chuyên nghiệp”.

---

## 7) Ý nghĩa của từng khái niệm trong dự án
### 7.1 Staging và production
- **Local**: chạy trên máy cá nhân để phát triển nhanh
- **Staging**: môi trường tiền sản xuất, gần production nhất có thể trong phạm vi dự án nhỏ
- **Production**: môi trường demo hoặc chạy thật của sản phẩm mô phỏng

Staging phải dùng để bắt lỗi tích hợp, lỗi cấu hình, lỗi deploy, lỗi contract dữ liệu, chứ không phải chỉ là nơi chạy thử vui.

### 7.2 Shadow deploy / ghost deploy
Model mới được chạy song song hoặc chạy ngầm trên dữ liệu thật, nhưng không trả kết quả trực tiếp cho người dùng cuối. Mục tiêu là so sánh chất lượng và phát hiện rủi ro trước khi promote.

### 7.3 Data drift
Khi phân phối dữ liệu đầu vào thay đổi theo thời gian, ví dụ ticket mới dùng từ vựng khác hoặc có kiểu phản hồi khác. Dự án cần mô phỏng được drift để thấy lý do hệ thống ML phải được monitor liên tục.

### 7.4 Rollback / fallback
Khi model mới gây lỗi hoặc chất lượng kém, hệ thống phải có cơ chế quay về behavior an toàn, ví dụ bật feature flag để dùng rule-based fallback hoặc model cũ.

### 7.5 CI/CD
Mỗi thay đổi code hợp lệ cần đi qua test, build, rồi deploy tự động lên staging hoặc môi trường mô phỏng production.

---

## 8) Bức tranh workflow tổng thể
Dự án cần mô phỏng một workflow có đủ các lớp:

### Lớp sản phẩm
- Vision
- Problem statement
- Personas
- User stories
- Backlog
- Acceptance criteria
- Sprint goal

### Lớp kỹ thuật
- Architecture overview
- Folder structure
- API contracts
- Data contracts
- Model artifacts
- Deployment strategy
- Testing strategy
- Monitoring strategy

### Lớp vận hành
- Logs
- Alerts
- Drift checks
- Rollback plan
- Runbook
- Postmortem giả lập nếu có incident

### Lớp làm việc với AI agent
- Context file cho agent
- Prompt rules
- Task breakdown nhỏ
- Review flow
- Anti-drift workflow
- Code/test/doc generation có kiểm soát

---

## 9) Cách dùng Scrum trong dự án này
Dự án được chia thành **2–3 sprint ngắn**, mỗi sprint chỉ khoảng 2–3 ngày.

### Sprint 1: Foundation, Data, Skeleton Product
Mục tiêu: dựng nền móng end-to-end tối thiểu.

Có thể bao gồm:
- Ticket intake và data contract
- Stream simulator
- Walking skeleton CI/CD
- Product placeholder / dashboard tối thiểu

### Sprint 2: Model + Shadow + Versioning
Mục tiêu: có baseline model, inference API, shadow logging, model versioning.

### Sprint 3: Monitoring + Rollback + Polish
Mục tiêu: drift detection, rollback/fallback, alerting, dashboard hoàn chỉnh, demo và slide.

---

## 10) Cấu trúc Sprint 1 đã chốt trong cuộc trao đổi
Sprint 1 được xác định như sau:

### Epic 1: Ticket intake và data contract
User story:
- Là Support Agent, tôi muốn gửi một ticket vào hệ thống để hệ thống tiếp nhận được nội dung triage.

Acceptance criteria:
- Ticket có `ticket_id`, `text`, `timestamp`, `source`
- Ticket rỗng hoặc thiếu `text` bị từ chối
- Có lưu raw ticket để tái dựng flow

Technical tasks gợi ý:
- Viết Pydantic schema cho ticket
- Viết API `POST /tickets`
- Lưu raw ticket vào local file hoặc S3
- Viết unit test cho validation

### Epic 2: Stream simulator
User story:
- Là hệ thống, tôi muốn sinh ticket giả lập liên tục để mô phỏng realtime traffic.

Acceptance criteria:
- Có script sinh ticket theo thời gian
- Sinh được ít nhất 3 nhóm nội dung: login issue, refund issue, general inquiry
- Có thể bật/tắt tốc độ sinh dữ liệu

Technical tasks gợi ý:
- Viết `producer.py`
- Sinh JSON event liên tục
- Ghi log đầu ra
- Có test cho format dữ liệu giả lập

### Epic 3: Walking skeleton CI/CD
User story:
- Là engineer, tôi muốn mỗi thay đổi hợp lệ được test và deploy tự động lên môi trường staging tối thiểu.

Acceptance criteria:
- Push code lên `main` sẽ chạy test
- Build Docker image thành công
- Deploy được app skeleton lên EC2
- Có health check endpoint

Technical tasks gợi ý:
- Tạo GitHub Actions workflow
- Viết Dockerfile
- Viết FastAPI skeleton
- Viết `GET /health`
- Deploy lên EC2 bằng SSH hoặc script đơn giản

### Epic 4: Product placeholder
User story:
- Là Support Lead, tôi muốn có một màn hình tối thiểu để nhìn thấy ticket đang vào hệ thống.

Acceptance criteria:
- Có màn hình hiển thị ticket mới nhất
- Có thể refresh thủ công hoặc tự động
- Không cần prediction thật ở giai đoạn này

Technical tasks gợi ý:
- Dựng Streamlit hoặc UI đơn giản
- Gọi API lấy ticket
- Hiển thị danh sách gần nhất

---

## 11) Vai trò của PO, SM, DevOps trong workflow
### PO
- Xác định vấn đề và giá trị sản phẩm
- Viết user story
- Chốt acceptance criteria
- Ưu tiên backlog
- Chốt sprint goal với stakeholder

### SM
- Chuyển backlog thành kế hoạch sprint
- Breakdown task
- Điều phối planning / daily / review / retro
- Ghi blocker, decision, risk log
- Giữ nhịp làm việc và bảo vệ sprint goal

### DevOps / Engineer
- Thiết kế và triển khai kỹ thuật
- Viết CI/CD, Docker, deploy, monitoring
- Breakdown task kỹ thuật
- Xử lý dependency, secret, environment
- Cung cấp phản hồi khả thi cho PO/SM

### Coding agent
- Sinh code theo nhiệm vụ nhỏ và rõ
- Sinh test, docs, scaffold, utility code
- Không được tự mở rộng scope ngoài yêu cầu
- Cần context file và quy tắc rõ ràng để tránh drift

---

## 12) Nguyên tắc dùng coding agent
Khi dùng AI coding agent, phải ghi rõ:
- Mục tiêu của task
- Phạm vi task
- Input / output
- Ràng buộc code style
- File nào được phép sửa
- Test nào phải chạy
- Không được tự ý refactor ngoài phạm vi

Cần có cơ chế chống drift:
- Task nhỏ
- Context ngắn nhưng đủ
- Review sau mỗi bước
- Chốt source of truth trong docs
- Tách prompt theo module

AI chỉ nên làm việc tốt nhất khi có ranh giới rõ ràng.

---

## 13) Tài liệu tối thiểu cần có trong project
### Tài liệu PO / product
- `Sprint-1-Brief.md`
- `Backlog.md`
- `Definition-of-Ready.md`
- `Definition-of-Done.md`
- `Demo-Plan.md`
- `Risk-Register.md`

### Tài liệu kỹ thuật
- `Architecture-Overview.md`
- `ADR-001.md`
- `Release-Checklist.md`
- `Test-Matrix.md`

### Tài liệu cho agent
- `AGENTS.md` hoặc tương đương
- Context file cho từng module nếu cần
- Prompt rules cho code generation

### Tài liệu vận hành
- Runbook
- Incident notes
- Decision log
- Observability notes
- Rollback guide

---

## 14) Tiêu chí thành công của dự án
Dự án được coi là thành công khi có thể:
- Mô phỏng được flow từ ticket vào đến output
- Có schema và validation rõ ràng
- Có training pipeline và artifact versioning
- Có deploy pipeline tự động
- Có staging / production thinking
- Có monitor và drift detection cơ bản
- Có rollback/fallback an toàn
- Có dashboard để demo
- Có tài liệu và workflow để AI agent hiểu và hỗ trợ tiếp

---

## 15) Điều AI cần ưu tiên khi hỗ trợ dự án này
Khi hỗ trợ, AI cần ưu tiên theo thứ tự:
1. Hiểu rõ mục tiêu sản phẩm trước
2. Giữ scope nhỏ và thực dụng
3. Tối ưu cho sprint ngắn và một người làm
4. Tách việc thành task nhỏ để agent xử lý tốt
5. Bảo toàn production thinking: test, deploy, monitor, rollback
6. Không làm kiến trúc quá phức tạp nếu không cần thiết
7. Mọi quyết định kỹ thuật nên phục vụ mục tiêu học tập và mô phỏng doanh nghiệp

---

## 16) Ghi chú cuối
Dự án này là một bài tập mô phỏng quy trình doanh nghiệp hiện đại năm 2026 theo góc nhìn cá nhân. Mục tiêu là hiểu sâu cách sản phẩm ML được phát triển và vận hành, không chỉ là viết model.

Điều quan trọng nhất là giữ được 3 trục cùng lúc:
- **Product**: giải quyết vấn đề gì
- **Process**: làm việc theo sprint ra sao
- **Platform**: hệ thống được deploy và vận hành như thế nào

Nếu AI đọc tài liệu này, nó phải hiểu rằng toàn bộ thiết kế tiếp theo cần bám vào Ticket Triage, Scrum sprint ngắn, MLOps thực dụng, và workflow có kiểm soát với coding agent.

