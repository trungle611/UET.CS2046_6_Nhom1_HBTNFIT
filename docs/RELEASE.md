# Ứng viên nộp bài HBTNFIT

Mốc ứng viên đầu tiên: `v0.1.0-rc.1`. Đây là bản dùng tổng duyệt và chuẩn bị nộp bài; tag không có nghĩa ứng dụng đã được deploy production hoặc đã hoàn tất đánh giá AI trên tập ảnh thực tế.

## Phạm vi tích hợp

- Đăng ký, đăng nhập, phiên đăng nhập và đăng xuất bằng tên đăng nhập/mật khẩu.
- Hồ sơ, thời hạn cân nặng và mục tiêu kcal/protein/carb/chất béo; đồng bộ với Ăn uống.
- Nhận diện ảnh qua Gemini, kiểm tra/sửa món và khẩu phần, xác nhận vào thực đơn, lịch sử và dữ liệu riêng theo tài khoản.
- Giáo án PPL/Upper-Lower, bài tập cụ thể, tiến độ theo buổi và lịch đi tập/nghỉ.
- Công cụ khóa nhãn, tách dev/test/smoke, ghi phản hồi Gemini và chấm nhận diện tên món.
- Tài liệu chạy local, cấu hình frontend Vercel/backend lưu bền và sao lưu dữ liệu.

Các PR chức năng đã merge được tích hợp từ nền `develop` commit `0865be5`; tại lúc chuẩn bị RC, nội dung `main` và `develop` tương ứng nhau. Bản RC bổ sung lệnh kiểm tra tập trung và tài liệu đóng phiên bản.

## Kiểm tra một lệnh

Tạo/chọn môi trường Python trên chính máy đang chạy, cài `backend/requirements-dev.txt` và Node.js phù hợp. Tại gốc repo:

```powershell
.\.venv\Scripts\python.exe scripts/check_release.py
```

Nếu dùng môi trường `.local/venv`, thay đường dẫn Python bằng `.\.local\venv\Scripts\python.exe`. macOS/Linux sau khi kích hoạt môi trường: `python scripts/check_release.py`.

Lệnh lần lượt chạy pytest, Ruff, kiểm tra định dạng backend, npm ci, Prettier, build và CLI đánh giá. Nó dừng ngay nếu một bước thất bại. Log và `checks.json` được ghi trong `.local/release-checks/<mã-lần-chạy>/`, không đưa lên Git mặc định. Mỗi lần chạy ghi commit và trạng thái thay đổi cục bộ để đối chiếu.

Mốc hiện tại kỳ vọng có 132 test backend đạt. Nếu thêm test sửa lỗi sau đó, báo đúng số lượng thực tế của phiên bản mới. Kết quả tự động không thay thế kiểm tra dịch vụ Gemini thật hoặc dữ liệu thật.

## Tổng duyệt chức năng

1. Đăng ký hai tài khoản; kiểm tra đăng nhập sai, đăng xuất và tải lại trang.
2. Lưu mục tiêu hợp lệ, chặn mục tiêu mâu thuẫn; chuyển Ăn uống kiểm tra đủ bốn chỉ số.
3. Tải ảnh, kiểm tra món, sửa khẩu phần và xác nhận; kiểm tra tổng thực đơn, sửa/xóa và lịch sử ảnh.
4. Kiểm tra lỗi AI/kết nối không làm mất dữ liệu đã lưu; nhập món thủ công vẫn dùng được.
5. Chọn giáo án, xem bài cụ thể, ghi nghỉ/đi tập, hoàn thành bài và kiểm tra tiến độ sau tải lại.
6. Đổi tài khoản để xác minh không thấy dữ liệu tài khoản khác; kiểm tra desktop, tablet và điện thoại.
7. Kiểm tra trên database demo riêng. Sao lưu trước khi nâng cấp database thật; không xóa dữ liệu thật để chữa lỗi.

## Giới hạn được ghi nhận

- Lần đánh giá Gemini có minh chứng hiện dùng hai ảnh tổng hợp ở split smoke. Lần chạy ngày 25/11/2026 có F1 66,67% và 1/2 ảnh đúng toàn bộ theo nhãn khóa; không suy rộng thành độ chính xác thực tế.
- Chưa có minh chứng đánh giá cuối trên tập ảnh thực tế đã được hai người duyệt độc lập và tách dev/test. Đây là phần dữ liệu/nghiệm thu còn phải bổ sung, không được ghi hoàn tất chỉ dựa vào 132 test hoặc hai ảnh demo.
- Dinh dưỡng CSV và ước tính từ ảnh còn giới hạn về nguồn/độ chính xác; người dùng cần kiểm tra trước khi xác nhận.
- Cần cấu hình Gemini, quota, domain và nơi lưu dữ liệu bền cho môi trường sử dụng thật. Cấu hình deploy đã chuẩn bị; RC không xác nhận đã triển khai production.
- Cấu hình `.idea/` là riêng từng máy. Sau khi cập nhật bản dọn tài liệu, chọn lại Python interpreter đang dùng nếu IDE mất cấu hình; không thay đổi hoặc xóa database để chữa lỗi IDE.

## Quy tắc từ ngày 26 tháng 11

Từ 26/11 chỉ nhận sửa lỗi và hoàn thiện minh chứng/tài liệu trên phạm vi đã chốt. Mỗi lỗi có bước tái hiện, phần sửa, kiểm tra phù hợp và PR vào `develop`. Tổng duyệt lại trước khi đưa bản sửa vào `main`.

Không di chuyển tag RC đã công bố. Nếu sửa mã sau RC1, tạo tag mới như `v0.1.0-rc.2`, ghi thay đổi và kiểm tra của đúng commit đó. Chỉ chọn phiên bản nộp cuối khi các giới hạn ảnh hưởng yêu cầu môn học đã được xử lý hoặc báo cáo rõ.

## Lấy đúng bản ứng viên

Sau khi tag đã được công bố:

```bash
git fetch origin --tags
git switch --detach v0.1.0-rc.1
```

Lệnh trên dùng để xem/chạy lại bản đã chốt. Khi sửa lỗi, quay lại nhánh làm việc của mình và cập nhật từ `origin/develop`; không sửa trực tiếp trên tag.

File `.env`, database, ảnh người dùng, khóa ký và thư mục môi trường Python là dữ liệu riêng của từng máy, không nằm trong gói source. Xem [DEPLOYMENT.md](DEPLOYMENT.md) để cấu hình, [DEMO.md](DEMO.md) để trình bày và [evaluation/README.md](../evaluation/README.md) để đánh giá AI.
