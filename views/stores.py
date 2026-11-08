import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from config import COLORS, PALETTE
from utils import money_short, chart_layout, section_title, analytical_insight, empty_chart


def render(df):
    section_title("Hiệu suất cửa hàng", "Phân biệt quy mô doanh thu với hiệu quả sinh lời để xác định cửa hàng cần nhân rộng hoặc tối ưu.", "stores")
    store = df.groupby("Store", as_index=False).agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Cost=("Cost", "sum"), Transactions=("Transaction_ID", "nunique"), Quantity=("Quantity", "sum"))
    if store.empty:
        st.plotly_chart(empty_chart(), use_container_width=True)
        return
    store["Margin"] = store["Profit"].div(store["Revenue"].replace(0, float("nan"))) * 100
    overall_margin = store["Profit"].sum() / store["Revenue"].sum() * 100 if store["Revenue"].sum() else 0
    leader_rev = store.loc[store["Revenue"].idxmax()]
    leader_margin = store.loc[store["Margin"].idxmax()]
    low_margin = store.loc[store["Margin"].idxmin()]
    analytical_insight(
        "INSIGHT 05 · STORE PERFORMANCE",
        f"{leader_rev['Store']} dẫn đầu doanh thu; {leader_margin['Store']} có biên lợi nhuận cao nhất",
        f"{leader_rev['Store']} tạo {money_short(leader_rev['Revenue'])} doanh thu. {low_margin['Store']} có biên thấp nhất ({low_margin['Margin']:.2f}%), so với {leader_margin['Store']} ({leader_margin['Margin']:.2f}%).",
        f"Biên lợi nhuận chung là {overall_margin:.2f}%; biểu đồ ma trận đặt từng cửa hàng cạnh hai mốc doanh thu trung vị và biên lợi nhuận chung.",
        f"Rà soát giá vốn, chiết khấu và cơ cấu sản phẩm tại {low_margin['Store']}; đối chiếu với cửa hàng có biên cao nhưng cần kiểm tra khác biệt về cơ cấu giao dịch.",
        "Scatter plot phù hợp để phân tích đồng thời quy mô doanh thu và biên lợi nhuận theo cửa hàng; kích thước điểm bổ sung quy mô giao dịch, còn hai đường tham chiếu chia vùng hiệu suất.",
        "Một điểm đại diện cho một cửa hàng nên không cho thấy biến động nội bộ; chênh lệch không chứng minh nguyên nhân và các cửa hàng có cơ cấu giao dịch khác nhau.",
    )
    section_title("Ma trận quy mô và hiệu quả sinh lời", "Mỗi điểm là một cửa hàng; trục X là doanh thu, trục Y là biên lợi nhuận.", "stores")
    fig = px.scatter(store, x="Revenue", y="Margin", size="Transactions", color="Store", text="Store", color_discrete_sequence=PALETTE,
                     hover_data={"Profit": ":,.0f", "Transactions": True, "Cost": ":,.0f", "Margin": ":.2f"},
                     labels={"Revenue": "Doanh thu (₫)", "Margin": "Biên lợi nhuận (%)", "Store": "Cửa hàng"}, size_max=38)
    fig.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="white")))
    fig.add_hline(y=overall_margin, line_dash="dash", line_color=COLORS["red"], annotation_text=f"Biên chung {overall_margin:.2f}%")
    fig.add_vline(x=store["Revenue"].median(), line_dash="dot", line_color="#94A3B8", annotation_text="Doanh thu trung vị")
    chart_layout(fig, 430)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Góc trên bên phải: doanh thu và biên lợi nhuận đều cao. Góc dưới bên phải: doanh thu lớn nhưng hiệu quả sinh lời dưới mức tham chiếu.")

    a, b = st.columns(2)
    with a:
        section_title("Doanh thu và lợi nhuận", "Grouped bar dùng chung đơn vị triệu đồng.", "revenue")
        plot = store.sort_values("Revenue")
        fig = go.Figure()
        fig.add_bar(y=plot["Store"], x=plot["Revenue"] / 1e6, name="Doanh thu", orientation="h", marker_color=COLORS["blue"])
        fig.add_bar(y=plot["Store"], x=plot["Profit"] / 1e6, name="Lợi nhuận", orientation="h", marker_color=COLORS["cyan"])
        fig.update_layout(barmode="group", xaxis_title="Giá trị (triệu ₫)", yaxis_title="Cửa hàng")
        chart_layout(fig, 340)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        section_title("Biên lợi nhuận so với mức chung", "Xác định cửa hàng cao hoặc thấp hơn biên lợi nhuận tổng hợp.", "margin")
        plot = store.sort_values("Margin")
        fig = go.Figure(go.Bar(x=plot["Margin"], y=plot["Store"], orientation="h",
                               marker_color=[COLORS["green"] if v >= overall_margin else COLORS["orange"] for v in plot["Margin"]],
                               text=plot["Margin"].map(lambda v: f"{v:.2f}%"), textposition="outside", cliponaxis=False))
        fig.add_vline(x=overall_margin, line_dash="dash", line_color=COLORS["red"])
        fig.update_layout(xaxis_title="Biên lợi nhuận (%)", yaxis_title="Cửa hàng")
        fig.update_xaxes(ticksuffix="%")
        chart_layout(fig, 340, False)
        st.plotly_chart(fig, use_container_width=True)

    display = store.sort_values("Profit", ascending=False).copy()
    display["Doanh thu"] = display["Revenue"].map(money_short)
    display["Lợi nhuận"] = display["Profit"].map(money_short)
    display["Biên lợi nhuận"] = display["Margin"].map(lambda v: f"{v:.2f}%")
    st.dataframe(display[["Store", "Doanh thu", "Lợi nhuận", "Biên lợi nhuận", "Transactions", "Quantity"]].rename(
        columns={"Store": "Cửa hàng", "Transactions": "Số giao dịch", "Quantity": "Sản phẩm bán"}), use_container_width=True, hide_index=True)
