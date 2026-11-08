import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS, PALETTE
from utils import money_short, chart_layout, section_title, empty_chart, analytical_insight, correlation_text


def render(df):
    section_title(
        "Doanh thu & Sản phẩm",
        "Xác định danh mục tạo doanh thu, danh mục sinh lời và mối liên hệ giữa giảm giá với lợi nhuận.",
        "sales",
    )

    cat = df.groupby("Product_Category", as_index=False).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"),
        Transactions=("Transaction_ID", "nunique"),
    )
    cat["Margin"] = cat["Profit"].div(cat["Revenue"].replace(0, float("nan"))) * 100

    if not cat.empty:
        top_rev = cat.loc[cat["Revenue"].idxmax()]
        top_margin = cat.loc[cat["Margin"].idxmax()]
        low_margin = cat.loc[cat["Margin"].idxmin()]
        analytical_insight(
            "INSIGHT 02 · PRODUCT PROFITABILITY",
            f"{top_rev['Product_Category']} dẫn đầu doanh thu nhưng {top_margin['Product_Category']} có biên lợi nhuận cao nhất",
            f"{top_rev['Product_Category']} tạo {money_short(top_rev['Revenue'])} doanh thu và biên lợi nhuận "
            f"{top_rev['Margin']:.2f}%; {top_margin['Product_Category']} đạt biên {top_margin['Margin']:.2f}%.",
            f"Khoảng cách biên lợi nhuận giữa danh mục cao nhất và thấp nhất là "
            f"{top_margin['Margin'] - low_margin['Margin']:.2f} điểm phần trăm.",
            f"Không nên phân bổ ngân sách chỉ theo doanh thu. Cần rà soát giá vốn, mức giảm giá và khả năng cải thiện "
            f"biên lợi nhuận của {low_margin['Product_Category']}.",
            "Grouped bar so sánh doanh thu và lợi nhuận giữa các danh mục trên cùng đơn vị; biểu đồ thanh ngang cũng giúp đọc tên danh mục rõ ràng.",
            "Lợi nhuận thường nhỏ hơn doanh thu nên có thể khó so sánh bằng mắt; grouped bar không thay thế biểu đồ biên lợi nhuận và không nên hiểu doanh thu cao là hiệu quả cao.",
        )

        section_title("Doanh thu và lợi nhuận theo danh mục", "Grouped bar dùng chung đơn vị triệu đồng để so sánh quy mô và phần lợi nhuận giữ lại.", "category")
        plot = cat.sort_values("Revenue", ascending=True).copy()
        plot["Revenue_M"] = plot["Revenue"] / 1e6
        plot["Profit_M"] = plot["Profit"] / 1e6
        fig = go.Figure()
        fig.add_bar(y=plot["Product_Category"], x=plot["Revenue_M"], name="Doanh thu",
                    orientation="h", marker_color=COLORS["blue"],
                    hovertemplate="%{y}<br>Doanh thu: %{x:.2f} triệu ₫<extra></extra>")
        fig.add_bar(y=plot["Product_Category"], x=plot["Profit_M"], name="Lợi nhuận",
                    orientation="h", marker_color=COLORS["cyan"],
                    hovertemplate="%{y}<br>Lợi nhuận: %{x:.2f} triệu ₫<extra></extra>")
        fig.update_layout(barmode="group", xaxis_title="Giá trị (triệu ₫)", yaxis_title="Danh mục")
        chart_layout(fig, 390)
        st.plotly_chart(fig, use_container_width=True)

        section_title("Biên lợi nhuận theo danh mục", "Biên lợi nhuận = tổng lợi nhuận / tổng doanh thu; không lấy trung bình margin từng giao dịch.", "margin")
        margin_plot = cat.sort_values("Margin", ascending=True)
        fig = px.bar(
            margin_plot, x="Margin", y="Product_Category", orientation="h",
            color="Margin", color_continuous_scale="RdYlGn",
            text=margin_plot["Margin"].map(lambda v: f"{v:.2f}%"),
            labels={"Margin": "Biên lợi nhuận (%)", "Product_Category": "Danh mục"},
            hover_data={"Revenue": ":,.0f", "Profit": ":,.0f"},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(ticksuffix="%", rangemode="tozero")
        chart_layout(fig, 300, False)
        st.plotly_chart(fig, use_container_width=True)

        display = cat.sort_values("Revenue", ascending=False).copy()
        display["Doanh thu"] = display["Revenue"].map(money_short)
        display["Lợi nhuận"] = display["Profit"].map(money_short)
        display["Biên lợi nhuận"] = display["Margin"].map(lambda x: f"{x:.2f}%")
        st.dataframe(display[["Product_Category", "Doanh thu", "Lợi nhuận", "Biên lợi nhuận", "Quantity", "Transactions"]].rename(
            columns={"Product_Category": "Danh mục", "Quantity": "Số sản phẩm", "Transactions": "Số giao dịch"}
        ), use_container_width=True, hide_index=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)

    st.divider()
    monthly = (
        df.groupby(["Month_Number", "Month_Name"], as_index=False)
        .agg(Revenue=("Revenue", "sum"), Transactions=("Transaction_ID", "nunique"))
        .sort_values("Month_Number")
    )
    if not monthly.empty:
        monthly["Average_Ticket"] = monthly["Revenue"] / monthly["Transactions"].replace(0, np.nan)
        peak = monthly.loc[monthly["Revenue"].idxmax()]
        analytical_insight(
            "INSIGHT 03 · MONTHLY SALES DRIVER",
            f"Tháng {peak['Month_Name']} đạt doanh thu cao nhất; cần tách tác động số đơn và giá trị đơn",
            f"Tháng {peak['Month_Name']} ghi nhận {money_short(peak['Revenue'])} từ {int(peak['Transactions'])} giao dịch, "
            f"giá trị trung bình {money_short(peak['Average_Ticket'])}/giao dịch.",
            "Biểu đồ kết hợp doanh thu và số giao dịch cho biết quy mô tăng do tần suất mua hay giá trị giỏ hàng.",
            "Nếu doanh thu tăng chủ yếu nhờ số đơn, ưu tiên chuyển đổi và giữ chân; nếu nhờ giá trị đơn, xem xét bán kèm và nâng cấp giỏ hàng.",
            "Cột thể hiện quy mô doanh thu, đường thể hiện biến động số giao dịch theo trục thời gian; hai trục riêng giữ đúng đơn vị của mỗi đại lượng và hỗ trợ so sánh nhịp thay đổi.",
            "Hai trục tung có thang đo khác nhau nên hình dạng đường không thể so sánh trực tiếp về độ lớn; cần đọc nhãn trục và tooltip. Dữ liệu một năm không xác nhận mùa vụ.",
        )
    section_title("Doanh thu và số giao dịch theo tháng", "Hai trục riêng vì khác đơn vị; hover để đối chiếu giá trị từng tháng.", "trend")
    if monthly.empty:
        fig = empty_chart()
    else:
        fig = go.Figure()
        fig.add_bar(x=monthly["Month_Name"], y=monthly["Revenue"] / 1e6,
                    name="Doanh thu (triệu ₫)", marker_color=COLORS["blue"],
                    hovertemplate="%{x}<br>Doanh thu: %{y:.2f} triệu ₫<extra></extra>")
        fig.add_scatter(x=monthly["Month_Name"], y=monthly["Transactions"],
                        name="Số giao dịch", mode="lines+markers+text",
                        text=monthly["Transactions"].astype(str), textposition="top center",
                        yaxis="y2", line=dict(color=COLORS["orange"], width=2.5))
        fig.update_layout(
            yaxis=dict(title="Doanh thu (triệu ₫)", rangemode="tozero"),
            yaxis2=dict(title="Số giao dịch", overlaying="y", side="right", showgrid=False, rangemode="tozero"),
        )
        chart_layout(fig, 370)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    if len(df) >= 3 and df["Discount"].nunique() > 1:
        corr = correlation_text(df, "Discount", "Profit")
        if corr:
            pearson_r, p_value, spearman_r, n = corr
            direction = "âm" if pearson_r < 0 else "dương" if pearson_r > 0 else "gần bằng 0"
            strength = "mạnh" if abs(spearman_r) >= .6 else "trung bình" if abs(spearman_r) >= .3 else "yếu"
            analytical_insight(
                "INSIGHT 04 · DISCOUNT & PROFIT",
                f"Mức giảm giá có mối liên hệ {direction}, {strength} với lợi nhuận giao dịch",
                f"Pearson r = {pearson_r:.3f}; Spearman ρ = {spearman_r:.3f}; p-value = {p_value:.3g}; N = {n}.",
                "Scatter plot thể hiện phân bố lợi nhuận theo mức giảm giá; đường xu hướng chỉ tóm tắt chiều liên hệ tuyến tính.",
                "Kiểm tra chính sách giảm giá theo từng danh mục và mức giá. Không diễn giải tương quan thành quan hệ nhân quả.",
                "Scatter plot phù hợp để đánh giá quan hệ giữa mức giảm giá và lợi nhuận từng giao dịch; màu theo danh mục giúp kiểm tra liệu các nhóm có phân bố khác nhau.",
                "Các điểm có thể chồng lấp và đường xu hướng chỉ mô tả tuyến tính; lợi nhuận còn chịu ảnh hưởng của giá vốn, sản phẩm và quy mô đơn hàng.",
            )
        section_title("Mức giảm giá và lợi nhuận từng giao dịch", "Discount được đo bằng phần trăm (%), đường ngang tại 0 là ngưỡng lãi/lỗ.", "discount")
        fig = px.scatter(
            df, x="Discount", y="Profit", color="Product_Category",
            color_discrete_sequence=PALETTE, hover_data=["Transaction_ID", "Store", "Product"],
            labels={"Discount": "Mức giảm giá (%)", "Profit": "Lợi nhuận (₫)"},
        )
        valid = df[["Discount", "Profit"]].dropna()
        if len(valid) >= 3 and valid["Discount"].nunique() > 1:
            slope, intercept = np.polyfit(valid["Discount"], valid["Profit"], 1)
            x_line = np.linspace(valid["Discount"].min(), valid["Discount"].max(), 40)
            fig.add_scatter(x=x_line, y=slope * x_line + intercept, mode="lines",
                            name="Xu hướng tuyến tính", line=dict(color="#E65B67", dash="dash", width=2))
        fig.add_hline(y=0, line_dash="dot", line_color="#9AA6B7", annotation_text="Lãi/lỗ = 0")
        fig.update_yaxes(tickprefix="₫", tickformat="~s")
        fig.update_xaxes(ticksuffix="%")
        chart_layout(fig, 390)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Không đủ biến thiên dữ liệu để phân tích mối liên hệ giữa giảm giá và lợi nhuận.")
