# Phân công triển khai từ bản khung

| Thành viên | Task chính | Branch ví dụ |
|---|---|---|
| Lê Đình Trung — 25023540 | Gemini, nhận diện, xử lý lỗi AI, tích hợp release | feat/25023540-gemini-recognition |
| Nguyễn Danh Nhân — 25023506 | CSV/catalog, database, tài khoản, cô lập dữ liệu | feat/25023506-food-catalog |
| Nguyễn Minh Hoàng — 25023478 | Ăn uống, khẩu phần, lịch sử, mục tiêu và tập luyện | feat/25023478-food-flow |
| Nguyễn Xuân Bình — 25023444 | Responsive, bộ ảnh đánh giá, kiểm thử chéo, tài liệu | test/25023444-cross-testing |

## Thứ tự tích hợp

1. CSV, model/schema, database và tài khoản.
2. Dịch vụ nhận diện Gemini và ghép món theo CSV.
3. Ăn uống, khẩu phần, checklist và lịch sử; mục tiêu; giáo án và lịch tập.
4. Responsive, kiểm thử chéo, bộ ảnh đánh giá AI và báo cáo.
5. Review, tích hợp và tạo tag bản nộp từ `main`.

Thành viên có thể làm song song trên branch riêng; thống nhất schema/API trước khi nối frontend. Bổ sung test theo chức năng thực tế, không thay test health hiện có bằng kết quả giả.

## Minh chứng Coreach

```text
Task:
Người thực hiện / người tham gia:
Branch:
Pull Request:
Commit:
Nội dung đã làm:
Kết quả test/build:
Ảnh/video:
Người review:
Vấn đề còn lại:
```

Phân công này là định hướng triển khai; deadline và trách nhiệm từng task lấy theo phân công đã thống nhất trên Coreach.
