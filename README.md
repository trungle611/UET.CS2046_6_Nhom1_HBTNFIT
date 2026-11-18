# UET.CS2046_6_Nhom1_HBTNFIT

Khung dự án HBTNFIT của Nhóm 1. Stack: React + Vite, FastAPI và SQLAlchemy/SQLite dự kiến. Bản này mới có điều hướng giao diện và `/api/health`; chưa triển khai tài khoản, database, nhận diện AI, thực đơn hay tập luyện.

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

`.env.example` chỉ là mẫu cho các task sau; bản khung chưa gọi Gemini hoặc mở database và không cần API key để chạy.

## Cấu trúc

```text
backend/
  app/main.py       API khởi động và health check
  app/db.py         chỗ bổ sung session/database
  app/models.py     chỗ bổ sung model
  app/schemas.py    chỗ bổ sung schema
  app/ai.py         chỗ tích hợp Gemini
  tests/            kiểm thử API
frontend/
  src/App.jsx       bố cục và điều hướng
  src/api.js        hàm gọi API chung
  src/constants.js  nhãn bữa ăn và dinh dưỡng
  src/style.css     giao diện nền
data/               dữ liệu CSV sẽ bổ sung theo task
docs/               phân công và quy trình làm việc
```

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

## Làm việc nhóm

Đọc [CONTRIBUTING.md](CONTRIBUTING.md) và [phân công](docs/TEAM_TASKS.md). Tạo branch từ `develop`, mở PR vào `develop`, review trước khi merge. `main` giữ bản ổn định.

Commit khởi tạo khung: `Tao khung cho du an`. Các commit tiếp theo phản ánh công việc thực tế của từng thành viên, không chỉnh tác giả/ngày commit để mô phỏng tiến độ trước đây.
