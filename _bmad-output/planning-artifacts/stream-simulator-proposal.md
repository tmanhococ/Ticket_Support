# Đề xuất Thiết kế Stream Simulator (Data Generator & Drift Injection)

Tài liệu này đề xuất cấu trúc và thuật toán cho **Stream Simulator (Epic 2)** trong dự án Ticket Triage MLOps. Yêu cầu chính là thuật toán sinh dữ liệu đơn giản, thêm trường `timestamp` thực tế, và **bắt buộc phải hỗ trợ mô phỏng Data Drift** về sau.

## 1. Phương pháp Chuẩn bị Dữ liệu (Bootstrapping)
Thay vì dùng toàn bộ 29,000 records, chúng ta sẽ cắt ra một tập dữ liệu nền (Base Pool) để mô phỏng.

- **Số lượng:** 2,000 records.
- **Cách làm:** Viết một script dùng `pandas` load file CSV gốc, drop các cột không cần thiết (chỉ giữ `Queue`, `Priority`, `Language`, `Subject`, `Body`, `Type`), sau đó dùng `.sample(n=2000)` để trích xuất và lưu thành file `base_pool.json` hoặc `base_pool.csv`.
- Lúc simulator chạy, nó chỉ cần load file `base_pool` này vào RAM (List of Dictionaries) để rút trích ngẫu nhiên, giúp tối ưu tốc độ.

## 2. Thuật toán Sinh Dữ liệu & Timestamp

Thuật toán sinh (generator) được thiết kế cực kỳ tối giản nhưng đáp ứng đủ yêu cầu của một luồng sự kiện thời gian thực (event stream).

### Logic Sinh Ticket
1. Lấy một mẫu ngẫu nhiên từ `base_pool` (Có thể dùng hàm `random.choice` hoặc `random.choices` có trọng số).
2. Tạo một UUID mới cho `ticket_id`.
3. Khởi tạo trường `timestamp` là thời gian hiện tại (`datetime.now(timezone.utc).isoformat()`).

### Logic Thời gian (Stream Pacing)
Thay vì sinh dữ liệu với tốc độ đều đặn phi thực tế (ví dụ: cứ 5 giây 1 ticket), ta dùng phân phối Poisson hoặc hàm `random.expovariate()` để tính toán thời gian chờ (`sleep_time`) giữa các lần gửi ticket.
- Giờ bình thường: trung bình 1 ticket / phút.
- Giờ cao điểm: trung bình 10 ticket / phút.

## 3. Kiến trúc Mô phỏng Data Drift (Yêu cầu Cốt lõi)

Để hỗ trợ sinh **Data Drift** (thay đổi phân phối dữ liệu đầu vào) một cách dễ dàng, simulator sẽ sử dụng khái niệm **"Drift Profiles"** và **"Weighted Sampling" (Lấy mẫu có trọng số)**.

Thay vì `random.choice()` ngẫu nhiên hoàn toàn từ 2000 dòng, ta sẽ chia 2000 dòng này thành các tập con (sub-pools) theo từng đặc trưng. Khi chạy, ta cấu hình tỷ lệ phần trăm (weights) cho các tập này.

### Ví dụ về Drift Profiles:

**Profile 1: Normal Operations (Hoạt động bình thường)**
- Priority: Low (60%), Medium (30%), Critical (10%)
- Language: EN (80%), Khác (20%)
- Queue: Rải đều.

**Profile 2: System Outage (Drift về Mức độ Ưu tiên / Feature Drift)**
*(Mô phỏng server sập, khách hàng phàn nàn ồ ạt)*
- Priority: Low (10%), Medium (20%), **Critical (70%)**
- Type: **Incident (80%)**
- Rate: Tăng tốc độ sinh lên x5.

**Profile 3: Market Expansion (Drift về Ngôn ngữ / Concept Drift)**
*(Mô phỏng công ty mở rộng sang thị trường Đức và Tây Ban Nha)*
- Language: EN (40%), **DE (30%), ES (30%)**

### Cách lập trình thuật toán Drift:
Khi hàm generator chạy, thay vì bốc đại 1 dòng từ `base_pool`, nó sẽ đọc `Current_Profile`:
```python
def generate_ticket(profile="normal"):
    if profile == "system_outage":
        # Lấy mẫu từ tập các ticket có Priority = Critical với xác suất 70%
        # Xác suất 30% lấy từ tập còn lại
        pass
    elif profile == "language_drift":
        # Ép tỷ lệ ticket tiếng DE và ES tăng vọt
        pass
    else:
        # Lấy ngẫu nhiên bình thường
        pass
```

## 4. Cấu trúc Source Code Đề xuất

Để giữ cho code "AI-friendly" và "Minimal", tôi đề xuất cấu trúc sau cho module simulator:

```text
simulator/
├── data/
│   └── base_pool.json       # 2000 records mẫu
├── profiles.py              # Định nghĩa các kịch bản Drift (Normal, Outage, LangDrift)
├── generator.py             # Hàm sinh ticket (chứa thuật toán Weighted Sampling & Timestamp)
├── producer.py              # Vòng lặp while gửi request POST đến FastAPI endpoint
└── README.md
```

## 5. Tóm tắt Action Plan cho bạn và AI

Khi bạn giao task này cho Coding Agent để bắt đầu code, bạn chỉ cần đưa cho AI các hướng dẫn sau:
1. Viết script lọc 2000 dòng lưu ra `base_pool.json`.
2. Viết `generator.py` có hàm `yield_ticket(profile_name)` dùng `random.choices` để thực hiện Weighted Sampling nhằm dễ dàng tạo Data Drift. Sinh `timestamp` theo giờ hệ thống hiện tại.
3. Viết `producer.py` có vòng lặp vô hạn, lấy ticket từ `generator` và gọi API `POST /tickets`, với tốc độ delay được random.

Thiết kế này hoàn toàn đáp ứng được tính **đơn giản**, nhưng có kiến trúc mở (**Profiles**) để ngay lập tức mô phỏng **Data Drift** phục vụ cho Sprint 3 (Monitoring & Alerts).
