import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from config import PALETTE
from utils import chart_layout, section_title, analytical_insight, empty_chart, correlation_text


def render(df):
    section_title("Khách hàng & Trải nghiệm giao hàng", "Phân tích đóng góp của nhóm khách hàng và kiểm tra mối liên hệ giữa tốc độ giao hàng với đánh giá.", "customers")
    cust = df.groupby("Customer_Type", as_index=False).agg(Revenue=("Revenue", "sum"), Transactions=("Transaction_ID", "nunique"))
    pay = df.groupby("Payment_Method", as_index=False).agg(Revenue=("Revenue", "sum"), Transactions=("Transaction_ID", "nunique"))
    if not cust.empty and not pay.empty:
        cust["Revenue_Share"] = cust["Revenue"] / cust["Revenue"].sum() * 100
        pay["Transaction_Share"] = pay["Transactions"] / pay["Transactions"].sum() * 100
        c_hi, c_lo = cust.loc[cust["Revenue"].idxmax()], cust.loc[cust["Revenue"].idxmin()]
        p_hi = pay.loc[pay["Transactions"].idxmax()]
        analytical_insight(
            "INSIGHT 06 · CUSTOMER & PAYMENT",
            f"{c_hi['Customer_Type']} đóng góp doanh thu lớn nhất; {p_hi['Payment_Method']} là phương thức phổ biến nhất",
            f"{c_hi['Customer_Type']} đóng góp {c_hi['Revenue_Share']:.1f}% doanh thu; {c_lo['Customer_Type']} đóng góp {c_lo['Revenue_Share']:.1f}%. {p_hi['Payment_Method']} chiếm {p_hi['Transaction_Share']:.1f}% giao dịch.",
            "Biểu đồ nhóm khách hàng dùng tỷ trọng doanh thu; biểu đồ thanh toán dùng tỷ trọng số giao dịch. Hai mẫu số được phân biệt rõ.",
            "Đánh giá giá trị đơn trung bình và tần suất mua của từng nhóm trước khi thiết kế ưu đãi riêng; không suy ra lòng trung thành chỉ từ tổng doanh thu.",
            "Biểu đồ thanh ngang phù hợp để so sánh các nhóm rời rạc và sắp thứ hạng; nhãn vừa cho biết giá trị tuyệt đối vừa cho biết tỷ trọng để trả lời hai câu hỏi khác nhau.",
            "Tỷ trọng doanh thu và tỷ trọng giao dịch có mẫu số khác nhau, không thể so sánh trực tiếp. Tổng doanh thu chưa phản ánh giá trị đơn trung bình hay hành vi quay lại.",
        )
        a, b = st.columns(2)
        with a:
            section_title("Đóng góp doanh thu theo nhóm khách hàng", "Nhãn hiển thị doanh thu và tỷ trọng doanh thu.", "customers")
            plot = cust.sort_values("Revenue").copy()
            plot["Revenue_M"] = plot["Revenue"] / 1e6
            plot["Label"] = plot.apply(lambda r: f"{r['Revenue_M']:.2f}M · {r['Revenue_Share']:.1f}%", axis=1)
            fig = px.bar(plot, x="Revenue_M", y="Customer_Type", orientation="h", color="Customer_Type",
                         color_discrete_sequence=PALETTE, text="Label",
                         labels={"Revenue_M": "Doanh thu (triệu ₫)", "Customer_Type": "Nhóm khách hàng"})
            fig.update_traces(textposition="outside", cliponaxis=False)
            chart_layout(fig, 330, False)
            st.plotly_chart(fig, use_container_width=True)
        with b:
            section_title("Cơ cấu phương thức thanh toán", "Tỷ trọng theo số giao dịch, không phải theo doanh thu.", "payments")
            plot = pay.sort_values("Transactions").copy()
            plot["Label"] = plot.apply(lambda r: f"{int(r['Transactions'])} · {r['Transaction_Share']:.1f}%", axis=1)
            fig = px.bar(plot, x="Transactions", y="Payment_Method", orientation="h", color="Payment_Method",
                         color_discrete_sequence=PALETTE, text="Label",
                         labels={"Transactions": "Số giao dịch", "Payment_Method": "Phương thức"})
            fig.update_traces(textposition="outside", cliponaxis=False)
            chart_layout(fig, 330, False)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    valid = df.dropna(subset=["Delivery_Days", "Customer_Rating"]) if {"Delivery_Days", "Customer_Rating"}.issubset(df.columns) else df.iloc[0:0]
    if len(valid) >= 3 and valid["Delivery_Days"].nunique() > 1 and valid["Customer_Rating"].nunique() > 1:
        pearson_r, p_value, spearman_r, n = correlation_text(valid, "Delivery_Days", "Customer_Rating")
        direction = "nghịch" if pearson_r < 0 else "thuận" if pearson_r > 0 else "không rõ"
        strength = "mạnh" if abs(spearman_r) >= .6 else "trung bình" if abs(spearman_r) >= .3 else "yếu"
        by_days = valid.groupby("Delivery_Days", as_index=False).agg(Average_Rating=("Customer_Rating", "mean"), Transactions=("Transaction_ID", "nunique"))
        fastest = by_days.loc[by_days["Delivery_Days"].idxmin()]
        slowest = by_days.loc[by_days["Delivery_Days"].idxmax()]
        analytical_insight(
            "INSIGHT 07 · DELIVERY EXPERIENCE",
            f"Thời gian giao hàng và điểm đánh giá có mối liên hệ {direction}, {strength}",
            f"Pearson r = {pearson_r:.3f}; Spearman ρ = {spearman_r:.3f}; p-value = {p_value:.3g}; N = {n}. Điểm trung bình ở nhóm giao {int(fastest['Delivery_Days'])} ngày là {fastest['Average_Rating']:.2f}/5, so với {slowest['Average_Rating']:.2f}/5 ở nhóm giao {int(slowest['Delivery_Days'])} ngày.",
            "Scatter plot cho thấy từng giao dịch; Pearson đo liên hệ tuyến tính, Spearman kiểm tra xu hướng đơn điệu và ít nhạy hơn với ngoại lệ.",
            "Ưu tiên rà soát quy trình giao hàng ở nhóm thời gian dài. Đây là mối liên hệ quan sát được, chưa chứng minh giao hàng chậm là nguyên nhân duy nhất làm giảm đánh giá.",
            "Scatter plot phù hợp vì cả thời gian giao và điểm đánh giá đều là biến số; từng điểm cho thấy độ phân tán, cụm và ngoại lệ, đường xu hướng giúp đọc chiều quan hệ.",
            "Chỉ dùng giao dịch có đủ dữ liệu và có biến thiên ở cả hai biến; điểm chồng lấp có thể làm mật độ khó đọc, còn tương quan không chứng minh nhân quả.",
        )
        section_title("Thời gian giao hàng và điểm đánh giá", "Mỗi điểm là một giao dịch hợp lệ; đường xu hướng chỉ mô tả quan hệ tổng quát.", "delivery")
        fig = px.scatter(valid, x="Delivery_Days", y="Customer_Rating", color="Store", color_discrete_sequence=PALETTE,
                         hover_data=["Transaction_ID", "Product", "Customer_Type"],
                         labels={"Delivery_Days": "Thời gian giao hàng (ngày)", "Customer_Rating": "Điểm đánh giá (1–5)"})
        slope, intercept = np.polyfit(valid["Delivery_Days"], valid["Customer_Rating"], 1)
        x_line = np.linspace(valid["Delivery_Days"].min(), valid["Delivery_Days"].max(), 30)
        fig.add_scatter(x=x_line, y=slope * x_line + intercept, mode="lines", name="Xu hướng tuyến tính",
                        line=dict(color="#E65B67", dash="dash", width=2))
        fig.update_yaxes(range=[0, 5], dtick=1)
        chart_layout(fig, 390)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Phân tích dùng {n:,}/{len(df):,} giao dịch có đủ dữ liệu. Tương quan không chứng minh quan hệ nhân quả.")
    else:
        st.info("Không đủ giao dịch hợp lệ hoặc biến thiên dữ liệu để phân tích mối liên hệ giữa giao hàng và đánh giá.")
        st.plotly_chart(empty_chart("Cần ít nhất 3 giao dịch hợp lệ và có biến thiên ở cả hai biến."), use_container_width=True)
