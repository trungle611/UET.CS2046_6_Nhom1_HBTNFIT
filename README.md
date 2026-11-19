# UET.CS2046_6_Nhom1_HBTNFIT

HBTNFIT của Nhóm 1 dùng React + Vite, FastAPI và SQLAlchemy/SQLite. Bản hiện tại có khung điều hướng, `/api/health`, các model/schema và nạp danh mục thực phẩm từ CSV khi khởi động. Module nhận diện Gemini và xử lý ảnh đã có; route `/api/scan` và các route nghiệp vụ khác đang được tích hợp.

## Chạy local

Yêu cầu: Python 3.11+, Node.js 20+ và Git. Các lệnh dưới đây chạy từ thư mục repo sau khi clone:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements-dev.txt
Copy-Item backend\.env.example backend\.env
cd backend
..\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal khác, từ thư mục repo:

```powershell
cd frontend
npm ci
npm run dev
```

Mở http://127.0.0.1:5173 và bấm **Kiểm tra kết nối API**. Swagger: http://127.0.0.1:8000/docs. Nếu bản demo cũ đang dùng cổng 8000/5173 trên cùng máy, hãy dừng nó trước khi chạy bản khung.

Backend tạo database SQLite local theo `DATABASE_URL` và nạp danh mục CSV khi khởi động. Chưa cần API key để chạy health check; không commit file `.env` hoặc database.

## Cấu trúc

```text
backend/
  app/main.py       API khởi động và health check
  app/db.py         kết nối, session và cập nhật database demo
  app/models.py     model SQLAlchemy
  app/schemas.py    schema kiểm tra dữ liệu
  app/catalog.py    nạp và kiểm tra danh mục CSV
  app/core.py       tính dinh dưỡng và đối chiếu thực phẩm
  app/auth.py       helper mật khẩu và token
  app/ai.py         Gemini, fallback và xử lý lỗi/timeout
  app/scan_service.py kiểm tra ảnh, đối chiếu món và dinh dưỡng
  tests/            kiểm thử API
frontend/
  src/App.jsx       bố cục và điều hướng
  src/api.js        hàm gọi API chung
  src/constants.js  nhãn bữa ăn và dinh dưỡng
  src/ScanSection.jsx tải ảnh và kiểm tra kết quả nhận diện
  src/TodayMeals.jsx thực đơn, khẩu phần và checklist
  src/ScanHistory.jsx lịch sử nhận diện
  src/FoodHistory.jsx lịch sử dinh dưỡng theo ngày
  src/style.css     giao diện nền
data/               danh mục thực phẩm và món ăn CSV
```

Bốn component ăn uống đã có mã nguồn, nhưng chưa được nối vào `App.jsx`, stylesheet và API nghiệp vụ. Chạy frontend hiện vẫn hiển thị khung điều hướng; luồng ăn uống chưa chạy end-to-end trong bản tích hợp này.

## Kiểm tra

Từ thư mục gốc:

```powershell
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m ruff check backend
.\.venv\Scripts\python -m ruff format --check backend
cd frontend
npm run format:check
npm run build
```

