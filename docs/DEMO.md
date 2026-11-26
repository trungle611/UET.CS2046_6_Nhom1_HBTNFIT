# Demo HBTNFIT

Phương án chính: trình bày trên **một laptop chạy local**, máy chiếu dùng cùng trình duyệt. Dành khoảng 8–10 phút để đi qua mục tiêu → món ăn → lịch sử → tập luyện → dữ liệu riêng. Tunnel chỉ dùng khi cần cho người xem truy cập, sau khi local đã chạy ổn.

## 1. Chuẩn bị trước buổi trình bày

1. Chọn commit/tag đã qua tổng duyệt, ghi lại bằng `git log -1 --oneline` và `git status`. Giữ nguyên phiên bản trong buổi trình bày.
2. Trên máy trình bày, cài sẵn thư viện và chạy `scripts/check_release.py` theo [RELEASE.md](RELEASE.md). Lưu thư mục log đạt; không dành thời gian trình bày để cài thư viện hoặc chờ chạy toàn bộ test.
3. Chạy backend và frontend theo [DEPLOYMENT.md](DEPLOYMENT.md). Mở [health](http://127.0.0.1:8000/api/health) và [ứng dụng](http://127.0.0.1:5173); kiểm tra hai terminal không có traceback.
4. Dùng dữ liệu demo riêng của nhóm. Giữ nguyên cấu hình/database đang có nếu trong đó chứa dữ liệu cần bảo toàn. Muốn tách DB demo, dừng backend rồi cấu hình `DATABASE_URL` bằng đường dẫn tuyệt đối mới, `SCAN_UPLOAD_DIR` bằng thư mục ảnh demo riêng; lưu cấu hình cũ ở nơi riêng trước khi đổi.
5. Chuẩn bị tài khoản A đã có một ít dữ liệu để xem lịch sử, tài khoản B trống để chứng minh dữ liệu riêng và một tên mới để đăng ký trực tiếp. Lịch sử ngày trước cần được ghi thật từ trước; không sửa thời gian hệ thống hoặc nhãn ngày để tạo minh chứng.
6. Chuẩn bị một ảnh món rõ, dưới 5 MB, JPG/PNG/WEBP, được phép sử dụng. Hai ảnh trong `frontend/public/demo/` là ảnh tổng hợp và cần gọi đúng là ảnh demo nếu dùng.
7. Thử Gemini thật trước buổi trình bày, kiểm tra quyền truy cập model/quota. Giữ riêng key trong `backend/.env`. Lượt nhận diện và gợi ý đều sử dụng dịch vụ bên ngoài; hạn chế gọi lặp lại khi không cần.
8. Chuẩn bị một video hoặc bộ ảnh ghi thao tác thành công từ đúng bản ứng dụng, ghi rõ thời điểm và phiên bản. Có thể dùng khi mất mạng/dịch vụ AI lỗi, và giới thiệu đó là bản ghi trước.
9. Nếu có laptop dự phòng, cài sẵn môi trường riêng và thử từ trước. Mỗi máy tự tạo môi trường Python; không chép `.venv` giữa Windows/Mac. Dữ liệu demo/backup riêng không đưa lên repo công khai.

## 2. Kịch bản 8–10 phút

| Thời gian | Thao tác | Điểm cần thể hiện |
| --- | --- | --- |
| 0:00–1:00 | Giới thiệu bài toán, đăng ký bằng một tên mới hoặc đăng nhập A | Tài khoản dùng tên đăng nhập/mật khẩu; thông tin cá nhân theo từng người |
| 1:00–2:15 | Vào Cá nhân, nhập mục tiêu, tính thử và lưu sang Ăn uống | Kcal/protein/carb/chất béo được tính và đồng bộ; thử một mục tiêu mâu thuẫn rồi sửa về hợp lệ |
| 2:15–4:15 | Chọn bữa, tải một ảnh, kiểm tra/đổi tên món, sửa khẩu phần, xác nhận | AI đưa gợi ý; người dùng kiểm tra. Tô/quả/đĩa dùng số nguyên, g/ml có thể thập phân. Chỉ sau xác nhận món mới được cộng |
| 4:15–5:15 | Sửa lượng hoặc xóa món; mở lịch sử ăn/ảnh | Tổng dinh dưỡng cập nhật theo dữ liệu đã lưu; lịch sử có ngày và ảnh tương ứng |
| 5:15–6:45 | Chọn PPL/Upper-Lower, xem bài cụ thể, chọn nghỉ rồi đi tập, hoàn thành một bài và tải lại | Lịch đỏ/xanh và tiến độ được giữ; buổi tiếp theo dựa trên tiến độ |
| 6:45–7:45 | Đăng xuất A, đăng nhập B, sau đó quay lại A | B không có dữ liệu cá nhân của A; A vẫn giữ dữ liệu. Có thể trình bày ở cửa sổ thường và ẩn danh để không chia sẻ phiên |
| 7:45–8:30 | Thu cửa sổ hoặc dùng chế độ thiết bị 390 px | Menu, biểu mẫu và nút bấm hoạt động trên màn hình nhỏ |
| 8:30–10:00 | Mở log kiểm tra, kết quả đánh giá AI có sẵn và nêu giới hạn | Báo đúng số test của commit đang dùng; tách kiểm thử giả lập, Gemini thật và dữ liệu đánh giá |

Nếu còn thời gian và Gemini ổn: vào Cá nhân → **Lưu và nhận gợi ý AI** → chọn cách ăn → đổi sáng/trưa/tối → nhập lượng và tick món. Phần này có thêm một lượt gọi AI; không bắt buộc đưa vào luồng trình bày ngắn nếu đã hết thời gian.

Gợi ý dữ liệu nhập để kiểm tra biểu mẫu: tuổi 22, cao 170 cm, cân hiện tại 65 kg, mong muốn 68 kg, chọn Tăng cân và một ngày hợp lệ trong tương lai. Đây là dữ liệu thử giao diện. Các chỉ số dinh dưỡng chỉ là ước tính của ứng dụng, không bảo đảm đạt mức cân vào hạn đã chọn.

## 3. Khi Gemini lỗi hoặc hết quota

1. Đọc thông báo trên giao diện, giới thiệu trạng thái dịch vụ. Hệ thống có ngân sách gọi AI tối đa 45 giây; không bấm tải lại liên tục để tăng thêm yêu cầu.
2. Sau lỗi nhận diện, màn hình có phần nhập tay. Nhập tên món vào **Tên món bạn nhận ra**, chọn món phù hợp ở **Hoặc chọn món trong danh mục**, nhập lượng rồi xác nhận. Dùng dữ liệu CSV để minh họa tính khẩu phần và lưu thực đơn.
3. Nếu món ngoài danh mục thì chỉ nhập giá trị dinh dưỡng từ nguồn đã có; không tự điền số để diễn như AI đã nhận diện được.
4. Với gợi ý thực đơn lỗi, mục tiêu đã lưu vẫn còn. Tiếp tục các phần mục tiêu, thực đơn đã lưu, lịch sử và tập luyện.
5. Dùng video/ảnh ghi trước nếu cần trình bày riêng đoạn nhận diện thành công; nói rõ đó là bản ghi. Không gọi thao tác nhập tay hay phản hồi giả lập là nhận diện AI trực tiếp.

Đây là phương án dự phòng cho dịch vụ AI. Nếu backend local cũng dừng, cần chạy lại backend để lưu món hoặc dùng laptop/bản ghi dự phòng.

## 4. Phương án tunnel và môi trường trình bày

- Ưu tiên local trên máy chiếu để giảm phụ thuộc đường truyền truy cập của người xem; gọi Gemini thật vẫn cần mạng.
- Nếu dùng tunnel, trỏ vào frontend đang chạy và cấu hình hostname đúng theo [DEPLOYMENT.md](DEPLOYMENT.md). Thử toàn bộ luồng từ điện thoại ngoài máy trước buổi demo.
- Dùng một người thao tác trình bày chính. Cho nhiều người quét cùng lúc là một tình huống tải riêng, không cần đưa vào kịch bản chức năng ngắn.
- Giữ backend/frontend hoạt động trong suốt buổi trình bày; không pull code hoặc đổi cấu hình giữa các bước.

## 5. Minh chứng nên giữ

- Commit/tag, trạng thái working tree và thư mục log của lần kiểm tra đạt.
- Ảnh mục tiêu hợp lệ, lỗi mục tiêu mâu thuẫn, bốn chỉ số ở Ăn uống.
- Ảnh trước/sau xác nhận món, khẩu phần và lịch sử.
- Ảnh lịch tập đỏ/xanh, tiến độ sau tải lại.
- Hai ảnh cùng trang của A và B thể hiện dữ liệu riêng; ảnh giao diện 390 px.
- Kết quả gọi AI thật với nhãn/lock, `run.json`, phản hồi và `summary.json` nếu trình bày đánh giá AI.

Lưu minh chứng ở thư mục riêng ngoài Git; không chụp mật khẩu hiện rõ, token hoặc khóa API.

## 6. Những giới hạn cần nói đúng

Lần đánh giá có minh chứng ngày 25/11/2026 mới gồm **hai ảnh tổng hợp ở split smoke**, F1 66,67%, 1/2 ảnh đúng toàn bộ theo nhãn đã khóa. Đây chưa là kết quả trên bộ ảnh thực tế tách biệt. Các test backend và tổng duyệt UI dùng giả lập không thay thế đánh giá độ chính xác của Gemini thật. Chưa xác nhận triển khai production; demo local/tunnel và triển khai chính thức là các môi trường riêng.
