import streamlit as st
import pandas as pd

from utils import section_title, money_short


def render(df, df_all):
    section_title(
        "Dữ liệu & Báo cáo",
        "Kiểm tra chất lượng dữ liệu, xem tập dữ liệu sau lọc và xuất CSV phục vụ phân tích tiếp.",
        "reports",
    )

    st.subheader("Chất lượng dữ liệu gốc")
    quality = pd.DataFrame({
        "Cột": df_all.columns,
        "Kiểu dữ liệu": [str(t) for t in df_all.dtypes],
        "Giá trị thiếu": [int(df_all[c].isna().sum()) for c in df_all.columns],
        "Tỷ lệ thiếu (%)": [round(df_all[c].isna().mean() * 100, 2) for c in df_all.columns],
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)

    st.subheader("Tóm tắt tập dữ liệu đang lọc")
    revenue = df["Revenue"].sum()
    profit = df["Profit"].sum()
    margin = profit / revenue * 100 if revenue else 0
    a, b, c = st.columns(3)
    a.metric("Số giao dịch", f"{df['Transaction_ID'].nunique():,}")
    b.metric("Doanh thu", money_short(revenue))
    c.metric("Biên lợi nhuận", f"{margin:.2f}%")

    st.subheader("Dữ liệu sau khi áp dụng bộ lọc")
    st.caption(f"{len(df):,} dòng · {df.shape[1]} cột")
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Tải dữ liệu đang lọc (CSV)",
        data=csv_bytes,
        file_name="urban_retail_filtered_data.csv",
        mime="text/csv",
    )

    with st.expander("Phương pháp và lưu ý"):
        st.write("- Biên lợi nhuận = tổng lợi nhuận / tổng doanh thu × 100%.")
        st.write("- Các biểu đồ doanh thu/lợi nhuận dùng cùng đơn vị khi đặt cạnh nhau.")
        st.write("- Tương quan mô tả mối liên hệ, không chứng minh quan hệ nhân quả.")
        st.write("- Isolation Forest dùng Quantity, Unit_Price, Discount, Revenue, Cost và Profit.")
        st.write("- Mô hình bất thường được huấn luyện trên dataset gốc trước khi áp dụng bộ lọc.")
