"""Trang tổng quan: sáu phát hiện kinh doanh có đối chiếu và điều tra dữ liệu."""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS, PALETTE
from utils import money_short, chart_layout, section_title, empty_chart, analytical_insight, correlation_text


def render(df):
    section_title(
        "Tổng quan · 6 phát hiện kinh doanh chính",
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
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
        Cost=("Cost", "sum"), Transactions=("Transaction_ID", "nunique"),
        Average_Discount=("Discount", "mean"),
    )
    cat["Margin"] = cat["Profit"].div(cat["Revenue"].replace(0, np.nan)) * 100
    if not cat.empty:
        rev_leader = cat.loc[cat["Revenue"].idxmax()]
        margin_leader = cat.loc[cat["Margin"].idxmax()]
        low_margin_category = cat.loc[cat["Margin"].idxmin()]
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
            "PHÁT HIỆN 01 · DANH MỤC & SINH LỜI",
            product_title,
            f"{rev_leader['Product_Category']} tạo {money_short(rev_leader['Revenue'])} doanh thu; "
            f"biên {rev_leader['Margin']:.2f}%, so với {margin_leader['Margin']:.2f}% của "
            f"{margin_leader['Product_Category']} và {low_margin_category['Margin']:.2f}% "
            f"của nhóm thấp nhất ({low_margin_category['Product_Category']}).",
            f"Khoảng cách giữa danh mục doanh thu cao nhất và biên cao nhất là "
            f"{margin_leader['Margin'] - rev_leader['Margin']:.2f} điểm phần trăm; "
            f"biên của danh mục thấp nhất thấp hơn {margin_leader['Margin'] - low_margin_category['Margin']:.2f} điểm "
            "so với danh mục dẫn đầu biên.",
            "Không phân bổ nguồn lực chỉ dựa trên doanh thu. Cần tìm nguyên nhân chênh lệch giá vốn và chiết khấu ở danh mục có biên thấp.",
            "Grouped bar so sánh doanh thu và lợi nhuận trên cùng thang đo; bar xếp hạng riêng cho biên phần trăm, tránh trộn tỷ lệ với giá trị tiền.",
            "Doanh thu và lợi nhuận có quy mô chênh lệch nên lợi nhuận có thể khó đọc; biểu đồ biên đi kèm cho biết tỷ lệ tổng hợp, không thể hiện biến động của từng giao dịch.",
            (
                f"Biên của {rev_leader['Product_Category']} thấp hơn {margin_leader['Product_Category']} "
                f"{margin_leader['Margin'] - rev_leader['Margin']:.2f} điểm phần trăm. "
                f"Giá vốn chiếm {rev_leader['Cost'] / rev_leader['Revenue'] * 100:.1f}% doanh thu "
                f"ở danh mục dẫn đầu doanh thu, so với "
                f"{margin_leader['Cost'] / margin_leader['Revenue'] * 100:.1f}% ở danh mục có biên cao nhất; "
                f"mức giảm giá trung bình lần lượt là {rev_leader['Average_Discount']:.1f}% "
                f"và {margin_leader['Average_Discount']:.1f}%. "
                f"{low_margin_category['Product_Category']} là nhóm cần rà soát thêm vì có biên thấp nhất "
                f"({low_margin_category['Margin']:.2f}%)."
            ),
        )
        plot = cat.sort_values("Revenue").copy()
        revenue_col, margin_col = st.columns(2)
        with revenue_col:
            fig = go.Figure()
            fig.add_bar(y=plot["Product_Category"], x=plot["Revenue"] / 1e6, orientation="h", name="Doanh thu", marker_color=COLORS["blue"])
            fig.add_bar(y=plot["Product_Category"], x=plot["Profit"] / 1e6, orientation="h", name="Lợi nhuận", marker_color=COLORS["cyan"])
            fig.update_layout(barmode="group", xaxis_title="Giá trị (triệu ₫)", yaxis_title="Danh mục")
            chart_layout(fig, 330)
            st.plotly_chart(fig, use_container_width=True)
        with margin_col:
            margin_plot = cat.sort_values("Margin")
            fig = go.Figure(go.Bar(
                x=margin_plot["Margin"], y=margin_plot["Product_Category"],
                orientation="h", marker_color=COLORS["purple"],
                text=margin_plot["Margin"].map(lambda value: f"{value:.2f}%"),
                textposition="outside", cliponaxis=False,
            ))
            fig.update_layout(xaxis_title="Biên lợi nhuận (%)", yaxis_title="Danh mục")
            fig.update_xaxes(ticksuffix="%")
            chart_layout(fig, 330, False)
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
        high_margin = store.loc[store["Margin"].idxmax()]
        store_category = df.groupby(
            ["Store", "Product_Category"], as_index=False
        ).agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
        low_mix = store_category[store_category["Store"] == low["Store"]]
        dominant_category = low_mix.loc[low_mix["Revenue"].idxmax()]
        reference_category = store_category[
            (store_category["Store"] == high_margin["Store"])
            & (store_category["Product_Category"] == dominant_category["Product_Category"])
        ]
        low_category_share = dominant_category["Revenue"] / low["Revenue"] * 100
        if not reference_category.empty and high_margin["Store"] != low["Store"]:
            reference = reference_category.iloc[0]
            reference_share = reference["Revenue"] / high_margin["Revenue"] * 100
            category_margin = (
                reference["Profit"] / reference["Revenue"] * 100
                if reference["Revenue"] else 0
            )
            store_investigation = (
                f"Tại {low['Store']}, {dominant_category['Product_Category']} là danh mục "
                f"đóng góp doanh thu lớn nhất, chiếm {low_category_share:.1f}% doanh thu cửa hàng. "
                f"Cùng danh mục này chiếm {reference_share:.1f}% tại {high_margin['Store']}; "
                f"biên của danh mục ở cửa hàng tham chiếu là {category_margin:.2f}%. "
                "Cơ cấu danh mục là một hướng giải thích cần kiểm tra, chưa đủ để kết luận nguyên nhân "
                "vì giá vốn và mức giảm giá theo từng giao dịch có thể khác nhau."
            )
        else:
            store_investigation = (
                f"{dominant_category['Product_Category']} đóng góp lớn nhất vào doanh thu "
                f"của {low['Store']} ({low_category_share:.1f}%). "
                "Cần đối chiếu cơ cấu sản phẩm và giá vốn theo giao dịch để xác định nguyên nhân "
                "chênh lệch biên; so sánh này chưa chứng minh quan hệ nhân quả."
            )
        store_title = (
            f"{high_rev['Store']} dẫn đầu doanh thu; {low['Store']} có biên thấp nhất"
            f" so với {high_margin['Store']} cao nhất"
        )
        analytical_insight(
            "PHÁT HIỆN 02 · QUY MÔ & HIỆU QUẢ CỬA HÀNG",
            store_title,
            f"{high_rev['Store']} đạt doanh thu cao nhất {money_short(high_rev['Revenue'])}. "
            f"Biên thấp nhất là {low['Margin']:.2f}% tại {low['Store']}, trong khi "
            f"{high_margin['Store']} đạt {high_margin['Margin']:.2f}%; mức chung là {overall_margin:.2f}%.",
            f"Doanh thu cao nhất là {money_short(high_rev['Revenue'])} tại {high_rev['Store']}; "
            f"biên cửa hàng thấp nhất ({low['Margin']:.2f}%, {low['Store']}) thấp hơn "
            f"cửa hàng cao nhất ({high_margin['Margin']:.2f}%, {high_margin['Store']}) "
            f"{high_margin['Margin'] - low['Margin']:.2f} điểm phần trăm và thấp hơn mức chung "
            f"{overall_margin:.2f}%.",
            f"Ưu tiên rà soát giá vốn, chiết khấu và cơ cấu sản phẩm tại {low['Store']}; đối chiếu với cửa hàng có biên cao trước khi đề xuất nhân rộng.",
            "Scatter plot phù hợp để xem đồng thời doanh thu và biên lợi nhuận của từng cửa hàng; đường tham chiếu chỉ rõ cửa hàng nằm trên hay dưới mức chung.",
            "Số cửa hàng ít nên mỗi điểm dễ đọc, nhưng kết quả chỉ mô tả các cửa hàng trong bộ lọc và không giải thích nguyên nhân chênh lệch.",
            store_investigation,
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
        trough = monthly.loc[monthly["Revenue"].idxmin()]
        peak_to_trough = (
            peak["Revenue"] / trough["Revenue"] if trough["Revenue"] else float("nan")
        )
        analytical_insight(
            "PHÁT HIỆN 03 · XU HƯỚNG DOANH THU",
            f"Doanh thu cao nhất thuộc tháng {peak['Month_Name']}; thấp nhất thuộc tháng {trough['Month_Name']}",
            f"Doanh thu đạt {money_short(peak['Revenue'])} từ {int(peak['Transactions'])} giao dịch; giá trị trung bình {money_short(peak['Average_Ticket'])}/giao dịch.",
            "Biểu đồ kết hợp cho thấy doanh thu và số giao dịch theo tháng; giá trị đơn trung bình được tính từ doanh thu chia số giao dịch.",
            "Tháng doanh thu cao nhất có thể đến từ nhiều giao dịch hoặc giá trị đơn cao; so sánh cả hai chỉ số giúp phân biệt hai động lực này.",
            "Cột doanh thu và đường số giao dịch trả lời đồng thời câu hỏi về quy mô bán hàng và số đơn; trục riêng giữ đúng đơn vị của từng đại lượng.",
            "Hai trục tung có thang đo khác nhau nên cần đọc nhãn trục, không so sánh độ cao trực tiếp. Dữ liệu một năm không đủ để khẳng định mùa vụ lặp lại.",
            (
                f"Doanh thu tháng {peak['Month_Name']} cao gấp {peak_to_trough:.2f} lần tháng "
                f"{trough['Month_Name']} ({money_short(trough['Revenue'])}). "
                f"Số đơn lần lượt là {int(peak['Transactions'])} và {int(trough['Transactions'])}; "
                f"giá trị đơn trung bình là {money_short(peak['Average_Ticket'])} so với "
                f"{money_short(trough['Average_Ticket'])}. Đối chiếu này giúp phân biệt tăng trưởng "
                "do nhiều đơn hay do giá trị mỗi đơn."
            ),
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
        discount_data = df.dropna(subset=["Discount", "Revenue", "Profit"]).copy()
        discount_data["Discount_Band"] = np.select(
            [
                discount_data["Discount"] <= 10,
                discount_data["Discount"] <= 20,
            ],
            ["Thấp (≤10%)", "Trung bình (>10–20%)"],
            default="Cao (>20%)",
        )
        discount_bands = discount_data.groupby("Discount_Band", as_index=False).agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Transactions=("Transaction_ID", "nunique"),
            Average_Discount=("Discount", "mean"),
        )
        discount_bands["Margin"] = (
            discount_bands["Profit"]
            .div(discount_bands["Revenue"].replace(0, np.nan)) * 100
        )
        if len(discount_bands) > 1:
            low_discount = discount_bands.loc[discount_bands["Average_Discount"].idxmin()]
            high_discount = discount_bands.loc[discount_bands["Average_Discount"].idxmax()]
            category_mix = discount_data.groupby(
                ["Discount_Band", "Product_Category"], as_index=False
            )["Revenue"].sum()
            low_mix = category_mix[
                category_mix["Discount_Band"] == low_discount["Discount_Band"]
            ]
            high_mix = category_mix[
                category_mix["Discount_Band"] == high_discount["Discount_Band"]
            ]
            low_top = low_mix.loc[low_mix["Revenue"].idxmax()]
            high_top = high_mix.loc[high_mix["Revenue"].idxmax()]
            discount_comparison = (
                f"Pearson r = {pearson_r:.3f}; Spearman ρ = {spearman_r:.3f}; "
                f"p-value = {p_value:.3g}; N = {n}. Biên của nhóm giảm thấp là "
                f"{low_discount['Margin']:.2f}% ({int(low_discount['Transactions'])} giao dịch), "
                f"so với {high_discount['Margin']:.2f}% ở nhóm giảm cao "
                f"({int(high_discount['Transactions'])} giao dịch)."
            )
            discount_investigation = (
                f"Theo ngưỡng ≤10%, >10–20% và >20%, mức giảm trung bình là "
                f"{low_discount['Average_Discount']:.1f}% ở nhóm thấp và "
                f"{high_discount['Average_Discount']:.1f}% ở nhóm cao. Danh mục đóng góp "
                f"doanh thu lớn nhất cũng khác nhau: {low_top['Product_Category']} ở nhóm thấp và "
                f"{high_top['Product_Category']} ở nhóm giảm cao. Cần tách tác động "
                "mức giảm giá khỏi khác biệt cơ cấu sản phẩm trước khi đánh giá chương trình."
            )
        else:
            discount_comparison = (
                f"Pearson r = {pearson_r:.3f}; Spearman ρ = {spearman_r:.3f}; "
                f"p-value = {p_value:.3g}; N = {n}."
            )
            discount_investigation = (
                "Bộ lọc hiện tại chỉ còn một nhóm mức giảm giá; chưa đủ nhóm để so sánh "
                "biên lợi nhuận giữa các mức."
            )
        analytical_insight(
            "PHÁT HIỆN 04 · CHIẾT KHẤU & LỢI NHUẬN",
            f"Mức chiết khấu có mối liên hệ {direction} với lợi nhuận giao dịch",
            f"Mức chiết khấu và lợi nhuận có tương quan {direction}.",
            discount_comparison,
            "Đánh giá chương trình giảm giá theo lợi nhuận còn lại và từng danh mục. Tương quan không chứng minh chiết khấu là nguyên nhân duy nhất.",
            "Scatter plot phù hợp để khảo sát mối liên hệ giữa hai biến số ở cấp giao dịch; có thể nhìn thấy phân tán, ngoại lệ và hình dạng quan hệ mà giá trị tổng hợp che khuất.",
            "Đường xu hướng chỉ tóm tắt tuyến tính và có thể bị ảnh hưởng bởi ngoại lệ; tương quan không chứng minh quan hệ nhân quả, nên cần phân tích thêm theo danh mục.",
            discount_investigation,
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
    st.markdown("#### 05 · Bán nhiều sản phẩm hơn có đi kèm doanh thu cao hơn không?")
    quantity_corr = (
        correlation_text(df, "Quantity", "Revenue")
        if {"Quantity", "Revenue"}.issubset(df.columns) else None
    )
    if quantity_corr:
        quantity_r, quantity_p, quantity_spearman, quantity_n = quantity_corr
        quantity_by = df.groupby("Quantity", as_index=False).agg(
            Average_Revenue=("Revenue", "mean"),
            Average_Discount=("Discount", "mean"),
            Average_Unit_Price=("Unit_Price", "mean"),
            Transactions=("Transaction_ID", "nunique"),
        ).sort_values("Quantity")
        lowest_quantity = quantity_by.iloc[0]
        highest_quantity = quantity_by.iloc[-1]
        quantity_direction = (
            "dương" if quantity_r > 0 else "âm" if quantity_r < 0 else "gần bằng 0"
        )
        quantity_strength = (
            "mạnh" if abs(quantity_spearman) >= .6
            else "trung bình" if abs(quantity_spearman) >= .3
            else "yếu"
        )
        analytical_insight(
            "PHÁT HIỆN 05 · SỐ LƯỢNG & DOANH THU",
            f"Số lượng sản phẩm và doanh thu có mối liên hệ {quantity_direction}, {quantity_strength}",
            f"Pearson r = {quantity_r:.3f}; Spearman ρ = {quantity_spearman:.3f}; "
            f"p-value = {quantity_p:.3g}; N = {quantity_n}.",
            f"Đơn có số lượng thấp nhất ({int(lowest_quantity['Quantity'])}) đạt doanh thu trung bình "
            f"{money_short(lowest_quantity['Average_Revenue'])} (N={int(lowest_quantity['Transactions'])}); "
            f"nhóm số lượng cao nhất ({int(highest_quantity['Quantity'])}) đạt "
            f"{money_short(highest_quantity['Average_Revenue'])} "
            f"(N={int(highest_quantity['Transactions'])}).",
            "Có thể cân nhắc bán kèm để tăng giá trị giỏ hàng, nhưng nên theo dõi doanh thu và lợi nhuận trên mỗi đơn thay vì chỉ tăng số món.",
            "Scatter plot phù hợp để xem quan hệ giữa số lượng và doanh thu ở từng giao dịch; mỗi điểm giữ được thông tin đơn lẻ và giúp nhận ra ngoại lệ.",
            "Giá đơn vị, danh mục và chiết khấu cũng ảnh hưởng doanh thu; tương quan không chứng minh tăng số lượng tự nó làm doanh thu tăng.",
            (
                f"Giá bán đơn vị trung bình thay đổi từ "
                f"{money_short(lowest_quantity['Average_Unit_Price'])} ở nhóm số lượng thấp "
                f"xuống {money_short(highest_quantity['Average_Unit_Price'])} ở nhóm số lượng cao; "
                f"mức giảm giá trung bình tương ứng là {lowest_quantity['Average_Discount']:.1f}% "
                f"và {highest_quantity['Average_Discount']:.1f}%. Giá và chiết khấu có thể giải thích "
                "một phần khác biệt doanh thu, vì vậy không nên diễn giải tương quan thành tác động nhân quả."
            ),
        )
        fig = px.scatter(
            df, x="Quantity", y="Revenue", color="Product_Category",
            color_discrete_sequence=PALETTE,
            hover_data=["Transaction_ID", "Unit_Price", "Discount", "Profit"],
            labels={
                "Quantity": "Số lượng sản phẩm",
                "Revenue": "Doanh thu (₫)",
                "Product_Category": "Danh mục",
            },
        )
        fig.update_yaxes(tickprefix="₫", tickformat="~s")
        chart_layout(fig, 350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Không đủ dữ liệu biến thiên để kiểm tra mối liên hệ giữa số lượng và doanh thu.")

    st.divider()
    st.markdown("#### 06 · Tốc độ giao hàng có liên quan đến trải nghiệm khách hàng không?")
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
            "PHÁT HIỆN 06 · GIAO HÀNG & TRẢI NGHIỆM",
            f"Mối liên hệ giữa thời gian giao và đánh giá là {direction}, {strength}",
            f"Pearson r = {pearson_r:.3f}; Spearman ρ = {spearman_r:.3f}; p-value = {p_value:.3g}; N = {n}. "
            f"Điểm trung bình là {fastest['Average_Rating']:.2f}/5 ở nhóm giao nhanh nhất "
            f"({int(fastest['Delivery_Days'])} ngày) và {slowest['Average_Rating']:.2f}/5 "
            f"ở nhóm giao lâu nhất ({int(slowest['Delivery_Days'])} ngày).",
            "Scatter plot thể hiện từng giao dịch; đường xu hướng và hai hệ số tương quan giúp đánh giá chiều và độ mạnh của mối liên hệ.",
            "Ưu tiên rà soát các đơn giao lâu. Đây là mối liên hệ thống kê, không chứng minh giao hàng chậm là nguyên nhân duy nhất làm giảm đánh giá.",
            "Scatter plot phù hợp để xem đồng thời thời gian giao và đánh giá của từng đơn; đường xu hướng hỗ trợ nhận diện quan hệ tổng quát mà không che mất phân tán dữ liệu.",
            "Chỉ các đơn đủ cả hai trường được đưa vào; đường xu hướng tuyến tính không thể hiện mọi quan hệ phi tuyến và kết quả không chứng minh quan hệ nhân quả.",
            (
                f"Điểm đánh giá trung bình chênh {fastest['Average_Rating'] - slowest['Average_Rating']:.2f} "
                f"điểm giữa nhóm giao {int(fastest['Delivery_Days'])} ngày "
                f"(N={int(fastest['Transactions'])}) và nhóm giao "
                f"{int(slowest['Delivery_Days'])} ngày (N={int(slowest['Transactions'])}). "
                "Đối chiếu này kiểm tra liệu chênh lệch hai đầu có phù hợp với xu hướng tương quan trên toàn bộ đơn hợp lệ."
            ),
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

    st.divider()
    section_title(
        "Kết luận & hướng hành động",
        "Tổng hợp các hướng ưu tiên từ những so sánh trong tập dữ liệu hiện tại.",
        "overview",
    )
    conclusion = [
        (
            f"Rà soát cơ cấu danh mục tại {low['Store']} và giá vốn của "
            f"{low_margin_category['Product_Category']}, vì đây là cửa hàng/danh mục có "
            "biên thấp nhất trong dữ liệu đang lọc."
        ),
        (
            "Đánh giá chương trình giảm giá theo biên lợi nhuận sau giảm và so sánh trong "
            "cùng danh mục; chênh lệch tổng thể chưa tách được ảnh hưởng cơ cấu sản phẩm."
        ),
        (
            "Theo dõi đồng thời số giao dịch, giá trị đơn trung bình và lợi nhuận; không dùng "
            "doanh thu đơn lẻ làm thước đo hiệu quả."
        ),
    ]
    if delivery_corr:
        if pearson_r < 0:
            conclusion.append(
                "Ưu tiên kiểm tra các đơn giao lâu vì dữ liệu hiện tại cho thấy thời gian giao "
                "và điểm đánh giá có liên hệ âm; cần kiểm soát thêm cửa hàng và loại sản phẩm."
            )
        else:
            conclusion.append(
                "Không kết luận giao hàng chậm làm giảm đánh giá trong tập này; theo dõi mối "
                "liên hệ cùng các yếu tố khác như cửa hàng và loại sản phẩm."
            )
    for action in conclusion:
        st.markdown(f"- {action}")
    st.caption(
        "Kết luận chỉ mô tả dữ liệu giao dịch đang chọn. Các so sánh gợi ý hướng điều tra, "
        "không chứng minh nguyên nhân; cần kiểm tra thêm theo sản phẩm, giá vốn, chiết khấu "
        "và cửa hàng trước khi ra quyết định."
    )
