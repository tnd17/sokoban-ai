## Cài đặt

pip install pygame

## Chạy dự án

python main.py

## Lưu ý

Chức năng Analysis:
- Chức năng này hoạt động nhờ vào file stats_cache.json
- Khi mới chạy project, hệ thống sẽ kiểm tra file này, nếu có rồi => ok; nếu chưa có, hệ thống sẽ tự thống kê để tạo file này. Trong thời gian file chưa được tạo thành, không thể sử dụng chức năng thống kê. Nếu tắt project khi file chưa tạo thành, file sẽ được tạo lại trong những lần run tiếp theo
- Nếu muốn thay đổi, cập nhật map, chỉ cần xóa file stats_cache.json đi, trong lần run tiếp theo chức năng thống kê sẽ chạy lại và cập nhật thống kê mới