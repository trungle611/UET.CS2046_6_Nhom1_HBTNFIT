# HBTNFIT

Ứng dụng theo dõi dinh dưỡng và tập luyện, dùng React + Vite, FastAPI và SQLite.

- Tài khoản bằng tên đăng nhập/mật khẩu; dữ liệu cá nhân riêng theo tài khoản.
- Mục tiêu cân nặng và kcal/protein/carb/chất béo hằng ngày.
- Nhận diện món qua Gemini, kiểm tra khẩu phần, thực đơn và lịch sử ăn uống.
- Giáo án PPL/Upper-Lower, tiến độ bài tập và lịch đi tập/nghỉ.

## Chạy nhanh

Yêu cầu Python 3.11+, Node.js 22 và Git. Chạy từ gốc repo, dùng môi trường Python trên chính máy đang chạy. Nếu đã có môi trường và cấu hình riêng, dùng lại chúng.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt
if (!(Test-Path backend/.env)) { Copy-Item backend/.env.example backend/.env }
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Terminal thứ hai:

```bash
cd frontend
npm ci
npm run dev
```

Mở [ứng dụng](http://127.0.0.1:5173) và [API health](http://127.0.0.1:8000/api/health). Hướng dẫn macOS, interpreter, dữ liệu bền và triển khai nằm trong [DEPLOYMENT](docs/DEPLOYMENT.md).

Khóa Gemini chỉ đặt trong `backend/.env`. Khi dịch vụ AI lỗi, giao diện cho nhập món thủ công; dữ liệu đã lưu vẫn được giữ. Mỗi món cần được kiểm tra và xác nhận trước khi cộng vào thực đơn.

## Kiểm tra

Sau khi cài đủ thư viện Python và Node.js, chạy tại gốc repo:

```powershell
.\.venv\Scripts\python.exe scripts/check_release.py
```

Môi trường `.local/venv` dùng Python tại `.local/venv/Scripts/python.exe`; macOS/Linux sau khi kích hoạt môi trường dùng `python scripts/check_release.py`. Log được lưu riêng trong `.local/release-checks/`.

## Tài liệu

| Nội dung | Hướng dẫn |
| --- | --- |
| Cài đặt, môi trường, database và triển khai | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) |
| Sử dụng, kiến trúc và hành vi chi tiết | [docs/USAGE.md](docs/USAGE.md) |
| Tổng duyệt và đóng phiên bản | [docs/RELEASE.md](docs/RELEASE.md) |
| Kịch bản demo và phương án dự phòng | [docs/DEMO.md](docs/DEMO.md) |
| Dữ liệu món và đơn vị khẩu phần | [data/README.md](data/README.md) |
| Khóa nhãn và đánh giá AI | [evaluation/README.md](evaluation/README.md) |

`backend/` và `frontend/` chứa mã ứng dụng; `data/` chứa CSV, `evaluation/` chứa nhãn mẫu và hướng dẫn đánh giá, `scripts/` chứa công cụ kiểm tra. Cấu hình pytest/Ruff giữ ở gốc để các lệnh kiểm tra hoạt động như cũ.

Không đưa `.env`, database, ảnh người dùng hoặc môi trường Python lên Git. `.idea/` là cấu hình IDE riêng từng máy và được Git bỏ qua.
