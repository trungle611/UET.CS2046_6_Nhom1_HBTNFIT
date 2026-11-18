# Quy trình đóng góp

## Bắt đầu task

```powershell
git clone https://github.com/trungle611/UET.CS2046_6_Nhom1_HBTNFIT.git
cd UET.CS2046_6_Nhom1_HBTNFIT
git config user.name "Ten GitHub cua ban"
git config user.email "email-da-lien-ket-github"
git switch develop
git pull --ff-only origin develop
git switch -c feat/MSSV-ten-chuc-nang
```

Mỗi người dùng danh tính Git của mình. Chia sẻ trước khi cùng sửa `main.py`, `App.jsx` hoặc `style.css`.

## Commit và PR

```powershell
git status
git diff
git add duong-dan-file-thuoc-task
git diff --cached
git commit -m "feat(food): them chon bua an"
git push -u origin feat/MSSV-ten-chuc-nang
```

Tạo PR từ branch này vào `develop`, gắn task Coreach, ghi cách kiểm tra và chọn một người review. Dùng merge commit để giữ lịch sử đóng góp.

Không commit `.env`, key, mật khẩu, database, log, ảnh cá nhân, `.venv`, `node_modules` hoặc `dist`. `.env.example` chỉ chứa giá trị trống/mẫu.

## Đồng bộ khi task khác đã merge

```powershell
git fetch origin
git merge origin/develop
```

Nếu conflict, đọc và sửa từng file, chạy kiểm tra rồi commit. Không force-push `main`/`develop`.

## Hoàn thành task

- Chạy test và build liên quan theo README.
- Reviewer chạy lại các bước kiểm tra rồi xác nhận PR.
- Sau merge, gửi link PR/commit, ảnh/video và kết quả kiểm thử vào task Coreach.
- Ghi rõ phần kế thừa từ bản nền, phần tự bổ sung, test hoặc sửa lỗi thực tế.

## Công cụ

Ruff dùng cho Python, Prettier dùng cho React/CSS. Chạy `python -m ruff format backend` hoặc `npm run format` trong frontend khi cần định dạng.

Stack Vite 6.4.5 được giữ tương thích bản tham chiếu. Lockfile được tạo lại trong repo mới; `npm audit` tại lúc tạo khung báo 0 lỗ hổng. Thành viên dùng `npm ci` để giữ đúng dependency đã khóa và kiểm tra lại audit khi nâng cấp. Bản khung chỉ cấu hình dev server tại local.
