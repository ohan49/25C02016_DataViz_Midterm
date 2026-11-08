# Urban Retail Analytics

Ứng dụng Streamlit phân tích dữ liệu bán lẻ HCMC 2025.

## Chạy trên Windows

1. Giải nén toàn bộ dự án.
2. Mở thư mục `urban_retail_modular` bằng VS Code.
3. Mở Terminal tại thư mục chứa `app.py`.
4. Chạy:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Hoặc nhấp đúp `run_app.bat`.

## Cấu trúc

- `app.py`: điểm khởi chạy, sidebar, điều hướng và bộ lọc toàn cục.
- `ant_icons.py`: bộ SVG icon phong cách Ant Design, không cần cài React.
- `config.py`: tên trang, màu sắc và ánh xạ icon.
- `styles.py`: CSS, hero và KPI.
- `data_loader.py`: nạp, làm sạch và lọc dữ liệu; gắn cờ Isolation Forest.
- `utils.py`: định dạng số, tiêu đề, insight và cấu hình biểu đồ.
- `views/`: từng trang phân tích.
- `data/`: CSV nguồn.

## Quy ước biểu đồ

- Doanh thu/lợi nhuận hiển thị bằng triệu đồng khi đặt cạnh nhau.
- Biên lợi nhuận được tính bằng tổng lợi nhuận / tổng doanh thu.
- Biểu đồ có nhãn giá trị và đơn vị phù hợp; biểu đồ phân tán dùng hover để tránh chồng nhãn.
- Tương quan không được diễn giải thành quan hệ nhân quả.
- Cờ bất thường là tín hiệu rà soát, không phải bằng chứng gian lận.

## Ghi chú

Không đưa thư mục `.venv` vào ZIP. Môi trường ảo sẽ được tạo lại trên máy chạy ứng dụng.

## Nguyên tắc phân tích và diễn giải insight

Mỗi trang phân tích sử dụng cấu trúc: **phát hiện → bằng chứng trực quan → vì sao chọn biểu đồ → đánh giá/giới hạn → hàm ý hành động**. Insight và số liệu được tính lại theo bộ lọc toàn cục hiện hành.

- Lý do chọn biểu đồ gắn với câu hỏi phân tích: so sánh nhóm dùng bar, xu hướng theo thời gian dùng line, quan hệ giữa hai biến số dùng scatter; biểu đồ kết hợp được giải thích rõ khi dùng hai trục khác đơn vị.
- Phần đánh giá nêu giới hạn diễn giải như cỡ mẫu, ngoại lệ, trục kép, dữ liệu thiếu hoặc tương quan không hàm ý nhân quả; không coi hình thức biểu đồ là bằng chứng vượt quá dữ liệu.

- Doanh thu và lợi nhuận được so sánh bằng cùng đơn vị; biên lợi nhuận được tính bằng tổng lợi nhuận / tổng doanh thu.
- Phân tích theo tháng đối chiếu doanh thu, số giao dịch và giá trị trung bình mỗi giao dịch. Dữ liệu một năm không đủ để khẳng định mùa vụ lặp lại.
- Discount được biểu diễn theo phần trăm; tương quan Pearson/Spearman không chứng minh quan hệ nhân quả.
- Phân tích giao hàng chỉ dùng các giao dịch có đủ Delivery_Days và Customer_Rating, đồng thời công bố cỡ mẫu hợp lệ.
- Giao dịch lỗ (Profit < 0) được phân biệt với quan sát bất thường do Isolation Forest gắn cờ. Bất thường không đồng nghĩa gian lận.
# 25C02016_DataViz_Midterm
# 25C02016_DataViz_Midterm
