import streamlit as st
import plotly.express as px
from config import COLORS
from utils import money_short, chart_layout, section_title, analytical_insight, empty_chart


def render(df):
    section_title(
        "Rủi ro lợi nhuận & Giao dịch bất thường",
        "Phân biệt giao dịch có lợi nhuận âm với quan sát khác biệt do mô hình thống kê phát hiện.",
        "risk",
    )
    loss_df = df[df["Is_Loss"]].copy()
    anomaly_df = df[df["Anomaly_Label"] == -1].copy()
    loss_rate = len(loss_df) / len(df) * 100 if len(df) else 0
    loss_amount = abs(loss_df["Profit"].sum()) if len(loss_df) else 0

    if len(loss_df):
        worst = loss_df.loc[loss_df["Profit"].idxmin()]
        by_category = loss_df.groupby("Product_Category").size().sort_values(ascending=False)
        most_loss_category = by_category.index[0]
        finding = (
            f"{len(loss_df)} giao dịch có lợi nhuận âm ({loss_rate:.1f}% tập đang lọc), "
            f"tổng mức lỗ cộng dồn {money_short(loss_amount)}. Giao dịch lỗ lớn nhất là "
            f"{worst['Transaction_ID']} với {money_short(abs(worst['Profit']))}; "
            f"{most_loss_category} có nhiều giao dịch lỗ nhất ({int(by_category.iloc[0])})."
        )
        action = "Ưu tiên rà soát giao dịch lỗ lớn nhất, sau đó kiểm tra giá vốn, mức giảm giá và giá bán của danh mục có nhiều giao dịch lỗ."
    else:
        finding = "Không ghi nhận giao dịch có lợi nhuận âm trong tập dữ liệu đang lọc."
        action = "Tiếp tục theo dõi khi thay đổi bộ lọc; không nên diễn giải việc không có giao dịch lỗ trong mẫu con là không có rủi ro toàn hệ thống."

    analytical_insight(
        "INSIGHT 08 · LOSS & ANOMALY REVIEW",
        f"{len(loss_df)} giao dịch lỗ cần rà soát; {len(anomaly_df)} quan sát được mô hình gắn cờ khác biệt",
        finding,
        "Giao dịch lỗ được xác định trực tiếp bằng Profit < 0. Isolation Forest đánh dấu các quan sát khác biệt đa biến, không đồng nghĩa với giao dịch lỗ.",
        action,
        "Scatter plot phù hợp để khảo sát quan hệ giữa doanh thu và lợi nhuận ở cấp giao dịch; đường 0 phân biệt lãi/lỗ, màu cho biết quan sát được mô hình gắn cờ.",
        "Điểm chồng lấp có thể che khuất mật độ; cờ mô hình chỉ là tín hiệu rà soát, không phải kết luận sai phạm. Tập lọc nhỏ không làm mô hình được huấn luyện lại.",
    )

    a, b, c, d = st.columns(4)
    a.metric("Giao dịch lỗ", f"{len(loss_df):,}", f"{loss_rate:.2f}% tập đã lọc")
    b.metric("Bất thường tiềm năng", f"{len(anomaly_df):,}", "Isolation Forest")
    c.metric("Tổng mức lỗ cộng dồn", money_short(loss_amount))
    d.metric("Lợi nhuận toàn tập", money_short(df["Profit"].sum()))

    section_title("Doanh thu và lợi nhuận theo giao dịch", "Đường ngang tại 0 phân tách giao dịch lãi và lỗ; màu biểu thị cờ bất thường của mô hình.", "alert")
    if not df.empty:
        fig = px.scatter(
            df, x="Revenue", y="Profit", color="Anomaly_Status",
            color_discrete_map={"Thông thường": COLORS["blue"], "Bất thường tiềm năng": COLORS["red"]},
            hover_data=["Transaction_ID", "Store", "Product_Category", "Product", "Discount"],
            labels={"Revenue": "Doanh thu (₫)", "Profit": "Lợi nhuận (₫)", "Anomaly_Status": "Cờ mô hình"},
        )
        fig.add_hline(y=0, line_dash="dash", line_color="#E65B67", annotation_text="Lợi nhuận = 0")
        fig.update_xaxes(tickprefix="₫", tickformat="~s")
        fig.update_yaxes(tickprefix="₫", tickformat="~s")
        chart_layout(fig, 410)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)

    if not loss_df.empty:
        section_title("Các giao dịch lỗ cần ưu tiên kiểm tra", "Sắp xếp từ khoản lỗ lớn nhất; bảng giúp truy ngược sản phẩm, cửa hàng và mức giảm giá.", "risk")
        cols = [c for c in ["Transaction_ID", "Date", "Store", "Product_Category", "Product", "Discount", "Revenue", "Cost", "Profit"] if c in loss_df.columns]
        st.dataframe(loss_df[cols].sort_values("Profit", ascending=True), use_container_width=True, hide_index=True)
    else:
        st.success("Không có giao dịch lỗ trong tập dữ liệu đang lọc.")

    if not anomaly_df.empty:
        with st.expander(f"Kiểm tra {len(anomaly_df)} quan sát được gắn cờ bất thường"):
            cols = [c for c in ["Transaction_ID", "Store", "Product_Category", "Revenue", "Cost", "Profit", "Discount", "Anomaly_Status"] if c in anomaly_df.columns]
            st.dataframe(anomaly_df[cols], use_container_width=True, hide_index=True)
    st.caption("Lưu ý phương pháp: Isolation Forest được huấn luyện trên dataset gốc trước khi áp dụng bộ lọc. Cờ bất thường là tín hiệu sàng lọc, không phải kết luận sai phạm.")
