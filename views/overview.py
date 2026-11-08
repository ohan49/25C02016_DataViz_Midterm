"""Trang tổng quan: 5 phát hiện kinh doanh chính, mỗi phát hiện đi kèm visualization phù hợp."""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS, PALETTE
from utils import money_short, chart_layout, section_title, empty_chart, analytical_insight, correlation_text


def render(df):
    section_title(
        "Tổng quan · 5 phát hiện kinh doanh chính",
        "Mỗi phần bắt đầu bằng một câu hỏi phân tích, tiếp theo là bằng chứng trực quan và hàm ý kinh doanh. Các kết quả thay đổi theo bộ lọc toàn cục.",
        "overview",
    )

    revenue = df["Revenue"].sum()
    profit = df["Profit"].sum()
    margin = profit / revenue * 100 if revenue else 0
    n_tx = df["Transaction_ID"].nunique()
    loss_df = df[df["Profit"] < 0]
    loss_transactions = loss_df["Transaction_ID"].nunique()
    loss_rate = loss_transactions / n_tx * 100 if n_tx else 0

    st.caption(
        f"Phạm vi: {df['Date'].min():%d/%m/%Y}–{df['Date'].max():%d/%m/%Y} · "
        f"{len(df):,} dòng / {n_tx:,} giao dịch · {df['Store'].nunique()} cửa hàng · "
        f"{df['Product_Category'].nunique()} danh mục. "
        f"Có {loss_transactions:,} giao dịch lỗ ({loss_rate:.1f}%) · "
        f"biên lợi nhuận tổng hợp {margin:.2f}%. Số liệu thay đổi theo bộ lọc."
    )

    st.markdown("#### 01 · Danh mục tạo doanh thu có phải danh mục sinh lời tốt nhất?")
    cat = df.groupby("Product_Category", as_index=False).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum")
    )
    cat["Margin"] = cat["Profit"].div(cat["Revenue"].replace(0, np.nan)) * 100
    if not cat.empty:
        rev_leader = cat.loc[cat["Revenue"].idxmax()]
        margin_leader = cat.loc[cat["Margin"].idxmax()]
        if rev_leader["Product_Category"] == margin_leader["Product_Category"]:
            product_title = (
                f"{rev_leader['Product_Category']} dẫn đầu cả doanh thu và biên lợi nhuận"
            )
        else:
            product_title = (
                f"{rev_leader['Product_Category']} dẫn đầu doanh thu, nhưng "
                f"{margin_leader['Product_Category']} có biên lợi nhuận cao nhất"
            )
        analytical_insight(
            "INSIGHT 01 · PRODUCT PROFITABILITY",
            product_title,
            f"{rev_leader['Product_Category']} tạo {money_short(rev_leader['Revenue'])} doanh thu với biên {rev_leader['Margin']:.2f}%; {margin_leader['Product_Category']} đạt biên {margin_leader['Margin']:.2f}%.",
            "Grouped bar đặt doanh thu và lợi nhuận cạnh nhau để so sánh quy mô; biên lợi nhuận được tính riêng từ tổng lợi nhuận chia tổng doanh thu.",
            "Không phân bổ nguồn lực chỉ dựa trên doanh thu. Cần tìm nguyên nhân chênh lệch giá vốn và chiết khấu ở danh mục có biên thấp.",
            "Grouped bar phù hợp vì cần so sánh hai đại lượng tiền tệ trên cùng thang đo giữa các danh mục; đặt cột cạnh nhau giúp nhận ra doanh thu lớn nhưng lợi nhuận không tăng tương ứng.",
            "Doanh thu và lợi nhuận có quy mô chênh lệch nên lợi nhuận có thể khó đọc; biểu đồ này không trực tiếp biểu diễn biên lợi nhuận, vì vậy cần đối chiếu tỷ lệ biên đã tính riêng.",
        )
        plot = cat.sort_values("Revenue").copy()
        fig = go.Figure()
        fig.add_bar(y=plot["Product_Category"], x=plot["Revenue"] / 1e6, orientation="h", name="Doanh thu", marker_color=COLORS["blue"])
        fig.add_bar(y=plot["Product_Category"], x=plot["Profit"] / 1e6, orientation="h", name="Lợi nhuận", marker_color=COLORS["cyan"])
        fig.update_layout(barmode="group", xaxis_title="Giá trị (triệu ₫)", yaxis_title="Danh mục")
        chart_layout(fig, 330)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)

    st.divider()
    st.markdown("#### 02 · Cửa hàng nào có quy mô lớn nhưng hiệu quả sinh lời chưa tương xứng?")
    store = df.groupby("Store", as_index=False).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
        Transactions=("Transaction_ID", "nunique")
    )
    store["Margin"] = store["Profit"].div(store["Revenue"].replace(0, np.nan)) * 100
    if not store.empty:
        overall_margin = profit / revenue * 100 if revenue else 0
        low = store.loc[store["Margin"].idxmin()]
        high_rev = store.loc[store["Revenue"].idxmax()]
        store_title = (
            f"{high_rev['Store']} dẫn đầu doanh thu và {low['Store']} có biên lợi nhuận thấp nhất"
            if high_rev["Store"] != low["Store"]
            else f"{high_rev['Store']} vừa dẫn đầu doanh thu vừa có biên lợi nhuận thấp nhất"
        )
        analytical_insight(
            "INSIGHT 02 · STORE PERFORMANCE",
            store_title,
            f"{high_rev['Store']} đạt {money_short(high_rev['Revenue'])}; {low['Store']} có biên {low['Margin']:.2f}%, so với mức chung {overall_margin:.2f}%.",
            "Scatter plot mã hóa doanh thu trên trục X, biên lợi nhuận trên trục Y và quy mô giao dịch bằng kích thước điểm. Đường tham chiếu giúp nhận diện cửa hàng dưới mức chung.",
            f"Ưu tiên rà soát giá vốn, chiết khấu và cơ cấu sản phẩm tại {low['Store']}; đối chiếu với cửa hàng có biên cao trước khi đề xuất nhân rộng.",
            "Scatter plot phù hợp để xem đồng thời hai chỉ số số học của từng cửa hàng và phát hiện cửa hàng có quy mô lớn nhưng biên thấp; đường tham chiếu tạo mốc đánh giá trực quan.",
            "Số cửa hàng ít nên mỗi điểm dễ đọc, nhưng kết quả chỉ mô tả các cửa hàng trong bộ lọc và không giải thích nguyên nhân chênh lệch.",
        )
        fig = px.scatter(store, x="Revenue", y="Margin", size="Transactions", color="Store", text="Store",
                         color_discrete_sequence=PALETTE, size_max=38,
                         hover_data={"Profit": ":,.0f", "Transactions": True},
                         labels={"Revenue": "Doanh thu (₫)", "Margin": "Biên lợi nhuận (%)", "Store": "Cửa hàng"})
        fig.add_hline(y=overall_margin, line_dash="dash", line_color=COLORS["red"], annotation_text=f"Biên chung {overall_margin:.2f}%")
        fig.update_traces(textposition="top center")
        fig.update_xaxes(tickprefix="₫", tickformat="~s")
        fig.update_yaxes(ticksuffix="%")
        chart_layout(fig, 350)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("#### 03 · Doanh thu biến động do số giao dịch hay giá trị mỗi đơn?")
    monthly = df.groupby(["Month_Number", "Month_Name"], as_index=False).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
        Transactions=("Transaction_ID", "nunique")
    ).sort_values("Month_Number")
    if not monthly.empty:
        monthly["Average_Ticket"] = monthly["Revenue"] / monthly["Transactions"].replace(0, np.nan)
        peak = monthly.loc[monthly["Revenue"].idxmax()]
        analytical_insight(
            "INSIGHT 03 · SALES TREND",
            f"Tháng {peak['Month_Name']} có doanh thu cao nhất trong giai đoạn được chọn",
            f"Doanh thu đạt {money_short(peak['Revenue'])} từ {int(peak['Transactions'])} giao dịch; giá trị trung bình {money_short(peak['Average_Ticket'])}/giao dịch.",
            "Biểu đồ kết hợp cho thấy doanh thu và số giao dịch theo tháng; giá trị đơn trung bình được tính từ doanh thu chia số giao dịch.",
            "Tháng doanh thu cao nhất có thể đến từ nhiều giao dịch hoặc giá trị đơn cao; so sánh cả hai chỉ số giúp phân biệt hai động lực này.",
            "Cột doanh thu và đường số giao dịch trả lời đồng thời câu hỏi về quy mô bán hàng và số đơn; trục riêng giữ đúng đơn vị của từng đại lượng.",
            "Hai trục tung có thang đo khác nhau nên cần đọc nhãn trục, không so sánh độ cao trực tiếp. Dữ liệu một năm không đủ để khẳng định mùa vụ lặp lại.",
        )
        fig = go.Figure()
        fig.add_bar(
            x=monthly["Month_Name"], y=monthly["Revenue"] / 1e6,
            name="Doanh thu (triệu ₫)", marker_color=COLORS["blue"],
            hovertemplate="%{x}<br>Doanh thu: %{y:.2f} triệu ₫<extra></extra>",
        )
        fig.add_scatter(
            x=monthly["Month_Name"], y=monthly["Transactions"],
            name="Số giao dịch", mode="lines+markers", yaxis="y2",
            line=dict(color=COLORS["orange"], width=2.5),
            hovertemplate="%{x}<br>Số giao dịch: %{y}<extra></extra>",
        )
        fig.update_layout(
            xaxis_title="Tháng",
            yaxis=dict(title="Doanh thu (triệu ₫)", rangemode="tozero"),
            yaxis2=dict(
                title="Số giao dịch", overlaying="y", side="right",
                showgrid=False, rangemode="tozero",
            ),
        )
        chart_layout(fig, 330)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Đọc hai trục riêng: cột là doanh thu (triệu ₫), đường là số giao dịch. "
            "Giá trị đơn trung bình = doanh thu / số giao dịch."
        )

    st.divider()
    st.markdown("#### 04 · Chiết khấu có đi kèm sự suy giảm lợi nhuận không?")
    corr = correlation_text(df, "Discount", "Profit") if {"Discount", "Profit"}.issubset(df.columns) else None
    if corr:
        pearson_r, p_value, spearman_r, n = corr
        direction = "âm" if pearson_r < 0 else "dương" if pearson_r > 0 else "gần bằng 0"
        analytical_insight(
            "INSIGHT 04 · DISCOUNT EFFECTIVENESS",
            f"Mức chiết khấu có mối liên hệ {direction} với lợi nhuận giao dịch",
            f"Pearson r = {pearson_r:.3f}; Spearman ρ = {spearman_r:.3f}; p-value = {p_value:.3g}; N = {n}.",
            "Scatter plot cho thấy phân bố từng giao dịch; đường xu hướng mô tả chiều liên hệ tuyến tính, còn hệ số Spearman kiểm tra xu hướng đơn điệu.",
            "Đánh giá chương trình giảm giá theo lợi nhuận còn lại và từng danh mục. Tương quan không chứng minh chiết khấu là nguyên nhân duy nhất.",
            "Scatter plot phù hợp để khảo sát mối liên hệ giữa hai biến số ở cấp giao dịch; có thể nhìn thấy phân tán, ngoại lệ và hình dạng quan hệ mà giá trị tổng hợp che khuất.",
            "Đường xu hướng chỉ tóm tắt tuyến tính và có thể bị ảnh hưởng bởi ngoại lệ; tương quan không chứng minh quan hệ nhân quả, nên cần phân tích thêm theo danh mục.",
        )
        fig = px.scatter(df, x="Discount", y="Profit", color="Product_Category", color_discrete_sequence=PALETTE,
                         hover_data=[c for c in ["Transaction_ID", "Store", "Product"] if c in df.columns],
                         labels={"Discount": "Mức chiết khấu (%)", "Profit": "Lợi nhuận (₫)"})
        valid = df[["Discount", "Profit"]].dropna()
        if len(valid) >= 3 and valid["Discount"].nunique() > 1:
            slope, intercept = np.polyfit(valid["Discount"], valid["Profit"], 1)
            x_line = np.linspace(valid["Discount"].min(), valid["Discount"].max(), 40)
            fig.add_scatter(x=x_line, y=slope * x_line + intercept, mode="lines", name="Xu hướng tuyến tính", line=dict(color=COLORS["red"], dash="dash", width=2))
        fig.add_hline(y=0, line_dash="dot", line_color="#8B98AA", annotation_text="Lợi nhuận = 0")
        fig.update_xaxes(ticksuffix="%")
        fig.update_yaxes(tickprefix="₫", tickformat="~s")
        chart_layout(fig, 350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Không đủ dữ liệu biến thiên để kiểm tra mối liên hệ giữa chiết khấu và lợi nhuận.")

    st.divider()
    st.markdown("#### 05 · Tốc độ giao hàng có liên quan đến trải nghiệm khách hàng không?")
    valid_delivery = df.dropna(subset=["Delivery_Days", "Customer_Rating"])
    delivery_corr = correlation_text(valid_delivery, "Delivery_Days", "Customer_Rating") if not valid_delivery.empty else None
    if delivery_corr:
        pearson_r, p_value, spearman_r, n = delivery_corr
        direction = "âm" if pearson_r < 0 else "dương" if pearson_r > 0 else "gần bằng 0"
        strength = (
            "mạnh" if abs(spearman_r) >= .6
            else "trung bình" if abs(spearman_r) >= .3
            else "yếu"
        )
        by_days = valid_delivery.groupby("Delivery_Days", as_index=False).agg(
            Average_Rating=("Customer_Rating", "mean"), Transactions=("Transaction_ID", "nunique")
        )
        fastest = by_days.loc[by_days["Delivery_Days"].idxmin()]
        slowest = by_days.loc[by_days["Delivery_Days"].idxmax()]
        analytical_insight(
            "INSIGHT 05 · DELIVERY EXPERIENCE",
            f"Mối liên hệ giữa thời gian giao và đánh giá là {direction}, {strength}",
            f"Pearson r = {pearson_r:.3f}; Spearman ρ = {spearman_r:.3f}; p-value = {p_value:.3g}; N = {n}. "
            f"Điểm trung bình là {fastest['Average_Rating']:.2f}/5 ở nhóm giao nhanh nhất "
            f"({int(fastest['Delivery_Days'])} ngày) và {slowest['Average_Rating']:.2f}/5 "
            f"ở nhóm giao lâu nhất ({int(slowest['Delivery_Days'])} ngày).",
            "Scatter plot thể hiện từng giao dịch; đường xu hướng và hai hệ số tương quan giúp đánh giá chiều và độ mạnh của mối liên hệ.",
            "Ưu tiên rà soát các đơn giao lâu. Đây là mối liên hệ thống kê, không chứng minh giao hàng chậm là nguyên nhân duy nhất làm giảm đánh giá.",
            "Scatter plot phù hợp để xem đồng thời thời gian giao và đánh giá của từng đơn; đường xu hướng hỗ trợ nhận diện quan hệ tổng quát mà không che mất phân tán dữ liệu.",
            "Chỉ các đơn đủ cả hai trường được đưa vào; đường xu hướng tuyến tính không thể hiện mọi quan hệ phi tuyến và kết quả không chứng minh quan hệ nhân quả.",
        )
        fig = px.scatter(valid_delivery, x="Delivery_Days", y="Customer_Rating", color="Store", color_discrete_sequence=PALETTE,
                         hover_data=[c for c in ["Transaction_ID", "Product", "Customer_Type"] if c in valid_delivery.columns],
                         labels={"Delivery_Days": "Thời gian giao hàng (ngày)", "Customer_Rating": "Điểm đánh giá (1–5)"})
        slope, intercept = np.polyfit(valid_delivery["Delivery_Days"], valid_delivery["Customer_Rating"], 1)
        x_line = np.linspace(valid_delivery["Delivery_Days"].min(), valid_delivery["Delivery_Days"].max(), 30)
        fig.add_scatter(x=x_line, y=slope * x_line + intercept, mode="lines", name="Xu hướng tuyến tính", line=dict(color=COLORS["red"], dash="dash", width=2))
        fig.update_yaxes(range=[0, 5], dtick=1)
        chart_layout(fig, 350)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Có {n:,}/{len(df):,} giao dịch đủ dữ liệu cho phân tích. Tương quan không chứng minh quan hệ nhân quả.")
    else:
        st.info("Không đủ dữ liệu hợp lệ hoặc biến thiên để phân tích mối liên hệ giữa thời gian giao hàng và đánh giá.")

    st.caption("Phạm vi kết luận: mô tả tập giao dịch đang chọn, không đại diện mặc định cho toàn bộ thị trường bán lẻ TP.HCM. Dùng các trang phân tích chi tiết để kiểm tra sâu từng phát hiện.")
