# Dữ liệu

Danh mục được nạp từ hai file CSV khi backend khởi động:

- `foods_team_unverified.csv`: thực phẩm với giá trị dinh dưỡng theo 100 g.
- `serving_items_team_unverified.csv`: món ăn và đồ uống theo khẩu phần, có đơn vị và khối lượng tham chiếu.

`backend/app/catalog.py` kiểm tra số liệu, nguồn và cập nhật danh mục theo ID. Các bản ghi do nhóm tổng hợp chưa được coi là dữ liệu dinh dưỡng đã kiểm chứng.

- Tách thực phẩm theo 100 g và món ăn theo khẩu phần.
- Ghi rõ đơn vị, nguồn và trạng thái kiểm chứng.
- Không commit database hoặc ảnh cá nhân.
